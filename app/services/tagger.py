from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
import numpy as np
from pathlib import Path
from app.models.schemas import PostInput
from app.utils.logger import logger

# 1. Let's load our model outside the API to call it only once
model = SentenceTransformer("all-MiniLM-L6-v2")

## 2. Now we'll load the already made vocabulary
TAGS_PATH = Path(__file__).resolve().parent.parent /"data" / "tag_vocabulary.json"

with open(TAGS_PATH, "r", encoding="utf-8") as f:
    TAG_OBJECTs = json.load(f)

    ## Extracting tag texts for embedding from json object
    TAG_TEXTS = [tag_obj["tag"] for tag_obj in TAG_OBJECTs]

    ## 3. Now let's compute the tag embedding before entering function 'coz it won't change in each request
    TAG_EMBEDDINGS = model.encode(
        TAG_TEXTS,
        normalize_embeddings=True
    )

#
# Confidence thresholds
#
CATEGORY_THRESHOLDS = {
    "intent": 0.28,
    "content_type": 0.30,
    "context": 0.30,
    "tone": 0.32,
    "difficulty": 0.32,
    "domain": 0.35,
    "technology": 0.35,
    "genre": 0.40,
    "meta": 0.34,
    "platform": 0.34,
    "maturity": 0.40,
    "length": 0.33,
}
MIN_CONFIDENCE_GAP = 0.05
TOP_K = 3

## Making the function that is been used by the api
def generate_tags(post: PostInput, top_k: int = TOP_K):

    logger.info("Running ML Trigger")

    # 1. Combine title + description
    text = post.title.strip()
    if post.description:
        text += f". {post.description.strip()}"

    # Short text guard 
    if len(text.split()) < 4:
        logger.warning("Text too short for reliable tagging")
        return {
            "tags":[],
            "error": "text_too_short"
        }

    # 2. Now do the post encoding
    post_embedding = model.encode(
        text, 
        normalize_embeddings=True
    )

    # 3. Compare cosine similarity between post encoding and tag embedding
    similarities = cosine_similarity(
        [post_embedding],
        TAG_EMBEDDINGS
    )[0]

    # 4. Selecting the top 3 tags
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    top_scores = similarities[top_indices]

    selected_tags = []

    # Logging
    for rank, idx in enumerate(top_indices):
        tag_obj = TAG_OBJECTs[idx]
        tag = tag_obj["tag"]
        category = tag_obj["category"]
        score = similarities[idx]

        threshold = CATEGORY_THRESHOLDS.get(category, 0.35)

        logger.info(
            f"{tag} ({category}) -> {score:.3f} | threshold={threshold}"
        )

        if score >= threshold:
            selected_tags.append(tag_obj)
    
    if not selected_tags:
        logger.warning("No tags passed category-specific thresholds")
        return {
            "tags": [],
            "error": "no_tag_crossed_threshold"
        }

    # Gap based abstention
    if len(selected_tags) >= 2:
        scores = [similarities[TAG_OBJECTs.index(tag)] for tag in selected_tags]
        if scores[0] - scores[1] < MIN_CONFIDENCE_GAP:
            logger.warning("Confidence gap too small")
            return {
                "tags": [],
                "error": "confidence_gap_too_small"
            }

        
    
    return {
        "tags": [tag_obj["tag"] for tag_obj in selected_tags],
        "error": None
    }


