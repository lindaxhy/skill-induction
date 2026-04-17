"""
Steps E3, E4 (annotation) + Assembler for percy-liang-abstract task.
Reads fingerprint from output/fingerprint_raw.md, runs E4 annotation,
then assembles the final generative skill file.
"""
import os, re, json
import requests

API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL   = "openai/gpt-5.4-pro"
BASE    = os.path.dirname(os.path.abspath(__file__))

def llm(system: str, user: str, temperature: float = 0.2) -> str:
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}",
                 "Content-Type": "application/json"},
        json={"model": MODEL,
              "temperature": temperature,
              "messages": [{"role": "system", "content": system},
                           {"role": "user",   "content": user}]},
        timeout=180,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()

def load(path):
    with open(path) as f: return f.read()

# ─── E3: Select reference examples (N=2, use all since N < 10) ───────────────
print("[E3] Using all 2 examples (N < 10 → use all).")
examples = {
    "paper1": load(f"{BASE}/examples/paper1_replay_finetuning.md"),
    "paper2": load(f"{BASE}/examples/paper2_infinite_compute.md"),
}
fingerprint = load(f"{BASE}/output/fingerprint_raw.md")

# ─── E4: Generate style annotations ──────────────────────────────────────────
print("[E4] Generating style annotations...")

e4_user = """You are annotating paper abstract examples to teach a language model
the abstract writing style of the Kotha/Kim/Liang research group on data-efficient pre-training.

Below is the style fingerprint extracted from their papers:

=== STYLE FINGERPRINT ===
{fingerprint}
=== END FINGERPRINT ===

Now annotate each of the 2 papers below.
For each paper's abstract, identify:
- Which of the unique mechanisms from Section 5 appear? Quote the specific line.
- Which vocabulary/structural patterns from the fingerprint are present?

Keep annotations concise (3–5 sentences per paper). Be specific — name the mechanism
and quote the exact phrase that instantiates it.

{examples}
""".format(
    fingerprint=fingerprint,
    examples="\n\n---\n\n".join(
        f"PAPER {i+1}:\n{v}" for i, v in enumerate(examples.values())
    )
)

annotations = llm(
    system="You are an expert annotator for academic writing style analysis.",
    user=e4_user,
)
with open(f"{BASE}/output/annotations.md", "w") as f:
    f.write(annotations)
print("[E4] Annotations saved to output/annotations.md")

# ─── Assembler: Build generative skill file ───────────────────────────────────
print("[Assembler] Building generative skill file...")

assemble_user = """You are assembling a generative skill file for LLM use.

The skill file will be used as a system prompt. When given a paper's Introduction,
the model using this skill must generate an abstract in the style of the
Kotha/Kim/Liang research group on data-efficient pre-training.

Use the following materials to assemble the skill file using the GENERATIVE SKILL TEMPLATE:

## STYLE FINGERPRINT
{fingerprint}

## ANNOTATED REFERENCE EXAMPLES
{annotations}

## FULL EXAMPLE TEXTS (for the Prototypes section — include abbreviated versions)
{examples}

---

Assemble a complete skill file with this exact structure:

```
# Kotha-Kim-Liang Data-Efficient Pre-training Abstract Generation Skill

[1-line identity + most distinctive quality]

## Style Fingerprint                          ← FEATURES
**Vocabulary and diction:** ...
**Structure and form:** ...
  - Opening sentence subject: ...
  - Abstract skeleton: ...
**Problem framing:** ...
**Stance and quantification:** ...
**Unique mechanisms:**
  - [Mechanism name]: [quote] → [effect]
  (list all mechanisms)
**What this style avoids:** ...

## Reference Examples                         ← PROTOTYPES
(Include all 2 papers. For each: title, then the ABSTRACT TEXT IN FULL,
then a "Style features:" annotation of 2-3 sentences citing specific mechanisms.)

## Generation Instructions                    ← TOOLS
(7-step generation process based on the fingerprint and mechanisms)
1. ...
```

The skill file should be self-contained and immediately usable as a system prompt.
Write it in second person ("You are generating...").
Do NOT truncate any abstract in the Prototypes section.
""".format(
    fingerprint=fingerprint,
    annotations=annotations,
    examples="\n\n---\n\n".join(
        f"PAPER {i+1}:\n{v}" for i, v in enumerate(examples.values())
    )
)

skill_file = llm(
    system="You are assembling a precise, immediately usable LLM skill file.",
    user=assemble_user,
    temperature=0.1,
)

# Strip markdown code fence if present
skill_file = re.sub(r'^```[^\n]*\n', '', skill_file.strip())
skill_file = re.sub(r'\n```$', '', skill_file.strip())

out_path = f"{BASE}/output/percy-liang-abstract-skill.md"
with open(out_path, "w") as f:
    f.write(skill_file)
print(f"[Assembler] Skill file saved to output/percy-liang-abstract-skill.md")
print(f"            ({len(skill_file)} chars, {len(skill_file.splitlines())} lines)")
