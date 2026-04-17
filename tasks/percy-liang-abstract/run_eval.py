"""
Step 5: Generate abstracts (zero-shot + skill-guided) and compute ROUGE.
"""
import os, re
import requests
from rouge_score import rouge_scorer

API_KEY = os.environ["OPENROUTER_API_KEY"]
MODEL   = "openai/gpt-5.4-pro"
BASE    = os.path.dirname(os.path.abspath(__file__))

def llm(system: str, user: str, temperature: float = 0.3) -> str:
    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}",
                 "Content-Type": "application/json"},
        json={"model": MODEL,
              "temperature": temperature,
              "messages": [{"role": "system", "content": system},
                           {"role": "user",   "content": user}]},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()

def load(path):
    with open(path) as f: return f.read()

def strip_latex(text: str) -> str:
    """Normalize LaTeX notation for fair ROUGE comparison."""
    text = re.sub(r'\\cite[tp]?\*?\{[^}]+\}', '', text)
    text = re.sub(r'\$([^$]+)\$', r'\1', text)  # strip $ delimiters
    text = re.sub(r'\\times', '×', text)
    text = re.sub(r'\\%', '%', text)
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', ' ', text)
    text = re.sub(r'[{}$\\]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# ─── Load inputs ─────────────────────────────────────────────────────────────
intro    = load(f"{BASE}/test/paper3_megadocs_intro.md")
gold_raw = load(f"{BASE}/test/paper3_megadocs_abstract_gold.md")
skill    = load(f"{BASE}/output/percy-liang-abstract-skill.md")

task_instruction = """Given the Introduction section of an ML research paper on data-efficient
language model pre-training, write an abstract for this paper.

Output ONLY the abstract text. No preamble, no explanation."""

# ─── Zero-shot generation ─────────────────────────────────────────────────────
print("[1/3] Generating zero-shot abstract...")
zeroshot = llm(
    system="You are an expert ML researcher writing paper abstracts.",
    user=f"{task_instruction}\n\n{intro}",
)
with open(f"{BASE}/output/zeroshot_abstract.txt", "w") as f:
    f.write(zeroshot)
print(f"      Zero-shot abstract: {len(zeroshot.split())} words")

# ─── Skill-guided generation ──────────────────────────────────────────────────
print("[2/3] Generating skill-guided abstract...")
skilled = llm(
    system=skill,
    user=f"{task_instruction}\n\n{intro}",
)
with open(f"{BASE}/output/skilled_abstract.txt", "w") as f:
    f.write(skilled)
print(f"      Skill-guided abstract: {len(skilled.split())} words")

# ─── ROUGE evaluation ─────────────────────────────────────────────────────────
print("[3/3] Computing ROUGE scores...")

gold = strip_latex(gold_raw)
zs   = strip_latex(zeroshot)
sk   = strip_latex(skilled)

scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
zs_scores = scorer.score(gold, zs)
sk_scores = scorer.score(gold, sk)

print("\n" + "="*60)
print("  ROUGE Evaluation: Percy-Liang Abstract Generation")
print("="*60)
print(f"\n{'Metric':<12} {'Zero-shot':>12} {'Skill-guided':>14} {'Delta':>10}")
print("-"*50)
for key, label in [('rouge1','ROUGE-1'), ('rouge2','ROUGE-2'), ('rougeL','ROUGE-L')]:
    zf = zs_scores[key].fmeasure
    sf = sk_scores[key].fmeasure
    delta = sf - zf
    sign = "+" if delta >= 0 else ""
    print(f"{label:<12} {zf:>12.4f} {sf:>14.4f} {sign+f'{delta:.4f}':>10}")

print("-"*50)
print(f"\nGold abstract ({len(gold.split())} words after stripping):")
print(f"  {gold[:200]}...")
print(f"\nZero-shot ({len(zs.split())} words):")
print(f"  {zs[:200]}...")
print(f"\nSkill-guided ({len(sk.split())} words):")
print(f"  {sk[:200]}...")
