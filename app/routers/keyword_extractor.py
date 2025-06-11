from abc import ABC, abstractmethod
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer

class KeywordExtractor(ABC):
    @abstractmethod
    def extract(self, text: str, top_n: int) -> List[str]:
        pass

    @abstractmethod
    def extract_bulk(self, texts: List[str], top_n: int) -> Dict[str, List[str]]:
        pass

class TFIDFExtractor(KeywordExtractor):
    def __init__(self):
        self.vec = TfidfVectorizer(stop_words='english', ngram_range=(1,2), max_features=5000)

    def extract(self, text: str, top_n: int) -> List[str]:
        # 단일 텍스트 처리
        return self.extract_bulk([text], top_n)[0]

    def extract_bulk(self, texts: List[str], top_n: int) -> Dict[str, List[str]]:
        X = self.vec.fit_transform(texts)
        # top_n 추출 로직 생략
        return {}