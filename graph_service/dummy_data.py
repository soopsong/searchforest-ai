# graph_service/dummy_data.py

def get_dummy_tree(root: str, top1: int = 5, top2: int = 3):
    """
    root 키워드 + top1, top2 파라미터를 반영한 더미 radial‐tree 반환
    """
    children = []
    # depth1: A, B 로 고정된 라벨 예시
    for label, base_sim in [("A", 0.9), ("B", 0.85)][:top1]:
        # depth2: 두 개 노드 생성
        grandchildren = [
            {
                "id": f"{root}-{label}-{i+1}",
                "value": base_sim - 0.1 * (i + 1),
                "children": []
            }
            for i in range(top2)
        ]
        children.append({
            "id":    f"{root}-{label}",
            "value": base_sim,
            "children": grandchildren
        })

    return {
        "id":       root,
        "value":    1.0,
        "children": children
    }