# Skill Induction Pipeline

A general-purpose workflow for building LLM skills from examples.

**Core concept:** Distill human judgment from a set of examples into a reusable system prompt (skill file) — a process called *taste model induction*. The induced skill answers: "What would someone with this taste do with this new input?"

Validated on: essay scoring (DREsS), resume scoring (CareerCorpus), resume classification (opensporks/resumes), style induction.

---

## Phase 0: Task Analysis & Routing

Two independent axes determine your path:

**Axis 1 — Signal type** (what your examples tell you):


| Signal                 | What you have                                    | Typical source                                     |
| ---------------------- | ------------------------------------------------ | -------------------------------------------------- |
| **S — Scored/Labeled** | Each example has an explicit score or category   | Human annotation, exam grades, star ratings        |
| **P — Pairwise**       | Only relative judgments: A is better than B      | Arena battles, A/B tests, human ranking sessions   |
| **E — Examples-only**  | Positive examples (± negatives), no label        | Curated content, style samples, "good output" sets |
| **I — Implicit**       | Behavioral signals (clicks, engagement, accepts) | Logs, interaction data → convert to P or E first   |


**Axis 2 — Application mode** (what the skill will do with new input):


| Mode             | Skill task                                            | Output format                     |
| ---------------- | ----------------------------------------------------- | --------------------------------- |
| **J — Judge**    | Evaluate / score / classify / filter existing content | Score, label, pass/fail           |
| **G — Generate** | Produce new content that matches the induced taste    | Text, code, structured output     |
| **R — Rank**     | Order or select from a candidate set                  | Ranking list, pairwise preference |


**Routing table — common configurations:**


| Scenario                         | Signal     | Mode   |
| -------------------------------- | ---------- | ------ |
| Essay / subjective scoring       | S          | J      |
| Traffic / engagement prediction  | S          | J      |
| Sentiment / rating prediction    | S          | J      |
| Resume / applicant screening     | S or E     | J      |
| Data filtering / curation        | E          | J      |
| Style induction                  | E          | G      |
| Text style transfer              | E          | G      |
| Preference learning (arena data) | P          | R or J |
| Personalized recommendation      | I → P or E | R      |


**Data scale modifier** (applies to every route):


| Scale        | N    | Adaptation                                                      |
| ------------ | ---- | --------------------------------------------------------------- |
| Rich         | ≥ 30 | Use statistical methods (quintile sampling, distribution stats) |
| Sparse       | 5–15 | Skip stats; use all examples directly                           |
| Ultra-sparse | < 5  | Fingerprint / criteria only; treat all examples as reference    |


**Output type → evaluation metric (Signal S only):**


| Output                        | Primary metric    | Secondary                   |
| ----------------------------- | ----------------- | --------------------------- |
| Continuous (0–1, 0–100)       | Pearson r         | MAE                         |
| Ordinal (1–5 with half steps) | QWK               | Pearson                     |
| Multi-dimensional ordinal     | Per-dimension QWK | Total Pearson               |
| Binary                        | F1                | Accuracy, Precision, Recall |
| Multi-class                   | Macro-F1          | Per-class F1, Accuracy      |


---

## Phase 1: Induce the Taste Model

### Signal S — Scored / Labeled Examples

#### Step S1 — Extract or Generate Rubric

**Have an annotation guide / rubric?**

- Extract and clean it: remove example-specific references, keep scoring criteria per dimension
- For scoring: keep Excellent / Adequate / Weak descriptions
- For classification: keep per-category distinguishing features

**No rubric? → Induce from data (1 LLM call):**

- Contrast high-scoring vs low-scoring examples (scoring tasks)
- Show 2–3 examples per category (classification tasks)

> **Multi-population warning:** If sub-groups have mean score differences > 0.2, show the rubric inducer the best and worst example *from each group* separately. Without this, the rubric conflates group identity with quality. Instruct the LLM: *"Write criteria that work across all groups — focus on specificity, depth, and impact relative to group norms, not group-specific vocabulary."*

> **Sparse (N < 15):** Use all available examples for rubric induction. Provide background domain knowledge as context if contrast is weak.

#### Step S2 — Compute Score Distribution from Training Set

Embed population statistics to prevent mean-regression:

- Overall: mean, std, range, Q10/Q25/Q50/Q75/Q90
- Per sub-group (domain, category): mean, std
- Calibration note: "A score of X is genuinely below average for this population"
- For classification: class distribution (%)

> **Sparse (N < 15):** Skip detailed statistics. Embed a simple range statement: "Examples in this dataset range from X to Y."

#### Step S3 — Select Calibration Examples

> **Critical rule: do NOT truncate.** Use the full text. Truncation breaks calibration.

**Single-population:**

- Scoring: 2–3 examples per quintile (10–15 total)
- Classification: 1–2 examples per class

**Multi-population (sub-groups with divergent score distributions):**
Use **per-group stratified selection**: Q20 and Q80 within each group's own distribution → `N_groups × 2` examples. Global quintiles will starve low-scoring groups — if Group A mean=0.44 and Group B mean=0.81, global bottom-20% is entirely Group A, leaving it with no high anchor.

> **Sparse (N < 15):** Use all examples, sorted by score or grouped by class.

#### Step S4 — Generate Diagnostic Annotations (1 LLM call)

```
System: You are an expert [domain] annotator.
        Write 2–3 sentence explanations for why each example received its label/score,
        citing specific observable features using rubric vocabulary.
User:   [rubric ≤1500 chars] + [all N examples in numbered blocks]
Output: JSON {"1": "annotation", ..., "N": "annotation"}
```

---

### Signal P — Pairwise Preferences

Use when you only have comparison outcomes (A won, B lost), not absolute scores.

#### Step P1 — Extract Preference Dimensions (1 LLM call)

Sample 10–20 representative pairs (winner + loser). Ask:

```
Here are N pairs where Version A was preferred over Version B.
What characteristics do winners consistently have?
What do losers consistently lack?
List 5–8 preference dimensions, with at least 2 quoted examples per dimension.
Do not use vague terms — name specific patterns.
```

Output: a structured **preference profile** ("preferred outputs tend to: X, Y, Z").

#### Step P2 — Select Representative Pairs

Choose 5–8 pairs that:

- Span different preference reasons (some style, some substance, some structure)
- Include both close calls and decisive wins — both are informative
- Avoid pairs where the winner is obviously better; those add little signal

#### Step P3 — Generate Pair Annotations (1 LLM call)

For each pair: "Why did A win? Which dimensions from the preference profile does it satisfy? What specifically does B lack?"

> **Sparse (< 5 pairs):** Use all pairs. Supplement with any domain knowledge about what this judge cares about.

---

### Signal E — Examples Only (Positive ± Negative)

Use when you have curated examples of what you want, but no explicit label.

#### Step E1 — Gather and Organize Examples

- **Positive examples**: 5–30 pieces that represent the target. Maximize variety over volume — different topics/moods/lengths that all clearly belong.
- **Negative examples** (optional, high value): 3–10 near-misses. Most useful when the style is defined partly by what it *doesn't* do.

> **Ultra-sparse (N < 5 positives):** Works, but the induced pattern will be narrow. State this in the skill file.

#### Step E2 — Extract Style Fingerprint (1 LLM call + human review)

```
User:   [N positive examples, labeled "Positive Example N"]
        [K counter-examples if available, labeled "Counter-example K"]

        Extract a structured style fingerprint. Each dimension must be specific enough
        for another writer to reproduce — cite original phrases, name syntactic patterns,
        do not use vague adjectives like "poetic" or "professional".

        1. Vocabulary and diction (5+ specific examples)
        2. Structure and form (sentence rhythm, parallelism, line breaks)
        3. Imagery / content system (core clusters, cross-line chains)
        4. Stance and expression (3 examples of object-carries-emotion)
        5. MOST IMPORTANT — unique mechanisms: 3-5 constructions that appear
           in these examples but not in generic content of this domain.
           For each: name it, quote ≥2 source lines, explain the effect.
        6. What this style conspicuously avoids
```

**Human review required:** Read section 5. LLMs reliably produce abstract category names ("emotional objectification") rather than operational mechanisms. If you see patterns the LLM missed, write them in directly. One hand-curated mechanism in section 5 is worth five auto-generated paragraphs.

> **Sparse (N < 8):** The fingerprint will be narrower. Expect to refine after seeing generated outputs.

#### Step E3 — Select Reference Examples

Pick 5–10 positive examples that maximize variety within the style. Include 2–5 negative examples if available. Use all if total N < 10.

> **Do NOT truncate.** Full text is required — rhythm, structure, and closure patterns break with truncation.

#### Step E4 — Generate Style Annotations (1 LLM call)

```
System: You are annotating examples to teach a language model a specific style.
        For each example, identify concrete style evidence — quote phrases,
        name patterns, point to structural choices.
        Focus especially on the unique mechanisms from section 5 of the fingerprint.
User:   [fingerprint] + [all selected examples]
        For positives: which mechanisms from section 5 appear? Quote the specific line.
        For negatives: which mechanism is absent or violated? What did the author do instead?
```

---

### Signal I — Implicit / Interaction Data

Convert to P or E before proceeding:

- **To P**: extract pairwise comparisons — treat high-engagement vs low-engagement items from similar contexts as A > B pairs
- **To E**: treat top-K engaged items as positive examples, bottom-K (if available) as negative examples

Then follow Signal P or E path.

---

## Phase 2: Assemble the Skill File

Signal determines *what goes into* the skill; **Application mode determines the template**.

### Application J — Judge Skill

```markdown
# [Task] Evaluation Skill

[1-line evaluator identity + task definition]

## Criteria / Rubric
[from Step S1 — cleaned rubric or induced criteria]
[or from Step E2 — style fingerprint adapted for classification]

## Score / Label Distribution (Signal S, N ≥ 15 only)
[Stats from Step S2]
[Calibration note: what the middle value means for this population]

## Calibration Examples
[Sorted low→high for scoring / grouped by class for classification]

### Example N — [label/score] | [sub-group if applicable]
[FULL input text — no truncation]
**Why [label/score]:** [2–3 sentence diagnostic annotation]

## Scoring Instructions
1. Assess against the criteria / rubric above.
2. Compare against calibration examples for anchoring.
3. Output ONLY: {"score": 0.XX}  or  {"category": "LABEL"}
```

**User message format** (keep this consistent across zero-shot and skill runs):

```
Please [task description].
### Answer format: {"key": value}
[Valid range or valid labels]
Please answer ONLY in the above JSON format.
### [input field 1]: ...
```

### Application G — Generate Skill

```markdown
# [Style/Task] Generation Skill

[1-line identity: "You are generating X in the style of Y"]
[Most distinctive quality of this style in one sentence]

## Style Fingerprint
**Vocabulary and diction:** [specifics]
**Structure and form:** [specifics]
**Themes and imagery:** [specifics]
**Stance and expression:** [specifics]
**Unique mechanisms:** [A, B, C — named and quoted]
**What this style avoids:** [specifics]

## Reference Examples

### Example N
[FULL text — no truncation]
**Style features present:** [annotation citing specific mechanisms]

## Counter-examples (if negatives collected)

### Counter-example N
[FULL text — no truncation]
**What it lacks:** [annotation]

## Generation Instructions
1. Study the fingerprint, especially the unique mechanisms.
2. Before writing, choose one mechanism to anchor the piece.
3. Draw on the *patterns* from examples, not their specific words — invent new content.
4. Emotion is always carried by objects. Never state it directly.
5. Check your draft against counter-examples.
6. Output only the generated content, no explanation.
```

### Application R — Rank Skill

```markdown
# [Task] Ranking / Preference Skill

[1-line ranker identity]

## Preference Profile
[from Step P1 or derived from S/E signal]
Preferred outputs tend to: [X, Y, Z]
Outputs to avoid: [...]

## Reference Comparisons

### Preferred: [brief label]
[FULL text]
**Why preferred:** [annotation citing preference dimensions]

### Less preferred: [brief label]
[FULL text]
**Why not preferred:** [annotation]

## Ranking Instructions
1. Assess each candidate against the preference profile above.
2. For pairwise comparison: {"preferred": "A", "reason": "..."}
3. For ranked list: {"ranking": ["id1", "id2", ...], "reasoning": "..."}
```

---

## Phase 3: Evaluate Against Baseline

Always compare against a baseline. What counts as baseline depends on signal:


| Signal | Baseline                                           | Test                    |
| ------ | -------------------------------------------------- | ----------------------- |
| S      | Zero-shot (no system prompt, task in user message) | Skill system prompt     |
| P      | Coin-flip or majority-class prediction             | Skill                   |
| E      | Zero-shot generation                               | Skill-guided generation |


**Signal S evaluation decision table:**


| Observation                  | Diagnosis                | Fix                                                      |
| ---------------------------- | ------------------------ | -------------------------------------------------------- |
| Primary metric improves      | Skill is effective       | Ship it                                                  |
| pred_mean systematically off | Reference frame mismatch | Strengthen distribution stats; add extreme examples      |
| pred_std too narrow          | Hedging                  | Add more examples at both ends                           |
| One sub-group drops          | Group bias               | Per-group stratified examples; add domain note to rubric |
| One class consistently worse | Rubric gap               | Add targeted examples for that class                     |
| Skill hurts on all metrics   | Wrong examples or rubric | Re-induce; check domain mismatch                         |


**Signal E / G evaluation (two levels):**

*Level 1 — Human judgment (required):* Generate 5–10 outputs. For each: "Does this feel like it belongs alongside the reference examples?" Rate yes/partially/no, note specific misses.

*Level 2 — Blind comparison (recommended for version comparison):* Save outputs from each skill version to files. Run the [comparator agent](https://github.com/anthropics/skills/blob/main/skills/skill-creator/agents/comparator.md) with `output_A` / `output_B` and the generation prompt. The comparator judges blindly — preventing your authorship bias toward the newer version. Customize the rubric dimensions for your style task (authenticity, mechanism usage, avoidance of direct emotion, no recycled phrases).

**Signal P / R evaluation:**
Compute win rate on a held-out set of pairs the skill hasn't seen. Skill should win > 60% to justify its token cost.

---

## Phase 4: Iterative Refinement (max 3 rounds)

1. Evaluate on dev set (Signal S: 100 examples; Signal E/G: 5–10 generated outputs per round)
2. Apply the most impactful fix
3. Re-evaluate; stop when gain < threshold (S: < 0.02 on primary metric; E/G: qualitative plateau)

**LLM calls per iteration:** 1 (revise rubric, re-annotate, or refine fingerprint/preference profile)

**Refinement triggers by signal:**

*Signal S:* follow the evaluation decision table above.

*Signal E / G:*

- "Generic" → strengthen fingerprint section 5; add contrasting negatives
- "Missing a key characteristic" → add a targeted example that exemplifies it
- "Mimics surface, misses depth" → add a counter-example of surface mimicry
- "Outputs feel like each other" → increase example variety; remove near-duplicates

*Signal P / R:*

- "Wrong dimension prioritized" → re-run Step P1 with more pairs; add explicit dimension weights
- "Wins on obvious pairs, loses on close calls" → add more close-call pairs to Step P2

**Signal E / G: cross-prompt pattern analysis (after 3+ iterations):**
The [analyzer agent](https://github.com/anthropics/skills/blob/main/skills/skill-creator/agents/analyzer.md) (benchmark patterns mode) can surface: which prompts consistently fail all versions (prompt is ill-suited), which versions win on some prompt types but lose on others (fingerprint blind spot), high-variance prompts needing multi-sample averaging.

---

## Phase 5: Final Configuration

```
System prompt:  Skill file
User message:   Task instructions + output format spec + input
Model:          GPT-4o or equivalent
Temperature:    0.0 for J (determinism); 0.5–0.8 for G (creativity); 0.0 for R
Timeout:        60s per call with 1–2 retries
```

**Optional: eval-viewer for qualitative inspection**
The skill-creator [eval-viewer](https://github.com/anthropics/skills/blob/main/skills/skill-creator/eval-viewer/generate_review.py) renders outputs side-by-side across iterations. Direct drop-in for Signal E/G review. For Signal S, wrap Python eval results into `benchmark.json` format by treating "predicted within threshold of true" as a per-example pass/fail assertion.

**Validated results:**


| Task                    | Signal | Mode | Dataset           | Zero-shot | Skill | Metric   |
| ----------------------- | ------ | ---- | ----------------- | --------- | ----- | -------- |
| Essay scoring (content) | S      | J    | DREsS_New n=228   | 0.150     | 0.229 | QWK      |
| Essay scoring (total)   | S      | J    | DREsS_New n=228   | 0.188     | 0.280 | Pearson  |
| Resume quality scoring  | S      | J    | CareerCorpus n=61 | 0.551     | 0.752 | Pearson  |
| Resume classification   | S      | J    | opensporks n=200  | 0.695     | 0.740 | Accuracy |


---

## Automation Skeleton

```python
def induce_skill(examples,        # list of dicts: text + label/score (S), or
                                  #   winner/loser pairs (P), or
                                  #   text + is_positive (E)
                 signal,          # "S", "P", "E", "I"
                 mode,            # "J", "G", "R"
                 label_col=None,  # S: column with scores/labels
                 input_cols=None, # S/P: columns forming the input
                 group_col=None,  # S: sub-group column for multi-population
                 style_name=None, # E/G: name/description of the style
                 rubric_text=None,# S/J: existing rubric (or None to induce)
                 dev_examples=None,
                 n_iter=3):

    df = pd.DataFrame(examples)

    # Signal I: convert first
    if signal == "I":
        signal, df = convert_implicit(df)   # returns "P" or "E"

    if signal == "S":
        rubric = clean_rubric(rubric_text) if rubric_text else induce_rubric(
            df, label_col, input_cols, group_col
        )
        stats = compute_distribution(df, label_col, group_col) if len(df) >= 15 else None

        if len(df) < 15:
            selected = df.sort_values(label_col).to_dict('records')
        elif group_col and group_means_diverge(df, label_col, group_col, threshold=0.2):
            selected = select_per_group(df, label_col, group_col)  # Q20+Q80 per group
        else:
            selected = select_quintiles(df, label_col, n_per_quintile=3)

        annotations = batch_annotate_diagnostic(rubric, selected)
        taste_model = {"rubric": rubric, "stats": stats,
                       "examples": selected, "annotations": annotations}

    elif signal == "P":
        preference_profile = extract_preference_dimensions(df)     # 1 LLM call
        pairs = select_representative_pairs(df, n=8)
        annotations = batch_annotate_pairs(preference_profile, pairs)  # 1 LLM call
        taste_model = {"profile": preference_profile, "pairs": pairs,
                       "annotations": annotations}

    elif signal == "E":
        positives = [e for e in examples if e.get('is_positive', True)]
        negatives = [e for e in examples if not e.get('is_positive', True)]
        fingerprint = extract_style_fingerprint(positives, negatives)  # 1 LLM call
        # ↑ HUMAN REVIEW section 5 before continuing
        selected_pos = positives if len(positives) <= 10 else select_varied(positives, n=10)
        selected_neg = negatives[:5] if negatives else []
        annotations = batch_annotate_style(fingerprint, selected_pos, selected_neg)  # 1 LLM call
        taste_model = {"fingerprint": fingerprint,
                       "examples": selected_pos, "negatives": selected_neg,
                       "annotations": annotations}

    skill = assemble_skill(taste_model, mode)  # uses J / G / R template

    if dev_examples and signal == "S":
        baseline = evaluate_zero_shot(dev_examples, label_col, input_cols)
        for _ in range(n_iter):
            metrics = evaluate(skill, dev_examples, label_col, input_cols)
            if metrics['primary'] > baseline['primary'] + 0.02:
                break
            issues = diagnose(metrics, dev_examples, group_col)
            skill = revise_skill(skill, issues, df)  # 1 LLM call

    return skill
```

**Human review checkpoints:**

- Signal S: verify rubric quality after induction — confirm criteria reflect annotator intent, not spurious correlations
- Signal E: review fingerprint section 5 — add any mechanisms the LLM failed to identify
- Signal P: review preference dimensions — confirm they match actual human judgment criteria

---

## Common Pitfalls


| Pitfall                                         | Signal | Mode | Symptom                                                | Fix                                                  |
| ----------------------------------------------- | ------ | ---- | ------------------------------------------------------ | ---------------------------------------------------- |
| Truncating examples                             | Any    | Any  | Skill underperforms baseline                           | Use full text always                                 |
| Global quintile sampling with multi-pop data    | S      | J    | One group's metric collapses                           | Per-group Q20/Q80                                    |
| Rubric induced from global high/low (multi-pop) | S      | J    | Rubric encodes group identity as quality               | Show per-group high/low to inducer                   |
| Computing stats on N < 15                       | S      | J    | Noisy stats mislead                                    | Skip stats; use simple range note                    |
| Fingerprint section 5 too abstract              | E      | G    | Outputs generic; model reverts to direct statements    | Human-curate section 5 with named, quoted mechanisms |
| No counter-examples for a sharp-boundary style  | E      | G    | Model misses "don'ts"; may plagiarize training phrases | Add 2–3 near-miss negatives                          |
| Too many near-duplicate positive examples       | E      | G    | Outputs all feel the same                              | Curate for variety                                   |
| Pairwise pairs too easy                         | P      | R    | High win rate on training, poor generalization         | Add close-call pairs                                 |
| Repeating rubric/criteria in user message       | S      | J    | Model ignores system prompt                            | Keep user message to format spec + input only        |
| No population stats (large N, Signal S)         | S      | J    | pred_mean drifts to scale midpoint                     | Always embed mean, std, calibration note             |


---

## Response Parsing

LLMs sometimes return unquoted JSON keys. Always implement a regex fallback:

```python
match = re.search(r'\{[^}]+\}', response, re.DOTALL)
if match:
    blob = match.group()
    try:
        result = json.loads(blob)
    except json.JSONDecodeError:
        result = {}
        for key in expected_keys:
            m = re.search(rf'{key}\s*[:\s]+([^\s,}}]+)', blob)
            if m:
                result[key] = m.group(1).strip('"\'')
```

