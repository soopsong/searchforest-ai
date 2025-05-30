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
            "year":           2023,
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
        },
        {
            "paper_id":       "p4",
            "title":          "Dummy Paper D",
            "abstract":       "This is the abstract of dummy paper D.",
            "authors":        ["Eve", "Frank"],
            "year":           2021,
            "citation_count": 10,
            "sim_score":      0.75,
            "summary":        "이 논문은 D 기법의 유효성을 평가합니다."
        },
        {
            "paper_id":       "p5",
            "title":          "Dummy Paper E",
            "abstract":       "This is the abstract of dummy paper E.",
            "authors":        ["Grace"],
            "year":           2019,
            "citation_count": 12,
            "sim_score":      0.70,
            "summary":        "이 논문에서는 E 알고리즘을 제안합니다."
        },
        {
            "paper_id":       "p6",
            "title":          "Dummy Paper F",
            "abstract":       "This is the abstract of dummy paper F.",
            "authors":        ["Heidi"],
            "year":           2020,
            "citation_count": 8,
            "sim_score":      0.65,
            "summary":        "이 논문은 F 시스템의 성능을 분석합니다."
        },
        {
            "paper_id":       "p7",
            "title":          "Dummy Paper G",
            "abstract":       "This is the abstract of dummy paper G.",
            "authors":        ["Ivan", "Judy"],
            "year":           2022,
            "citation_count": 6,
            "sim_score":      0.60,
            "summary":        "이 논문에서는 G 모델을 제안하고 평가합니다."
        },
        {
            "paper_id":       "p8",
            "title":          "Dummy Paper H",
            "abstract":       "This is the abstract of dummy paper H.",
            "authors":        ["Kevin"],
            "year":           2021,
            "citation_count": 9,
            "sim_score":      0.55,
            "summary":        "이 논문은 H 프로토콜의 보안성을 검증합니다."
        },
        {
            "paper_id":       "p9",
            "title":          "Dummy Paper I",
            "abstract":       "This is the abstract of dummy paper I.",
            "authors":        ["Laura"],
            "year":           2023,
            "citation_count": 4,
            "sim_score":      0.50,
            "summary":        "이 논문에서는 I 프레임워크를 소개합니다."
        },
        {
            "paper_id":       "p10",
            "title":          "Dummy Paper J",
            "abstract":       "This is the abstract of dummy paper J.",
            "authors":        ["Mallory", "Niaj"],
            "year":           2018,
            "citation_count": 15,
            "sim_score":      0.45,
            "summary":        "이 논문은 J 방법론의 활용 사례를 제시합니다."
        }
    ]