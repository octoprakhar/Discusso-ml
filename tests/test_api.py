import os
import numpy as np
import pandas as pd


from fastapi.testclient import TestClient
from app.main import app

from app.services.quality_estimator import compute_post_score
from app.api.routes import process_tagging
from app.models.schemas import TagRequest, PostInput
from app.services.quality_estimator import update_post_score
from app.services.tag_writer import update_post_tags, update_post_tag_error
from app.services.tagger import generate_tags

from ml.features.post_quality_feature.effort_features import (
    num_paragraphs, has_multi_paragraphs, sentence_count, avg_sentence_length,
    num_tokens, question_count, has_first_person, has_attempt_marker,
    has_constraint_marker, has_contextual_grounding, has_temporal_progression,
    informational_question, personal_problem_question, curiosity_feature,
    opinion_with_experience, opinion_with_experience_long,
    narrative_vent_feature, self_reflection_feature, generate_effort_features
)

from ml.utils.post_quality_feature.utils import create_combined_text,create_embeddings

## Creating a client: It is for me a fake browser, where I will test
client = TestClient(app)
TEST_SECRET = os.getenv("ML_INTERNAL_SECRET")

## Integration Testing
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status":"ok"}


## Testing whether my tag generation hit the background task or not
## Good scenario
def test_tag_endpoint_success(mocker):
    mock_db = mocker.patch("app.api.routes.process_tagging")

    ## Fake request
    payload = {
        "post_id": "123-abc",
        "title": "Learning PyTest",
        "description":"This is a test description"
    }

    ## Need to include fake secret
    response = client.post(
        "/tag", 
        json=payload,
        headers={"x-internal-secret": TEST_SECRET} 
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}

    ## Was the background logic triggered?
    mock_db.assert_called_once()

## Security scenario
def test_tag_endpoint_unauthorized():
    """Verify that a wrong secret results in a 403"""
    payload = {"post_id":"123", "title":"Test","description":"Test"}

    response = client.post(
        "/tag",
        json=payload,
        headers={"x-internal-secret": "I_AM_A_HACKER"}
    )

    assert response.status_code == 403

## Missing Scenario
def test_tag_endpoint_missing_data():
    """Verify that missing required fields return 422 Uprocessable Entity"""
    incomplete_payload = {
        "title":"Missing ID",
        "description": "This should fail"
    }

    response = client.post(
        "/tag",
        json=incomplete_payload,
        headers={"x-internal-secret": TEST_SECRET}

    )

    assert response.status_code == 422


## Unit testing of process tagging function
def test_process_tagging_logic_success(mocker):
    ### Making mocker for generate tag, coz it is heavy function, it is using sentence embedding
    mock_gen = mocker.patch("app.api.routes.generate_tags")
    mock_update_tags = mocker.patch("app.api.routes.update_post_tags")

    mock_gen.return_value = {"tags":["ai","python"],"error":None}

    payload = TagRequest(post_id="123", title="Test", description="Test")

    process_tagging(payload)

    mock_gen.assert_called_once()
    mock_update_tags.assert_called_once_with("123",["ai","python"])

def test_process_tagging_logic_crash(mocker):
    mocker.patch("app.api.routes.PostInput", side_effect = Exception("Hard Drive Failure"))
    mock_error_db = mocker.patch("app.api.routes.update_post_tag_error")

    process_tagging(TagRequest(post_id="123", title="T", description="D"))

    mock_error_db.assert_called_once_with("123","internal_error")






#### POST QUALITY ENDPOINT ####


## Component test
def test_compute_post_score_logic():
    ## Testing positive karma
    score = compute_post_score(post_quality=2.0,karma=100) ## tanh(100) is almost 1.0
    assert score > 2.0 and score <= 3.0

    ## Testing zero karma
    score_zero = compute_post_score(post_quality=2.0,karma=0)
    assert score_zero == 2.0

    ## Testing negative karma(tanh(-100) is almost -1)
    score_neg = compute_post_score(post_quality=2.0,karma=-100)
    assert score_neg < 2.0 

def test_post_quality_unauthorized():
    """Verify that wrong secret blocks access to post-quality."""
    payload = {"postId": "123", "title": "Test", "body": "Test", "karma": 0}
    
    response = client.post(
        "/post-quality",
        json=payload,
        headers={"x-internal-secret": "WRONG_SECRET"}
    )
    # Check if your code returns 403 (or 401)
    assert response.status_code == 403


## Testing the api
def test_post_quality_endpoint_success(mocker):

    mock_inference = mocker.patch("ml.pipelines.post_quality_feature.inference_pipeline.InferencePipeline.predict")
    mock_inference.return_value = {
        "effort": 1,
        "openness": 1,
        "score": 3
    }

    mock_db_update = mocker.patch("app.api.routes.update_post_score")

    payload = {
        "postId": "post-132",
        "title":"Testing post-quality",
        "body": "This is a test body",
        "karma": 50
    }

    response = client.post(
        "/post-quality",
        json=payload,
        headers={"x-internal-secret": TEST_SECRET}
    )

    assert response.status_code == 200

    assert response.json()["result"]["score"] == 3

    mock_db_update.assert_called_once()

    _, kwargs = mock_db_update.call_args
    assert kwargs["post_id"] == "post-132"
    assert kwargs["post_quality"] == 3


def test_post_quality_inference_failure(mocker):
    """Verify that if the ML pipeline crashes, the API returns a 500 error."""
    mock_inference = mocker.patch("ml.pipelines.post_quality_feature.inference_pipeline.InferencePipeline.predict")
    mock_inference.side_effect = Exception("Model file not found")

    payload = {
        "postId": "post-132",
        "title":"Crash Test",
        "body": "This should trigger an error",
        "karma": 10
    }

    response = client.post(
        "/post-quality",
        json=payload,
        headers={"x-internal-secret": TEST_SECRET}
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Post quality failed"

def test_post_quality_missing_id():
    """Verify that missing postId returns 422."""
    payload = {"title": "Missing ID", "body": "Body", "karma": 10} # No postId
    
    response = client.post(
        "/post-quality",
        json=payload,
        headers={"x-internal-secret": TEST_SECRET}
    )
    assert response.status_code == 422

## Checking whether all file is present or not 
def test_ml_artifacts_exist():
    artifacts = [
        "ml/artifacts/post_quality_feature/transformation/effort/tfidf.pkl",
        "ml/artifacts/post_quality_feature/transformation/effort/scaler.pkl",
        "ml/artifacts/post_quality_feature/model/effort_model.pkl",
        "ml/artifacts/post_quality_feature/model/openness_model.pkl"
    ]
    for path in artifacts:
        assert os.path.exists(path), f"Critical ML artifact missing: {path}"


## Updating post score in DB
def test_update_post_score_success(mocker):
    mock_supabase = mocker.patch("app.services.quality_estimator.supabase")
    update_post_score("123",3.0,100)

    # 3. ASSERT: Did the function try to talk to the table "Post"?
    mock_supabase.table.assert_called_with("Post")
    # Did it try to run an update?
    mock_supabase.table().update.assert_called_once()


def test_update_post_score_failure(mocker):
    # We tell the 'table' method to explode when called
    mock_supabase = mocker.patch("app.services.quality_estimator.supabase")
    mock_supabase.table.side_effect = Exception("Database is Down")

    # This will now trigger the 'except' block in your service!
    update_post_score("123", 3.0, 100)

    # If your code reaches the 'logger.error' line, coverage increases!
    mock_supabase.table.assert_called_once()



## Testing Tag Writer Success
def test_update_post_tags_success(mocker):
    # 1. Patch the supabase object in the tag_writer module
    mock_supabase = mocker.patch("app.services.tag_writer.supabase")
    
    # 2. Call the function
    update_post_tags("post-123", ["python", "fastapi"])

    # 3. Assertions
    # Did it join the tags with a comma?
    mock_supabase.table.assert_called_with("Post")
    
    # Get the arguments passed to .update()
    args, _ = mock_supabase.table().update.call_args
    assert args[0]["tag"] == "python,fastapi"
    assert args[0]["tag_error"] is None

## Testing Tag Writer Error logic
def test_update_post_tag_error_success(mocker):
    # 1. Patch
    mock_supabase = mocker.patch("app.services.tag_writer.supabase")
    
    # 2. Call
    update_post_tag_error("post-123", "ML_MODEL_TIMEOUT")

    # 3. Assert
    args, _ = mock_supabase.table().update.call_args
    assert args[0]["tag"] is None
    assert args[0]["tag_error"] == "ML_MODEL_TIMEOUT"



def test_generate_tags_short_text():
    # This hits the 'if len(text.split()) < 4' branch
    post = PostInput(title="Hi", description="Bye")
    result = generate_tags(post)
    
    assert result["error"] == "text_too_short"
    assert result["tags"] == []

def test_generate_tags_logic_flow(mocker):
    # 1. Patch the .encode method of the model already sitting in tagger
    mock_encode = mocker.patch("app.services.tagger.model.encode")
    
    
    mock_encode.return_value = np.random.rand(384) # 384 is MiniLM dimension

    # 2. We also need to mock cosine_similarity 
    # so we can CONTROL which tags pass the threshold
    mock_sim = mocker.patch("app.services.tagger.cosine_similarity")
    # Return 1.0 for the first tag, 0.0 for others
    fake_similarities = np.zeros((1, 58)) # Assuming 58 tags in vocab
    fake_similarities[0][0] = 0.9 # Make the first tag very confident
    mock_sim.return_value = fake_similarities

    # 3. ACT
    post = PostInput(title="Large Language Models", description="Deep learning and AI")
    result = generate_tags(post, top_k=1)

    # 4. ASSERT
    assert result["error"] is None
    assert len(result["tags"]) > 0
    mock_encode.assert_called_once()


## Effort feature testing(regex can't capture each thing, so they may fail)
import pytest
import pandas as pd
import numpy as np
from ml.features.post_quality_feature.effort_features import (
    num_paragraphs, has_multi_paragraphs, sentence_count, avg_sentence_length,
    num_tokens, question_count, has_first_person, has_attempt_marker,
    has_constraint_marker, has_contextual_grounding, has_temporal_progression,
    informational_question, personal_problem_question, curiosity_feature,
    opinion_with_experience, opinion_with_experience_long,
    narrative_vent_feature, self_reflection_feature, generate_effort_features
)

# --- 1. Structural Features ---

@pytest.mark.parametrize("text, expected", [
    ("Paragraph 1\n\nParagraph 2", 2),
    ("Line 1\nLine 2", 2),
    ("   ", 0),
    (None, 0),
    ("Only one paragraph.", 1)
])
def test_num_paragraphs(text, expected):
    assert num_paragraphs(text) == expected

def test_has_multi_paragraphs():
    assert has_multi_paragraphs("Para 1\n\nPara 2") == 1
    assert has_multi_paragraphs("Just one") == 0

@pytest.mark.parametrize("text, expected", [
    ("Hello world. This is a test!", 2),
    ("What? No way... Yes.", 3),
    ("", 0),
    (123, 0) # Testing non-string handling
])
def test_sentence_count(text, expected):
    assert sentence_count(text) == expected

def test_avg_sentence_length():
    assert avg_sentence_length("Hello world. Hello.") == 1.5 # (2 words + 1 word) / 2
    assert avg_sentence_length("") == 0

# --- 2. Behavioral Features ---

@pytest.mark.parametrize("text, expected", [
    ("I am here", 1),
    ("This is my car", 1),
    ("He is there", 0),
    ("I've been working", 1)
])
def test_has_first_person(text, expected):
    assert has_first_person(text) == expected

@pytest.mark.parametrize("text, expected", [
    ("I tried everything", 1),
    ("It doesn't work", 1),
    ("Success at last", 0)
])
def test_has_attempt_marker(text, expected):
    assert has_attempt_marker(text) == expected

# --- 3. Question Type Features ---

@pytest.mark.parametrize("text, expected", [
    ("Why is the sky blue?", True),    # Question word, no first person
    ("I wonder why I am sad", False),  # Has first person (I)
    ("Just a statement", False)
])
def test_informational_question(text, expected):
    assert informational_question(text) == expected

@pytest.mark.parametrize("text, expected", [
    ("I am struggling with this", True),
    ("How do I fix this?", False), # Missing first person in some regex contexts or logic
    ("I need help", True)
])
def test_personal_problem_question(text, expected):
    assert personal_problem_question(text) == expected

def test_curiosity_feature():
    # Needs (curiosity or question) AND subject AND question_mark in title
    assert curiosity_feature("Why do humans dream?", "Dreams?") is True
    assert curiosity_feature("I like cake", "Cake") is False

# --- 4. Narrative/Reflection ---

def test_self_reflection_feature():
    # First person + cognitive verb - help request
    assert self_reflection_feature("I think this is true") is True
    assert self_reflection_feature("I think I need help") is True

def test_opinion_with_experience_long():
    long_text = "I think this is great. Sentence two. Sentence three. Sentence four. Sentence five."
    assert opinion_with_experience_long(long_text) is False
    assert opinion_with_experience_long("I think it's short.") is False

# --- 5. DataFrame Wrapper ---

def test_generate_effort_features():
    df = pd.DataFrame([
        {"title": "Test Title?", "body": "Why do humans code? I think it is fun."}
    ])
    result = generate_effort_features(df)
    
    assert "num_tokens" in result.columns
    assert "has_curiosity_question" in result.columns
    assert result["num_paragraphs"].iloc[0] == 1


## Testing utilities


def test_create_combined_text_logic():
    # 1. Prepare a DataFrame with different scenarios
    data = [
        {"title": "My Title", "body": "My Body"},      # Both
        {"title": "Only Title", "body": None},         # Title only
        {"title": None, "body": "Only Body"},         # Body only
        {"title": "  Space  ", "body": "  Trim  "}    # Needs stripping
    ]
    df = pd.DataFrame(data)

    # 2. ACT
    result_df = create_combined_text(df)

    # 3. ASSERT
    assert result_df["combined_text"].iloc[0] == "Title: My Title\n\nBody: My Body"
    assert result_df["combined_text"].iloc[1] == "Title: Only Title"
    assert result_df["combined_text"].iloc[2] == "Only Body"
    assert result_df["combined_text"].iloc[3] == "Title: Space\n\nBody: Trim"


def test_create_embeddings_mocked(mocker):
    # 1. Mock the SentenceTransformer CLASS
    # Note: Patch it where it is IMPORTED in utils file
    mock_model_class = mocker.patch("ml.utils.post_quality_feature.utils.SentenceTransformer")
    
    # 2. Setup the "Instance" that the class returns
    mock_instance = mock_model_class.return_value
    
    # 3. Setup what the .encode() method returns (a fake numpy array)
    fake_embeddings = np.array([[0.1, 0.2], [0.3, 0.4]])
    mock_instance.encode.return_value = fake_embeddings

    # 4. ACT
    sample_texts = ["Hello world", "Machine learning"]
    result = create_embeddings("fake-model-name", sample_texts)

    # 5. ASSERT
    # Check if the model was initialized with the right name
    mock_model_class.assert_called_once_with("fake-model-name")
    
    # Check if encode was called with correct parameters
    mock_instance.encode.assert_called_once_with(
        sample_texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    
    # Ensure the result is our fake array
    np.testing.assert_array_equal(result, fake_embeddings)

## To see coverage : pytest --cov=app --cov=ml tests/
## To get lines of not covered: pytest --cov=app.api.routes --cov-report=term-missing tests/