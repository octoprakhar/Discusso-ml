# Tagger Evaluation Summary

## Overview

This document summarizes the evaluation of a semantic tag generation system built using **SentenceTransformers (all-MiniLM-L6-v2)** with cosine similarity, category-specific confidence thresholds, and abstention logic.

The goal of the system is to automatically assign meaningful tags (e.g., domain, context, intent, tone) to user-generated posts while **avoiding incorrect or low-confidence predictions**.

A total of **14 diverse posts** were manually evaluated to understand model behavior, strengths, and failure modes.

---

## Evaluation Setup

* **Model**: all-MiniLM-L6-v2 (SentenceTransformers)
* **Method**: Semantic similarity between post text and predefined tag vocabulary
* **Thresholding**:

  * Category-specific confidence thresholds
  * Confidence gap constraint to prevent ambiguous predictions
* **Output policy**:

  * Return top tags only if confidence criteria are satisfied
  * Abstain (return empty list) otherwise

---

## Key Observations

### 1. Conservative but Safe Behavior

The system frequently abstained even when predicted tags were semantically reasonable. This is an intentional design choice that prioritizes **precision over recall** and avoids misleading tags.

Examples:

* Posts with multiple equally valid tags triggered confidence-gap abstention
* Ambiguous emotional or reflective content was often withheld

This behavior is desirable for production systems where incorrect tags are worse than missing tags.

---

### 2. Positivity Bias in Predictions

The model showed a recurring tendency to map reflective or emotionally complex posts to:

* `motivation`
* `self-improvement`
* `personal-growth`

Even when the post theme was:

* burnout
* failure
* pressure
* emotional exhaustion

**Root cause**:
SentenceTransformers capture *semantic similarity*, not emotional polarity or stance. Positive reframing language (“learned”, “growth”, “changed my view”) often dominates embeddings.

---

### 3. Vocabulary Coverage is the Primary Bottleneck

Most incorrect or weak predictions were not model failures, but **vocabulary gaps**.

Missing or underrepresented concepts included:

* Burnout, exhaustion, stress
* Adulting, modern life pressure
* Minimalism, intentional living
* Dating fatigue, digital detox
* Emotional processing without resolution

When vocabulary lacked precise anchors, the model drifted toward adjacent but imperfect tags.

---

### 4. Emotional and Mental Health Signals Are Underweighted

Posts dealing with:

* loneliness
* guilt
* anxiety
* pressure

were often classified under broader contextual tags (e.g., work-life-balance, lifestyle) rather than explicit mental-health concepts.

This highlights the need for **emotion-centric and mental-state tags**, not model retraining.

---

## What Worked Well

* Strong detection of **contextual themes** (remote work, finance, productivity)
* Reliable abstention on ambiguous or overlapping cases
* Category-specific thresholds reduced noisy cross-category matches
* Confidence-gap logic prevented overconfident multi-tag output

---

## What Did Not Work Well

* Emotional polarity (negative vs positive framing)
* Distinguishing critique from motivation
* Posts describing struggle without explicit outcome
* Lifestyle philosophy topics with limited vocabulary support

---

## Design Decisions Justified by Evaluation

* **No model fine-tuning** at this stage
* **Vocabulary expansion prioritized over threshold lowering**
* **Abstention retained** as a first-class outcome
* **Manual evaluation CSV maintained** as a learning artifact

---

## Final Assessment

This evaluation confirms that the tagging system:

* Is **semantically strong but intentionally conservative**
* Handles ambiguity responsibly
* Demonstrates production-aware ML design principles
* Requires vocabulary iteration rather than architectural changes

The system is suitable to be integrated into the application backend, with future improvements driven by logged abstentions and real user data.

---

## Next Steps

1. Expand vocabulary with emotional, lifestyle, and modern-life tags
2. Integrate tagging output into database storage
3. Log abstained cases for iterative improvement
4. Re-evaluate after vocabulary updates

---

*This evaluation document is intended as both a development artifact and a portfolio-ready demonstration of applied ML system thinking.*
