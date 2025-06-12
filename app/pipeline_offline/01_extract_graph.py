"""
Create citation graph (NetworkX DiGraph) from:
  • data/SSN/papers.SSN.jsonl            – paper meta + TLDR + “references”
  • data/SSN/citation_relations.json     – optional global citation file
Outputs:
  • indices/graph_raw.gpickle
"""

import json, pathlib, tqdm, networkx as nx, orjson

# ─────────────────────────────────────────────
# 경로 설정 ‒ 필요하면 프로젝트 구조에 맞게 수정
PAPER_PATH = pathlib.Path("data/SSN/papers.SSN.jsonl")
CITE_PATH  = pathlib.Path("data/SSN/citation_relations.json")  # 없으면 무시
OUT_PATH   = pathlib.Path("indices/graph_raw.gpickle")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
# ─────────────────────────────────────────────

G = nx.DiGraph()

# 1) 논문 노드 + 내부 레퍼런스 엣지
for line in tqdm.tqdm(PAPER_PATH.open("rb"), desc="nodes"):
    j    = orjson.loads(line)
    pid  = j["paper_id"]              # 필드 확정

    # ────────────────────────────────
    # 1) 텍스트 뽑기 규칙
    text = (
        j.get("abstract")                              # ① abstract가 가장 짧고 요약적
        or " ".join(sum(j.get("text", []), []))[:5000] # ② (fallback) 본문 앞 5000자
        or j.get("title", "")                       # ③ (최후) 제목
    )

    G.add_node(pid, abstract=text)

    # 내부 references → edge 추가 (ref 노드 없으면 placeholder 생성)
    for ref in j.get("references", []):               # <- refs 리스트 그대로 사용
        G.add_edge(pid, ref)

# 2) 추가 citation 파일이 있으면 형식 감지 후 엣지 보강
if CITE_PATH.exists():
    with CITE_PATH.open("r", encoding="utf-8") as f:
        first = f.read(1)
        f.seek(0)

        if first == "{":                               # dict: { "pid": [...] }
            cite_dict = json.load(f)
            for src, refs in tqdm.tqdm(cite_dict.items(), desc="edges(dict)"):
                for tgt in refs:
                    G.add_edge(src, tgt)

        elif first == "[":                             # list: [{src,tgt}, …]
            for rec in tqdm.tqdm(json.load(f), desc="edges(list)"):
                G.add_edge(rec["source"], rec["target"])

        else:                                          # JSONL: one per line
            for line in tqdm.tqdm(f, desc="edges(jsonl)"):
                rec = json.loads(line)
                G.add_edge(rec["source"], rec["target"])

# 3) 저장 및 요약 로그
print(f"✔ graph → {G.number_of_nodes():,} nodes / {G.size():,} edges")
nx.write_gpickle(G, OUT_PATH)
print(f"✓ saved to {OUT_PATH}")