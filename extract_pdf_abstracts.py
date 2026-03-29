#!/usr/bin/env python3
"""
Extract title, abstract, and introduction opening from arXiv PDFs.
Saves to data/arxiv_abstracts.json for use by build_abstract_skill.py.

Uses PyMuPDF (fitz) for text extraction.
"""

import json
import os
import re
import fitz  # PyMuPDF

DATA_DIR  = os.path.join(os.path.dirname(__file__), "data")
PDF_DIR   = os.path.join(DATA_DIR, "arxiv_pdfs")
OUT_PATH  = os.path.join(DATA_DIR, "arxiv_abstracts.json")

# ─── Paper assignment ─────────────────────────────────────────────────────────
# arXiv ID prefix → researcher (strip version suffix like "v2")

YEJIN_CHOI_IDS = {
    "1811.00203", "1904.09728", "1905.07830", "1907.10641",
    "1908.05739", "1911.11641", "2005.00557", "2010.05953",
    "2104.08696", "2110.07178", "2402.05070", "2410.03868",
    "2510.06084", "2510.07105",
}
GREG_DURRETT_IDS = {
    "2310.16049", "2504.11381", "2505.13444", "2506.04721", "2602.16699",
}

# Manual title corrections for papers where small-caps / truncation breaks extraction
TITLE_CORRECTIONS = {
    "1907.10641": "WinoGrande: An Adversarial Winograd Schema Challenge at Scale",
    "1908.05739": "Abductive Commonsense Reasoning",
    "2310.16049": "MuSR: Testing the Limits of Chain-of-Thought with Multistep Soft Reasoning",
    "2510.06084": "Spectrum Tuning: Post-Training for Distributional Coverage and In-Context Steerability",
}


def arxiv_id_from_filename(fname: str) -> str:
    """'1905.07830v1.pdf' → '1905.07830'"""
    base = os.path.splitext(fname)[0]   # strip .pdf
    return re.sub(r'v\d+$', '', base)   # strip version


ARXIV_STAMP_RE = re.compile(
    r'arXiv:|^\s*\[(?:cs|stat|math|econ|physics|q-bio)\.'  # category tags
    r'|^\s*\d{1,2}\s+\w{3}\s+\d{4}\s*$'                   # date-only lines
    r'|^\s*\d{4}\.\d{4,5}',                                # bare arXiv ID
    re.IGNORECASE | re.MULTILINE
)

# Keywords that should appear in the abstract of an NLP/AI paper
NLP_KEYWORDS = {
    "language", "model", "neural", "learning", "nlp", "commonsense",
    "reasoning", "generation", "text", "dataset", "benchmark", "llm",
    "transformer", "pretraining", "training", "task", "evaluation",
    "alignment", "fine-tuning", "token", "inference",
}


def extract_title(page) -> str:
    """Return the paper title from page 1.
    Skips the arXiv preprint stamp (y < 55 points) and metadata lines.
    Looks for the largest-font text in the main body area.
    """
    result = page.get_text("dict")
    spans = []
    for block in result.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            # Skip arXiv stamp area at top margin (y0 < 55 pt)
            y0 = line["bbox"][1]
            if y0 < 55:
                continue
            for span in line.get("spans", []):
                text = span["text"].strip()
                if not text or len(text) < 3:
                    continue
                # Skip arXiv stamp patterns
                if ARXIV_STAMP_RE.search(text):
                    continue
                spans.append((span["size"], y0, text))

    if not spans:
        return ""

    max_size = max(s[0] for s in spans)
    # Collect all spans at ~max size (within 15% of max)
    title_spans = [s[2] for s in sorted(spans, key=lambda x: x[1])
                   if s[0] >= max_size * 0.85]

    # Take first 6 spans (title typically spans 1-4 lines)
    title = " ".join(title_spans[:6]).strip()
    # Remove any residual arXiv category in brackets at end
    title = re.sub(r'\s*\[(?:cs|stat|math)\.\w+\].*$', '', title).strip()
    return title[:300]


def is_cs_paper(abstract: str) -> bool:
    """Return True if the abstract looks like a CS/NLP/AI paper."""
    lower = abstract.lower()
    hits = sum(1 for kw in NLP_KEYWORDS if kw in lower)
    return hits >= 3


# ─── Abstract extraction ──────────────────────────────────────────────────────

def extract_abstract(text: str) -> str:
    """
    Extract text between 'Abstract' heading and next section heading
    from page 1 plain text.
    """
    # Pattern: "Abstract" on its own line (or with newline) followed by body
    pattern = re.compile(
        r'(?i)(?:^|\n)\s*abstract\s*\n([\s\S]+?)(?=\n\s*(?:'
        r'1[\s\.]|introduction|keywords|index terms|acm|ccs'
        r'))',
        re.IGNORECASE | re.MULTILINE
    )
    m = pattern.search(text)
    if m:
        raw = m.group(1)
    else:
        # Fallback: look for "Abstract" anywhere and take next 600 chars
        idx = text.lower().find("abstract")
        if idx == -1:
            return ""
        raw = text[idx + 8: idx + 1200]

    # Clean: collapse hyphenated line breaks, normalize whitespace
    raw = re.sub(r'-\n', '', raw)
    raw = re.sub(r'\n+', ' ', raw)
    raw = re.sub(r'\s{2,}', ' ', raw)
    return raw.strip()[:1500]


# ─── Introduction extraction ─────────────────────────────────────────────────

def extract_intro(doc) -> str:
    """
    Extract the full introduction section from pages 1–5.
    Strategy: find 'introduction' heading, then take up to 1500 words.
    Does NOT rely on detecting the next section header (too fragile).
    """
    combined = ""
    for i in range(min(5, len(doc))):
        combined += doc[i].get_text("text") + "\n"

    # Clean hyphenated line breaks first (common in multi-column PDFs)
    combined = re.sub(r'-\n', '', combined)

    # Find Introduction heading (handles "1 Introduction", "1. Introduction",
    # bare "Introduction", Roman numeral "I. Introduction")
    intro_pattern = re.compile(
        r'(?i)(?:^|\n)\s*(?:[1I][\s\.]?\s*)?introduction\s*\n',
        re.MULTILINE
    )
    m = intro_pattern.search(combined)
    if m:
        raw = combined[m.end():]
    else:
        # Fallback: find "introduction" anywhere and take text after it
        idx = combined.lower().find("introduction")
        if idx == -1:
            return ""
        raw = combined[idx + 12:]

    # Normalize whitespace
    raw = re.sub(r'\n+', ' ', raw)
    raw = re.sub(r'\s{2,}', ' ', raw)

    # Take up to 1500 words (full introduction for most papers)
    words = raw.split()
    return " ".join(words[:1500])


# ─── Year extraction from filename / first page ───────────────────────────────

def estimate_year(arxiv_id: str) -> int:
    """Estimate publication year from arXiv ID prefix (YYMM.xxxxx)."""
    yymm = arxiv_id.split(".")[0]
    if len(yymm) == 4:  # format YYMM
        yy = int(yymm[:2])
        return (2000 + yy) if yy <= 30 else (1900 + yy)
    return 2020  # fallback


# ─── Main ─────────────────────────────────────────────────────────────────────

def process_pdf(pdf_path: str, arxiv_id: str) -> dict | None:
    try:
        doc = fitz.open(pdf_path)
        page1 = doc[0]
        page1_text = page1.get_text("text")

        title    = TITLE_CORRECTIONS.get(arxiv_id) or extract_title(page1)
        # Clean stray leading junk (e.g. "-)A " or ": ")
        title    = re.sub(r'^[\W_]+', '', title).strip()
        abstract = extract_abstract(page1_text)
        intro    = extract_intro(doc)
        year     = estimate_year(arxiv_id)

        if not abstract:
            print(f"  [warn] No abstract found: {arxiv_id}")
            return None

        if not is_cs_paper(abstract):
            print(f"  [skip] Not a CS/NLP paper (wrong PDF?): {arxiv_id}")
            print(f"         Abstract preview: {abstract[:120]}")
            return None

        return {
            "arxiv_id": arxiv_id,
            "title":    title,
            "abstract": abstract,
            "intro":    intro,
            "year":     year,
        }
    except Exception as e:
        print(f"  [error] {arxiv_id}: {e}")
        return None


def main():
    pdf_files = sorted(f for f in os.listdir(PDF_DIR) if f.endswith(".pdf"))
    print(f"Found {len(pdf_files)} PDFs in {PDF_DIR}\n")

    yejin_papers   = []
    durrett_papers = []
    unknown = []

    for fname in pdf_files:
        arxiv_id = arxiv_id_from_filename(fname)
        pdf_path = os.path.join(PDF_DIR, fname)

        print(f"Processing {fname} → {arxiv_id}")
        paper = process_pdf(pdf_path, arxiv_id)
        if paper is None:
            continue

        if arxiv_id in YEJIN_CHOI_IDS:
            yejin_papers.append(paper)
            print(f"  [Yejin Choi]  title: {paper['title'][:60]}")
            print(f"  abstract len: {len(paper['abstract'])} chars")
        elif arxiv_id in GREG_DURRETT_IDS:
            durrett_papers.append(paper)
            print(f"  [Greg Durrett] title: {paper['title'][:60]}")
            print(f"  abstract len: {len(paper['abstract'])} chars")
        else:
            unknown.append(arxiv_id)
            print(f"  [UNASSIGNED] {arxiv_id}")
        print()

    if unknown:
        print(f"Warning: {len(unknown)} unassigned papers: {unknown}")

    data = {
        "yejin_choi":   yejin_papers,
        "greg_durrett": durrett_papers,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"{'='*60}")
    print(f"Saved {OUT_PATH}")
    print(f"  yejin_choi:   {len(yejin_papers)} papers")
    print(f"  greg_durrett: {len(durrett_papers)} papers")

    # Quick quality check
    print("\nAbstract length check (Yejin Choi):")
    for p in yejin_papers:
        flag = " ✗ SHORT" if len(p["abstract"]) < 200 else ""
        print(f"  [{p['arxiv_id']}] {len(p['abstract'])} chars{flag}")


if __name__ == "__main__":
    main()
