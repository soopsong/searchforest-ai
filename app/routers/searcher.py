from abc import ABC, abstractmethod
from typing import List

class KeywordSearcher(ABC):
    @abstractmethod
    def search(self, query: str, topk: int) -> List[str]:
        pass

class ESKeywordSearcher(KeywordSearcher):
    def __init__(self, es_client, index_name: str):
        self.es = es_client
        self.index = index_name

    def search(self, query: str, topk: int) -> List[str]:
        body = {"size": topk, "query": {"multi_match": {"query": query, "fields": ["title^2","abstract"]}}}
        res = self.es.search(index=self.index, body=body)
        return [hit['_id'] for hit in res['hits']['hits']]

# VectorKeywordSearcher 예시 생략