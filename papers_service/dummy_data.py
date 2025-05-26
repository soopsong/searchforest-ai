# papers_service/dummy_data.py

def get_dummy_papers():
    """
    더미 논문 리스트 반환
    """
    return [
        {
            "paper_id":       "p1",
            "title":          "Dummy Paper A",
            "abstract":       "This is the abstract of dummy paper A.",
            "authors":        ["Alice"],
            "year":           2021,
            "citation_count": 5,
            "sim_score":      0.90,
            "summary":        "이 논문은 A에 대해 간략히 설명합니다."
        },
        {
            "paper_id":       "p2",
            "title":          "Dummy Paper B",
            "abstract":       "This is the abstract of dummy paper B.",
            "authors":        ["Bob", "Carol"],
            "year":           2020,
            "citation_count": 3,
            "sim_score":      0.85,
            "summary":        "이 논문은 B의 주요 기여를 요약합니다."
        },
        {
            "paper_id":       "p3",
            "title":          "Dummy Paper C",
            "abstract":       "This is the abstract of dummy paper C.",
            "authors":        ["Dave"],
            "year":           2022,
            "citation_count": 7,
            "sim_score":      0.80,
            "summary":        "이 논문에서는 C를 제안하고 실험 결과를 제공합니다."
        }
    ]