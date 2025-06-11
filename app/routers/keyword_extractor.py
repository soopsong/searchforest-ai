from abc import ABC, abstractmethod
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer


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
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000
        )
        self._fitted = False

    def extract_bulk(self, texts: List[str], top_n: int) -> Dict[str, List[str]]:
        """
        전체 텍스트 리스트를 기반으로 TF-IDF 피팅 후, 각 텍스트별 상위 키워드 추출
        """
        self.vectorizer.fit(texts)
        self._fitted = True
        tfidf_matrix = self.vectorizer.transform(texts)
        feature_names = self.vectorizer.get_feature_names_out()

        result = {}
        for i, row in enumerate(tfidf_matrix):
            row_data = row.toarray().flatten()
            top_indices = row_data.argsort()[::-1][:top_n]
            top_keywords = [feature_names[idx] for idx in top_indices if row_data[idx] > 0]
            result[texts[i]] = top_keywords

        return result

    def extract(self, text: str, top_n: int) -> List[str]:
        """
        단일 텍스트에서 키워드 추출
        (주의: 처음 호출 시엔 자동으로 fit 수행)
        """
        if not self._fitted:
            self.vectorizer.fit([text])
            self._fitted = True

        tfidf_matrix = self.vectorizer.transform([text])
        feature_names = self.vectorizer.get_feature_names_out()
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

