import re
import pandas as pd


## 1. Structural features
def num_paragraphs(text:str) -> int:
    if not isinstance(text,str) or text.strip() == "":
        return 0
    return len([p for p in text.split("\n") if p.strip()])

def has_multi_paragraphs(text: str) -> int:
    return int(num_paragraphs(text) >= 2)

def sentence_count(text: str) -> int:
    if not isinstance(text, str):
        return 0

    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return len(sentences)

def avg_sentence_length(text: str) -> float:
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return 0

    word_counts = [len(s.split()) for s in sentences]
    return sum(word_counts) / len(sentences)

def num_tokens(text: str) -> int:
    if not isinstance(text, str):
        return 0
    return len(text.split())

def question_count(text: str) -> int:
    if not isinstance(text, str):
        return 0
    return text.count("?")


## 2. Behavioral Features

FIRST_PERSON_PATTERN = re.compile(
    r"\b(i|me|my|mine|i'm|i am|i've)\b",
    re.IGNORECASE
)

def has_first_person(text: str) -> int:
    if not isinstance(text, str):
        return 0
    return int(bool(FIRST_PERSON_PATTERN.search(text)))

ATTEMPT_MARKERS = [
    "tried", "attempted", "failed",
    "didn't work", "doesn't work",
    "already tried", "so far"
]

def has_attempt_marker(text: str) -> int:
    if not isinstance(text, str):
        return 0

    text = text.lower()
    return int(any(marker in text for marker in ATTEMPT_MARKERS))

CONSTRAINT_PATTERN = re.compile(
    r"\b(but|however|because|although|though|except|unless|while)\b",
    re.IGNORECASE
)

def has_constraint_marker(text: str) -> int:
    if not isinstance(text, str):
        return 0

    return int(bool(CONSTRAINT_PATTERN.search(text)))

CONTEXT_MARKERS = [
    "because", "due to", "as a result", "currently",
    "right now", "i am", "i'm", "i work", "i live",
    "based in", "looking for", "trying to",
    "in my role", "in my situation"
]

def has_contextual_grounding(text: str) -> int:
    if not isinstance(text, str):
        return 0

    text = text.lower()
    return int(any(marker in text for marker in CONTEXT_MARKERS))

TEMPORAL_MARKERS = [
    "first", "then", "later", "eventually", "initially",
    "at first", "used to", "but now", "now i",
    "before", "after", "have been", "i've been",
    "so far", "for a while"
]

def has_temporal_progression(text: str) -> int:
    if not isinstance(text, str):
        return 0

    text = text.lower()
    return int(any(marker in text for marker in TEMPORAL_MARKERS))


## 3. Question Type Features
QUESTION_WORD_PATTERN = re.compile(
    r"\b(why|how|what|when|where|which)\b",
    re.IGNORECASE
)

FIRST_PERSON_PATTERN_INFO = re.compile(
    r"\b(i|me|my|mine|i'm|i am|i've)\b",
    re.IGNORECASE
)

def informational_question(text):

    if not isinstance(text, str):
        return False

    has_question_word = bool(QUESTION_WORD_PATTERN.search(text))
    has_first_person = bool(FIRST_PERSON_PATTERN_INFO.search(text))

    return has_question_word and not has_first_person


FIRST_PERSON_PATTERN_PERS_PROB = re.compile(
    r"\b(i|me|my|mine|i'm|i am|i've)\b",
    re.IGNORECASE
)


PROBLEM_PATTERN = re.compile(
    r"\b(struggling|can't|cannot|unable|problem|issue|trouble|difficulty|stuck)\b",
    re.IGNORECASE
)

HELP_PATTERN = re.compile(
    r"\b(help|any advice|any suggestions|what should i do|can anyone help)\b",
    re.IGNORECASE
)

def personal_problem_question(text):

    if not isinstance(text, str):
        return False

    has_first_person = bool(FIRST_PERSON_PATTERN_PERS_PROB.search(text))
    has_problem = bool(PROBLEM_PATTERN.search(text))
    has_help = bool(HELP_PATTERN.search(text))

    return has_first_person and (has_problem or has_help)


QUESTION_START = re.compile(
r"\b(why|what|how|are|is|do|does|would|could|should|can)\b",
re.I
)
CURIOSITY_PHRASE = re.compile(r"\b(why\s+do|why\s+does|why\s+are|why\s+is|what\s+makes|how\s+do|how\s+does|is\s+there|are\s+there)\b", re.I)

GENERAL_SUBJECT = re.compile(r"\b(people|humans|society|culture|animals|technology|psychology|behavior|history)\b", re.I)

def curiosity_feature(text, title):

    question = bool(QUESTION_START.search(text))
    curiosity = bool(CURIOSITY_PHRASE.search(text))
    subject = bool(GENERAL_SUBJECT.search(text))
    question_mark = "?" in title

    return (curiosity or question) and subject and question_mark




## 4. Narrative/Reflection
FIRST_PERSON_PATTERN_OP = re.compile(
    r"\b(i|me|my|mine|i'm|i am|i've)\b",
    re.IGNORECASE
)

OPINION_PATTERN = re.compile(
    r"\b(what do you think|do you think|am i wrong|am i crazy|does anyone else|has anyone else|is it just me|what are your thoughts|how do you feel about|would you say|anyone else)\b",
    re.IGNORECASE
)

def opinion_with_experience(text):

    if not isinstance(text, str):
        return False

    has_first_person = bool(FIRST_PERSON_PATTERN_OP.search(text))
    has_opinion_phrase = bool(OPINION_PATTERN.search(text))

    return has_first_person and has_opinion_phrase


def opinion_with_experience_long(text):

    if not isinstance(text, str):
        return False

    has_first_person = bool(FIRST_PERSON_PATTERN.search(text))
    has_opinion_phrase = bool(OPINION_PATTERN.search(text))

    sc = sentence_count(text)

    return has_first_person and has_opinion_phrase and sc >= 5



FIRST_PERSON_RENT_VENT = re.compile(r"\b(i|me|my|mine|myself|we|our|ours|ourselves)\b", re.I)

TEMPORAL_ANCHOR = re.compile(
r"\b(yesterday|last\s+(night|week|month|year|summer|winter)|a\s+long\s+time\s+ago|back\s+then|at\s+that\s+time|when\s+i\s+was|when\s+i\s+used\s+to|growing\s+up|in\s+(college|school|high\s+school))\b",
re.I
)

PAST_ACTION = re.compile(
r"\b(was|were|had|did|went|made|took|gave|said|told|felt|thought|tried|started|stopped|worked|lived|met|lost|found)\b",
re.I
)

HELP_REQUEST = re.compile(
r"\b(what\s+should\s+i|any\s+advice|how\s+do\s+i|can\s+someone\s+help|what\s+can\s+i\s+do|should\s+i)\b",
re.I
)

def narrative_vent_feature(text):

    first = bool(FIRST_PERSON_RENT_VENT.search(text))
    temporal = bool(TEMPORAL_ANCHOR.search(text))
    past = bool(PAST_ACTION.search(text))
    help_req = bool(HELP_REQUEST.search(text))

    return first and (temporal or past) and not help_req


COGNITIVE_VERB = re.compile(
r"\b(think|thought|feel|felt|realize|realized|wonder|guess|believe|noticed|understand)\b",
re.I
)
def self_reflection_feature(text):

    first = bool(FIRST_PERSON_RENT_VENT.search(text))
    cognitive = bool(COGNITIVE_VERB.search(text))
    help_req = bool(HELP_REQUEST.search(text))

    return first and cognitive and not help_req



## Making Of Feature Registry
EFFORT_FEATURES = {
    "num_paragraphs": num_paragraphs,
    "has_multi_paragraphs": has_multi_paragraphs,
    "sentence_count": sentence_count,
    "avg_sentence_length": avg_sentence_length,
    "num_tokens": num_tokens,
    "question_count": question_count,

    "has_first_person": has_first_person,
    "has_attempt_marker": has_attempt_marker,
    "has_constraint_marker": has_constraint_marker,
    "has_contextual_grounding": has_contextual_grounding,
    "has_temporal_progression": has_temporal_progression,

    "has_informational_question": informational_question,
    "has_personal_problem_question": personal_problem_question,
    "has_curiosity_question": curiosity_feature,


    "has_opinion_experience": opinion_with_experience,
    "has_opinion_experience_long":opinion_with_experience_long,
    "has_rant_vent_storytelling": narrative_vent_feature,
    "has_self_reflection": self_reflection_feature
}


## Final Feature extraction function
def generate_effort_features(df: pd.DataFrame) -> pd.DataFrame:

    df = df.copy()

    df["text"] = df["title"].fillna("") + " " + df["body"].fillna("")

    for feature_name, feature_fn in EFFORT_FEATURES.items():
        if feature_name == 'has_curiosity_question':
            df[feature_name] = df.apply(
                lambda row: feature_fn(row["text"], row["title"]),
                axis=1
            )
        else:
            df[feature_name] = df["text"].apply(feature_fn)

    return df