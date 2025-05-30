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