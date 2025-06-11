from abc import ABC, abstractmethod
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List, Dict, Tuple


class KeywordExtractor(ABC):
    """
    키워드 추출기 추상 클래스.
    - extract: 단일 텍스트에서 상위 키워드 추출
    - extract_bulk: 복수 텍스트에서 상위 키워드 추출 (각 텍스트별 반환)
    """
    @abstractmethod
    def extract(self, text: str, top_n: int) -> List[str]:
        pass

    @abstractmethod
    def extract_bulk(self, texts: List[str], top_n: int) -> Dict[str, List[str]]:
        pass


class TFIDFExtractor(KeywordExtractor):
    """
    TF-IDF 기반 키워드 추출기
    - 영어 불용어 제거
    - 유니그램 + 바이그램 사용
    """
    def __init__(self):
        # max_df: 전체 문서의 80% 이상에 등장하는 단어는 무시
        # min_df=1: 최소 1개 문서에만 등장해도 어휘에 포함
        # stop_words=None: 기본 불용어만 사용
        self.vectorizer = TfidfVectorizer(max_df=0.8, min_df=1, stop_words=None)

    def extract_bulk(self, texts: List[str], top_n: int = 5) -> Dict[str, List[tuple]]:
        """
        texts: hop1_texts or hop2_texts
        반환값: { text: [(keyword, score), ...] }
        """
        results: Dict[str, List[tuple]] = {}
        if not texts:
            return {t: [] for t in texts}

        try:
            X = self.vectorizer.fit_transform(texts)
        except ValueError as e:
            # 빈 어휘집 발생 시, 모두 빈 리스트로 넘김
            return {t: [] for t in texts}

        # sklearn 버전에 따라 호출 메서드 분기
        feature_names = None
        if hasattr(self.vectorizer, "get_feature_names_out"):
            feature_names = self.vectorizer.get_feature_names_out()
        else:
            feature_names = self.vectorizer.get_feature_names()

        # 각 문서마다 TF-IDF 상위 top_n 키워드 추출
        for row_idx, vec in enumerate(X):
            row = vec.toarray().flatten()
            # (단어, 점수) 쌍 리스트
            pairs = [(feature_names[i], float(row[i])) for i in row.argsort()[::-1] if row[i] > 0]
            results[texts[row_idx]] = pairs[:top_n]

        return results

    def extract(self, text: str, top_n: int) -> List[str]:
        """
        단일 텍스트에서 키워드 추출
        (주의: 처음 호출 시엔 자동으로 fit 수행)
        """
        if not self._fitted:
            self.vectorizer.fit([text])
            self._fitted = True
            
        tfidf_matrix = self.vectorizer.transform([text])

        try:
            feature_names = self.vectorizer.get_feature_names_out()
        except AttributeError:
            feature_names = self.vectorizer.get_feature_names()

        row = tfidf_matrix.toarray().flatten()
        top_indices = row.argsort()[::-1][:top_n]
        return [feature_names[idx] for idx in top_indices if row[idx] > 0]


if __name__ == "__main__":
    texts = [
        "deep learning improves machine learning techniques",
        "machine learning and deep learning are important in AI",
        "graph neural networks are part of deep learning"
    ]

    extractor = TFIDFExtractor()
    results = extractor.extract_bulk(texts, top_n=3)

    for text, keywords in results.items():
        print(f"[{text[:30]}...] → {keywords}")

