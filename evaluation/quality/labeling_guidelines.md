# Binary Labeling Guidelines for Post Quality Modeling

**Version**: v2.0  
**Author**: Prakhar Pathak  
**Last Updated**: 2025-12-27

## Objective

Instead of predicting a single post-quality score, posts are evaluated along two independent binary dimensions:

- **Author Effort (E)**
- **Discussion Openness (O)**

This separation removes shortcut learning and aligns the model with how humans actually judge discussion quality.

## Axis 1 — Author Effort (E)

### Definition

Author Effort measures how much cognitive, contextual, or emotional work the author has performed before asking others to engage.  
This axis does not measure correctness, writing skill, length, or emotional intensity.

### Labels

#### E = 0 → Low Effort
The post demonstrates minimal upfront work by the author.  
The burden of making the discussion meaningful is pushed entirely onto commenters.

**Common Indicators**  
- Very short or vague prompt  
- No context, framing, or constraints  
- Rhetorical or shower-thought style  
- Rants, vents, or declarations  
- Pure opinion bait or norm-setting  
- Questions that could be answered without reading the post

**Examples**  
- “Why is life so hard?”  
- “Thoughts?”  
- “Men are terrible communicators.”  
- “What’s the best phone?”  
- “Why are you on Reddit right now?”

**Rule of Thumb**  
If the author could have spent 30 more seconds thinking and the post would materially improve → E = 0

#### E = 1 → Meaningful Effort
The author has done visible work to frame the discussion.  
This includes context, reflection, constraints, failed attempts, or a clear problem setup.

**Common Indicators**  
- Personal or situational context  
- Explicit constraints or trade-offs  
- Acknowledgment of uncertainty  
- Reflection on past attempts  
- Clear intent behind the question  
- Structured framing (even if short)

**Examples**  
- “I’ve tried X and Y, but both failed because… What alternatives make sense?”  
- “People who live alone and feel fulfilled — what changed for you?”  
- “I’m struggling with mismatched bedtimes in my relationship. How do couples navigate this long-term?”

**Rule of Thumb**  
If removing the body would significantly weaken the question → E = 1

#### Important Clarifications

- **Length ≠ Effort**
- Bullet points can be high effort.
- Emotional posts can be E = 1 only if they invite engagement.
- **CMV posts** are E = 1 by default.

## Axis 2 — Discussion Openness (O)

### Definition

Discussion Openness measures the likelihood that the post will generate diverse, non-redundant, reasoning-based responses.  
This is about response entropy, not engagement volume.

### Labels

#### O = 0 → Convergent / Closed Discussion
The post is likely to produce:
- Similar answers
- Correct/incorrect responses
- One-liners or factual replies
- Agreement/disagreement without reasoning

**Common Indicators**  
- Factual questions  
- Advice with a single obvious answer  
- Binary opinion prompts  
- Questions answerable by search  
- Rhetorical or leading questions

**Examples**  
- “What year did X happen?”  
- “How many calories are in an apple?”  
- “Is X good or bad?”  
- “Should I quit my job?” (without constraints)

**Rule of Thumb**  
If most reasonable answers would look similar → O = 0

#### O = 1 → Open / Divergent Discussion
The post invites:
- Multiple valid perspectives
- Experience-based reasoning
- Value trade-offs
- Disagreement without collapse
- Interpretation rather than correctness

**Common Indicators**  
- “How do people…”  
- “What has your experience been…”  
- Hypothetical or counterfactual framing  
- Ambiguous but intentional questions  
- Prompts requiring lived experience

**Examples**  
- “What’s a subtle sign someone has high emotional intelligence?”  
- “People who changed careers in their 30s — what surprised you most?”  
- “How do couples navigate mismatched bedtimes?”

**Rule of Thumb**  
If two smart people could answer in opposite ways and both be right → O = 1

#### Important Clarifications

- Question marks do not guarantee openness.
- Short posts can still be O = 1.
- Long rants are often O = 0.
- Emotional intensity ≠ openness.

## Combined Label Interpretation

Each post receives a binary tuple:

| Effort (E) | Openness (O) | Interpretation                          |
|------------|--------------|------------------------------------------|
| 0          | 0            | Low quality / low discussion value       |
| 0          | 1            | High potential but underdeveloped       |
| 1          | 0            | Thoughtful but convergent                |
| 1          | 1            | High-quality discussion post            |

### Final Post Quality Score (Derived)

I prefer openness > effort. So the scoring must reflect that.

### Recommended Scoring Formula

**FinalScore** = 2 × O + 1 × E

| E  | O  | FinalScore |
|----|----|------------|
| 0  | 0  | 0          |
| 1  | 0  | 1          |
| 0  | 1  | 2          |
| 1  | 1  | 3          |

### Interpretation

A low-effort but highly open question beats a high-effort convergent post.  
This matches my real labeling intuition.

## Edge Case Resolution Rules

- When uncertain → choose the lower value.
- If effort exists but openness is unclear → O = 0.
- If openness exists but effort is weak → O = 1, E = 0.
- Do not infer openness from length or formatting.

## Intended Modeling Implications

- Effort can be learned from structural and self-referential features.
- Openness requires semantic signals (TF-IDF or embeddings).
- These axes should be modeled separately.



# ✅ Label 00 — Low Effort + Low Openness

## Collector’s Checklist (v1.0)

Use this checklist post-by-post.
If any item fails, discard the post — do not downgrade.

---

### 1️⃣ **Effort Axis — Must be 0**

Did the author invest effort in framing the post?

❌ **Effort = 0 IF ANY OF THE FOLLOWING ARE TRUE**

**A. Structural Signals**

* ☐ One sentence or fragment
* ☐ No paragraphing for meaning (line breaks only for style/bullets)
* ☐ No explanation, background, or framing
* ☐ Title-only post or title + 1 trivial line

**B. Cognitive Signals**

* ☐ No constraints stated
* ☐ No trade-offs acknowledged
* ☐ No attempt history (“I tried X…”)
* ☐ No clarification of what kind of response is wanted

**C. Intent Signals**

* ☐ Statement instead of inquiry
* ☐ Vent without guidance (“I’m so tired of…”)
* ☐ PSA / instruction / moral command
* ☐ Brag / announcement without engagement hook

If the post could be written in 10 seconds → **Effort = 0**

---

### 2️⃣ **Openness Axis — Must be 0**

Can this post realistically generate diverse, reasoned replies?

❌ **Openness = 0 IF ANY OF THE FOLLOWING ARE TRUE**

**A. Answer Space**

* ☐ Answers are obvious or factual
* ☐ Replies converge quickly
* ☐ Mostly yes/no, agreement/disagreement
* ☐ Googleable or definitional

**B. Discussion Shape**

* ☐ No room for interpretation
* ☐ No conflicting values possible
* ☐ Replies likely to be jokes, memes, or affirmations

**C. Question Type**

* ☐ Rhetorical question
* ☐ Opinion bait (“X is overrated”)
* ☐ Shower-thought style observation
* ☐ Complaint framed as question (“Why is everyone so dumb?”)

---

### 3️⃣ **Special Case Rules (IMPORTANT)**

#### 🔹 **Rants**

Label 00 IF:

* ☐ Pure emotional vent
* ☐ No advice request
* ☐ No constraints or dilemma
* ☐ No question OR only rhetorical question

❌ **NOT 00** if the rant asks how to act, what to change, or seeks perspectives

#### 🔹 **Personal Experience / Stories**

Label 00 IF:

* ☐ Story only
* ☐ No reflection question
* ☐ No invitation to interpret
* ☐ No “what would you do / how should I think about this”

❌ **NOT 00** if it asks for meaning, advice, or comparison

#### 🔹 **Short Questions**

Label 00 IF:

* ☐ Factual (“What is X?”)
* ☐ Binary (“Is this normal?”)
* ☐ Generic (“Why do people lie?”)

Length does not save it.

#### 🔹 **Bullet / List Posts**

Label 00 IF:

* ☐ Bullets are stylistic, not reasoning
* ☐ No synthesis or framing
* ☐ Reads like notes, not argument

High paragraph count ≠ high effort.

---

### 4️⃣ **Final Gate (Non-Negotiable)**

Before assigning 00, ask:

“Would most replies be one-liners?”

* If yes → ✅ 00
* If no → ❌ discard

# ✅ Label 10 — Meaningful Effort + Closed Discussion

## Mental Summary

> **“This took thought to write — but there’s basically one reasonable answer.”**

---

## 1️⃣ Effort Axis — **Must be 1**

The author did real framing work.

### ✔ Effort = 1 IF MOST of the following are true

#### **A. Structural Signals**
- ☐ Multiple paragraphs with meaning  
- ☐ Clear narrative or argument  
- ☐ Specific context (time, place, constraints)  
- ☐ Body adds essential information beyond title  

#### **B. Cognitive Signals**
- ☐ Explains why the question exists  
- ☐ Shows reflection or reasoning  
- ☐ Mentions trade-offs, attempts, or uncertainty  
- ☐ Clarifies what kind of response is wanted  

#### **C. Intent Signals**
- ☐ Genuine problem to solve  
- ☐ Asks for explanation, not validation  
- ☐ Shows responsibility for the issue  

📌 **Rule of Thumb**  
If deleting the body would destroy the post → **Effort = 1**

---

## 2️⃣ Openness Axis — **Must be 0**

Despite the effort, the answer space is narrow.

### ❌ Openness = 0 IF ANY are true

#### **A. Answer Space**
- ☐ One correct explanation  
- ☐ Replies mostly agree  
- ☐ Advice converges quickly  
- ☐ Solutions are obvious to domain users  

#### **B. Discussion Shape**
- ☐ Experience doesn’t meaningfully vary outcomes  
- ☐ Disagreement would be pedantic  
- ☐ Most replies look structurally similar  

#### **C. Question Type**
- ☐ “What should I do?” with clear best practice  
- ☐ Technical / procedural explanation  
- ☐ Legal, medical, travel, or finance rules  
- ☐ “Am I wrong?” with obvious moral answer  

📌 **Rule of Thumb**  
If experts would mostly say the same thing → **Openness = 0**

---

## 3️⃣ Common 10 Patterns (Learn These)

### ✅ Strong 10 Examples
- “I’ve been lifting for 6 months and my bench has stalled at X. Here’s my routine. What am I missing?”
- “My landlord is doing X. Here’s the lease clause. Is this legal?”
- “I’m choosing between job A and B; here are the details. Which is better?”
- “Why does my code deadlock only under load? Here’s the snippet.”

### ❌ NOT 10 (Be Careful)
- Turns into philosophy → **11**
- Asks for experiences → **01 or 11**
- Seeks validation → **00**

# **🟦 Label 01 — Low Effort + Open Discussion**

**Mental Summary**  
**“This is an honest curiosity — but lightly framed and open to many valid answers.”**

These posts ask interesting questions, but the author has not done real framing work, and the discussion space is broad.

---

**1️⃣ Effort Axis — Must be 0**

The author did little to no framing work.

**❌ Effort = 0 IF MOST of the following are true**

- **A. Structural Signals**
  - Short body or loosely structured paragraphs  
  - Little to no concrete context (time, place, constraints missing)  
  - Title alone nearly captures the whole question  
  - Body mostly restates the title  

- **B. Cognitive Signals**
  - No evidence of prior research or reading  
  - No attempted explanation or hypothesis  
  - No trade-offs, edge cases, or constraints mentioned  
  - “I was wondering / I’m curious / Just thought of this” tone  

- **C. Intent Signals**
  - General curiosity, not problem-solving  
  - Not time-sensitive or personally consequential  
  - Asking what people think, not what is correct  
  - Would be equally valid as a shower-thought  

**📌 Rule of Thumb**  
- If the post could be answered just as well without the body → **Effort = 0**

---

**2️⃣ Openness Axis — Must be 1**

The answer space is broad, with multiple valid explanations or perspectives.

**✅ Openness = 1 IF MOST of the following are true**

- **A. Answer Space**
  - Multiple plausible explanations exist  
  - Different experts may emphasize different factors  
  - No single “correct” or authoritative answer  
  - Answers vary by culture, time, or interpretation  

- **B. Discussion Shape**
  - Replies differ meaningfully from each other  
  - Personal knowledge or background changes answers  
  - Disagreement is reasonable, not pedantic  
  - Threads branch rather than converge  

- **C. Question Type**
  - Historical “why” questions  
  - Cultural or linguistic curiosity  
  - Educational or narrative questions  
  - “How is X viewed / taught / perceived?”  

**📌 Rule of Thumb**  
- If many good answers can coexist without contradiction → **Openness = 1**

---

**3️⃣ Common 01 Patterns (Learn These)**

- **✅ Strong 01 Examples**
  - “Why do people say X even though it’s inaccurate?”  
  - “How is [historical event] taught in other countries?”  
  - “Why do animals do [behavior]?”  
  - “Why does English use this word instead of that?”  
  - “Why do some cultures consider X rude?”  

- **❌ NOT 01 (Be Careful)**
  - Contains strong personal stakes → **10 or 11**  
  - Seeks validation or reassurance → **00**  
  - Narrow technical explanation → **10**  
  - Philosophical debate → **11**

---

**🧭 Subreddits That Produce Reliable 01 Posts**

These are gold mines for low-effort, open-ended curiosity — minimal framing, broad discussion, very few hard constraints.

---

**🏛 History / Culture / Society (VERY SAFE)**

- r/AskHistorians (only beginner-style posts)  
- r/history  
- r/AskHistory  
- r/AskSocialScience  
- r/AskAnthropology  
- r/AskSociology  
- r/AskCulturalStudies  
- r/AskReligion  
- r/AskTheologists  
- r/AskPhilosophy (non-technical posts)

---

**🌍 Language / Linguistics / Naming**

- r/etymology  
- r/linguistics (casual questions)  
- r/NoStupidQuestions  
- r/EnglishLearning (why-does-English-do-X)  
- r/AskLanguage  
- r/translator (conceptual questions)

---

**🔬 General Science Curiosity (NOT technical)**

- r/AskScienceDiscussion  
- r/AskBiology (why questions)  
- r/AskPhysics (conceptual curiosity)  
- r/askscience (ELI5-style only)

- ⚠️ Avoid posts with equations, code, or experiments (those drift to **10**).

---

**🌐 Geography / International / Education**

- r/geography  
- r/AskEurope  
- r/AskAnAmerican  
- r/AskUK  
- r/AskLatinAmerica  
- r/AskAsia

---

**🧠 Psychology / Behavior (Non-clinical)**

- r/AskPsychology  
- r/AskBehavioralScience  
- r/socialskills (theory-only posts)  
- r/humanbehavior


# ✅ Label 11 — Meaningful Effort + Open Discussion
Mental Summary

“This took real thought to write — and multiple well-reasoned answers are genuinely possible.”

Label 11 posts show clear intellectual effort and invite substantive, divergent discussion rather than converging on a single “correct” response.

1️⃣ Effort Axis — Must be 1

The author has done serious framing work.

✔ Effort = 1 IF MOST of the following are true
A. Structural Signals

☐ Multi-paragraph body with logical flow

☐ Clear framing of a problem, dilemma, or question

☐ Specific context (historical, ethical, technical, social, personal constraints)

☐ Body meaningfully expands the title (not just emotional venting)

B. Cognitive Signals

☐ Shows reflection, reasoning, or internal conflict

☐ Explicitly weighs multiple perspectives

☐ Clarifies what kind of answers are desired

☐ Demonstrates awareness of complexity or uncertainty

C. Intent Signals

☐ Seeks understanding, not validation

☐ Asks a real question, not rhetorical outrage

☐ Takes responsibility for the framing (not “tell me what to think”)

📌 Rule of Thumb
If removing the body would destroy the question → Effort = 1

2️⃣ Openness Axis — Must be 1

The answer space is broad, legitimate, and non-convergent.

✔ Openness = 1 IF MOST of the following are true
A. Answer Space

☐ Multiple reasonable positions exist

☐ Answers vary meaningfully by framework or worldview

☐ No single authoritative answer dominates

☐ Disagreement is substantive, not pedantic

B. Discussion Shape

☐ Responses differ in structure, not just wording

☐ Personal experience, theory, and reasoning all matter

☐ Experts may disagree in good faith

☐ Discussion does not collapse into “best practice”

C. Question Type

☐ Ethical or moral dilemmas

☐ Philosophical or interpretive questions

☐ “How should we think about X?”

☐ Cultural, historical, or sociological interpretation

☐ Trade-off analysis with no clear optimum

📌 Rule of Thumb
If thoughtful people can disagree without being wrong → Openness = 1

3️⃣ What 11 Is NOT (Hard Exclusions)

❌ NOT 11 if:

It’s a rant with a question mark

It’s asking for advice with obvious best practices

It’s technical troubleshooting with a correct fix

It’s “what do you think?” with no framing

It’s validation-seeking or identity-affirming

It’s a yes/no or factual explanation question

4️⃣ Canonical 11 Examples
✅ Strong 11

“Is it morally justifiable to sentence juveniles to life imprisonment?”

“Has globalization done more harm than good for developing economies?”

“Is historical objectivity actually possible in modern historiography?”

“Should free speech protect misinformation?”

“Are nation-states becoming obsolete in a digital world?”

❌ Common Mislabels

Opinion polls → 01

Rants with context → 01

Technical ‘why/how’ → 10

Shallow philosophy → 00

🧠 Key Distinction

11 = effort in framing + openness in answers
01 = openness without effort
10 = effort without openness