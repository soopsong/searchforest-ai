#!/usr/bin/env python3
"""
json_to_tree_and_kw2pid.py

– 입력:  ① your_raw_json : 처음 보내주신 {"results": …} 구조
– 출력: ② tree_dict      : manual_tree_with_full_values() 로 만든 2-depth 그래프
        ③ kw2pid_dict    : {키워드(str): [pid, …]} 형태
"""
import json
from typing import Dict, List, Union, Tuple

# ---------- 타입 & util ---------- #
TreeMapping = Dict[str, Dict[str, Union[float, List[Dict[str, Union[str, float]]]]]]

def manual_tree_with_full_values(root: str, mapping: TreeMapping):
    children = []
    for lvl1_label, data in mapping.items():
        lvl1_value = data["value"]
        lvl2_items = data["children"]

        grandchildren = []
        for lvl2 in lvl2_items:
            lvl2_label = lvl2["id"]
            lvl2_value = lvl2["value"]

            grandchildren.append({
                "id": lvl2_label,
                "context": f"{root}-{lvl1_label}-{lvl2_label}",
                "value": lvl2_value,
                "children": []
            })

        children.append({
            "id": lvl1_label,
            "context": f"{root}-{lvl1_label}",
            "value": lvl1_value,
            "children": grandchildren
        })

    return {
        "id": root,
        "context": root,
        "value": 1.0,
        "children": children
    }

# ---------- 파싱 핵심 ---------- #
def split_json(
    raw_json: str
) -> Tuple[dict, dict]:
    """
    1) 2-depth 트리(dict)
    2) kw2pid 매핑(dict)  반환
    """
    data = json.loads(raw_json)
    res = data["results"]

    root = res["root"]
    lvl1_nodes = res["children"]

    # 1-depth → 2-depth 변환용 임시 mapping
    mapping: TreeMapping = {}
    # kw2pid 누적
    kw2pid: Dict[str, List[str]] = {}

    for lvl1 in lvl1_nodes:
        lvl1_label = lvl1["id"]
        lvl1_value = lvl1["value"]
        mapping[lvl1_label] = {"value": lvl1_value, "children": []}

        # 이 예시 JSON에선 pids 가 2-depth 키워드마다 달려있음
        for lvl2 in lvl1["children"]:
            lvl2_label = lvl2["id"]
            lvl2_value = lvl2["value"]
            mapping[lvl1_label]["children"].append(
                {"id": lvl2_label, "value": lvl2_value}
            )

            # kw2pid 추가
            if "pids" in lvl2 and lvl2["pids"]:
                kw2pid[lvl2_label] = lvl2["pids"]

        # (선택) 1-depth 키워드에도 동일 pids 부여하고 싶다면 주석 해제
        # if mapping[lvl1_label]["children"]:
        #     kw2pid[lvl1_label] = mapping[lvl1_label]["children"][0]["pids"]

    tree_dict = manual_tree_with_full_values(root, mapping)
    return tree_dict, kw2pid

# ---------- 사용 예시 ---------- #
if __name__ == "__main__":
    with open("first_result.json", "r", encoding="utf-8") as f:
        raw = f.read()

    tree, kw2pid = split_json(raw)

    # 필요에 따라 파일로 저장
    with open("tree_2depth.json", "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)

    with open("kw2pid.json", "w", encoding="utf-8") as f:
        json.dump(kw2pid, f, ensure_ascii=False, indent=2)

    # 콘솔 확인
    print("=== 2-depth tree ===")
    print(json.dumps(tree, ensure_ascii=False, indent=2)[:800], "...\n")
    print("=== kw2pid ===")
    print(json.dumps(kw2pid, ensure_ascii=False, indent=2)[:800], "...")