# sum_service/dummy_data.py

def get_dummy_summary(paper_id: str) -> str:
    """
    paper_id를 받아 더미 요약문을 반환합니다.
    """
    return f"이 논문({paper_id})의 더미 요약문입니다."