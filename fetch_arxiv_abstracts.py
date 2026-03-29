#!/usr/bin/env python3
"""
Fetch abstracts for specific arXiv IDs and save to data/arxiv_abstracts.json.
Uses id_list query (no author search) — avoids 429 rate limits.

Usage:
    python3 fetch_arxiv_abstracts.py
"""

import json, os, time, xml.etree.ElementTree as ET
import urllib.request

OUT_PATH = os.path.join(os.path.dirname(__file__), "data", "arxiv_abstracts.json")
NS = "http://www.w3.org/2005/Atom"

# ─── Paper ID lists ──────────────────────────────────────────────────────────

YEJIN_CHOI_IDS = [
    # From COLM committee dataset (2025–2026, verified)
    "2510.07105",   # Opt-ICL at LeWiDi-2025
    "2510.06084",   # Spectrum Tuning
    "2410.03868",   # Can LMs Reason about Individualistic Human Values
    "2402.05070",   # A Roadmap to Pluralistic Alignment
    # Classic commonsense reasoning papers (last/senior author)
    "1905.07830",   # HellaSwag
    "1907.10641",   # WinoGrande
    "1811.00203",   # ATOMIC
    "1906.05317",   # COMET
    "1908.05739",   # Abductive NLI (αNLI)
    "1911.11641",   # PIQA
    "1904.09728",   # SocialIQa
    "2110.07178",   # Symbolic Knowledge Distillation
    "2104.08696",   # UNICORN on RAINBOW
    "2010.05953",   # Reflective Decoding
    "2005.00557",   # CommonSense Reasoning for Natural Language Processing (tutorial)
]

GREG_DURRETT_IDS = [
    # From COLM committee dataset (verified)
    "2602.16699",   # Calibrate-Then-Act
    "2504.11381",   # RankAlign
    "2506.04721",   # Collectively Aligning LLMs
    "2505.13444",   # ChartMuseum
    "2310.16049",   # MuSR
]

# ─── Fetch function ───────────────────────────────────────────────────────────

def fetch_by_ids(id_list: list[str], batch_size: int = 5) -> list[dict]:
    """Fetch papers from arXiv API by ID list, in batches."""
    papers = []
    for i in range(0, len(id_list), batch_size):
        batch = id_list[i:i + batch_size]
        ids_str = ",".join(batch)
        url = f"https://export.arxiv.org/api/query?id_list={ids_str}&max_results={batch_size}"
        print(f"  Fetching batch {i//batch_size + 1}: {batch}")
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                xml_data = resp.read()
            root = ET.fromstring(xml_data)
            for entry in root.findall(f"{{{NS}}}entry"):
                arxiv_id_raw = entry.find(f"{{{NS}}}id").text.strip()
                arxiv_id = arxiv_id_raw.split("/abs/")[-1].split("v")[0]
                title    = entry.find(f"{{{NS}}}title").text.strip().replace("\n", " ")
                abstract = entry.find(f"{{{NS}}}summary").text.strip().replace("\n", " ")
                published = entry.find(f"{{{NS}}}published").text[:4]
                papers.append({
                    "arxiv_id": arxiv_id,
                    "title":    title,
                    "abstract": abstract,
                    "year":     int(published),
                })
        except Exception as e:
            print(f"  [Error] {e}")
        time.sleep(4)   # arXiv asks for ≥3s between requests
    return papers


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    print(f"Fetching {len(YEJIN_CHOI_IDS)} Yejin Choi papers...")
    yejin_papers = fetch_by_ids(YEJIN_CHOI_IDS)
    print(f"  Got {len(yejin_papers)} papers\n")

    print(f"Fetching {len(GREG_DURRETT_IDS)} Greg Durrett papers...")
    durrett_papers = fetch_by_ids(GREG_DURRETT_IDS)
    print(f"  Got {len(durrett_papers)} papers\n")

    data = {
        "yejin_choi":   yejin_papers,
        "greg_durrett": durrett_papers,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved to {OUT_PATH}")
    print(f"  yejin_choi:   {len(yejin_papers)} papers")
    print(f"  greg_durrett: {len(durrett_papers)} papers")
    print()
    print("Titles fetched:")
    for p in yejin_papers:
        print(f"  [{p['arxiv_id']}] {p['title'][:65]}")


if __name__ == "__main__":
    main()
