def get_dummy_tree(root: str, top1: int = 5, top2: int = 3):
    """
    root 키워드 + top1, top2 파라미터를 반영한 더미 radial-tree 반환
    depth1: top1 개수, depth2: top2 개수로 구성됩니다.
    """
    children = []

    # depth1: top1개의 자식 노드 생성
    for i in range(top1):
        # 라벨은 A, B, C, ... 또는 번호로 생성
        label = chr(ord('A') + i) if i < 26 else str(i+1)
        # base_sim: 0.9에서 일정 간격으로 감소
        base_sim = round(1.0 - (i + 1) * (0.1), 4)

        # depth2: 각 depth1 노드에 top2 개수만큼 자식 생성
        grandchildren = []
        for j in range(top2):
            child_label = f"{root}-{label}-{j+1}"
            # sim value: base_sim에서 0.05씩 감소
            child_sim = round(base_sim - (j + 1) * 0.05, 4)
            grandchildren.append({
                "id": child_label,
                "value": child_sim,
                "children": []
            })

        children.append({
            "id": f"{root}-{label}",
            "value": base_sim,
            "children": grandchildren
        })

    # 루트 노드 반환
    return {
        "id": root,
        "value": 1.0,
        "children": children
    }

# --- 기본 더미 트리 생성기 (context 포함) ---
def get_dummy_tree_with_context(root: str, top1: int = 5, top2: int = 3):
    children = []
    for i in range(top1):
        label = chr(ord('A') + i) if i < 26 else str(i+1)
        base_sim = round(1.0 - (i + 1) * 0.1, 4)
        grandchildren = []
        for j in range(top2):
            child_label = f"{label}-{j+1}"
            full_context = f"{root}-{label}-{j+1}"
            child_sim = round(base_sim - (j + 1) * 0.05, 4)
            grandchildren.append({
                "id": child_label,
                "context": full_context,
                "value": child_sim,
                "children": []
            })
        children.append({
            "id": label,
            "context": f"{root}-{label}",
            "value": base_sim,
            "children": grandchildren
        })
    return {
        "id": root,
        "context": root,
        "value": 1.0,
        "children": children
    }

def get_dummy_tree_with_context_and_example(root: str, top1: int = 5, top2: int = 3):
    """
    root 키워드를 중심으로 top1개의 1-depth와 각 1-depth마다 top2개의 2-depth를 생성한 더미 트리를 반환.
    각 노드에는 context, value, example 필드가 포함됨.
    """
    children = []

    for i in range(top1):
        label = chr(ord('A') + i) if i < 26 else str(i + 1)
        base_sim = round(1.0 - (i + 1) * 0.1, 4)
        lvl1_id = label
        lvl1_context = f"{root}-{label}"
        lvl1_example = f"{root} 분야의 하위 주제 {label}에 대한 간단한 설명입니다."

        grandchildren = []
        for j in range(top2):
            lvl2_id = f"{label}-{j + 1}"
            lvl2_context = f"{root}-{label}-{j + 1}"
            lvl2_value = round(base_sim - (j + 1) * 0.05, 4)
            lvl2_example = f"{label} 세부 주제 {j + 1}에 대한 예시 설명입니다."

            grandchildren.append({
                "id": lvl2_id,
                "context": lvl2_context,
                "value": lvl2_value,
                "example": lvl2_example,
                "children": []
            })

        children.append({
            "id": lvl1_id,
            "context": lvl1_context,
            "value": base_sim,
            "example": lvl1_example,
            "children": grandchildren
        })

    return {
        "id": root,
        "context": root,
        "value": 1.0,
        "example": f"{root}라는 주제를 중심으로 확장된 키워드 구조입니다.",
        "children": children
    }


