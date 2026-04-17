"""
Steps E1, E2: Gather examples and extract style fingerprint for percy-liang-abstract task.
"""
import os, re
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

# ─── E1: Gather examples ─────────────────────────────────────────────────────
print("[E1] Loading examples...")
examples = {
    "paper1": load(f"{BASE}/examples/paper1_replay_finetuning.md"),
    "paper2": load(f"{BASE}/examples/paper2_infinite_compute.md"),
}
print(f"     Loaded {len(examples)} positive examples (N < 5 → ultra-sparse)")

# ─── E2: Extract style fingerprint ───────────────────────────────────────────
print("[E2] Extracting style fingerprint...")

e2_prompt = """Below are positive examples of abstracts written by a specific NLP/ML research group
(Suhas Kotha, Konwoo Kim, Percy Liang, and collaborators) working on data-efficient
language model pre-training. Each example contains the paper's Introduction and Abstract.

{examples}

---

Extract a structured style fingerprint for their ABSTRACT writing style.
Each dimension must be specific enough for another writer to reproduce — cite original
phrases, name syntactic patterns, do not use vague adjectives like "clear" or "well-written".

1. **Vocabulary and diction** (5+ specific word/phrase examples)
   - What verbs do they use to introduce findings?
   - What nouns/phrases recur across abstracts?
   - How do they quantify improvements?

2. **Structure and form** (sentence rhythm, parallelism, transitions)
   2b. **Opening sentence**: what is the grammatical subject of the first sentence?
       (e.g., the problem setting, "We", a method name, a trend statement)
   2c. **Abstract skeleton**: what is the typical sequence of moves
       (e.g., setup → question → finding 1 → finding 2 → ... → practical validation)?

3. **Problem framing** (how is the research gap introduced? what motivates the work?)

4. **Stance and expression** (how do they signal confidence, surprise, or limitation?
   Give 3+ examples of how stance is carried by specific word choices.)

5. **MOST IMPORTANT — unique mechanisms**: 3–5 constructions that appear in these
   abstracts but NOT in generic ML paper abstracts.
   For each mechanism: **name it**, **quote ≥2 source lines**, **explain the effect**.

6. **What this style conspicuously avoids**
""".format(
    examples="\n\n---\n\n".join(
        f"POSITIVE EXAMPLE {i+1}:\n{v}" for i, v in enumerate(examples.values())
    )
)

fingerprint = llm(
    system="You are an expert writing style analyst specializing in academic ML research papers.",
    user=e2_prompt,
)

os.makedirs(f"{BASE}/output", exist_ok=True)
with open(f"{BASE}/output/fingerprint_raw.md", "w") as f:
    f.write(fingerprint)
print(f"[E2] Fingerprint saved to output/fingerprint_raw.md")
print(f"     ({len(fingerprint)} chars, {len(fingerprint.splitlines())} lines)")
