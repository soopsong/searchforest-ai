# 🤖 SearchForest-AI

**Multilingual embedding-based keyword expansion engine**  
중앙대학교 캡스톤디자인 팀 **숲송 (Soopsong)** 이 개발한 **AI 연관검색어 추론 시스템**입니다.  
이 저장소는 **AI 모델 로직 및 임베딩 추론 모듈 전용 레포지토리**입니다.  
프론트엔드 및 백엔드는 별도 레포로 분리되어 있습니다.

---

## 🧠 What’s inside

- 🔎 [M3E-base](https://huggingface.co/moka-ai/m3e-base) 모델 기반 키워드 임베딩
- 🧠 Cosine similarity 기반 유사 키워드 Top-N 추출
- 🌿 키워드 임베딩 추론 API 제공 (서빙용)
- ⚡ 추후 FAISS 기반 고속 검색 기능 연동 예정

---

## 📂 Repository Structure

searchforest-ai/
├── model/            # M3E 모델 로딩 및 추론
├── utils/            # 임베딩 계산, 유사도 함수
├── test_data/        # 테스트용 키워드 샘플
├── scripts/          # 추론 테스트용 스크립트
└── README.md

---

## ⚙️ Tech Stack

- Python 3.10+
- HuggingFace Transformers
- M3E-base (Multilingual Embedding)
- Numpy / Scikit-learn
- (Optional) FAISS (추후 추가 예정)

---

## 🧑‍💻 팀 숲송 (Team Soopsong)

| 이름 | 역할 | GitHub |
|------|------|--------|
| 송정현 | PM / 프론트엔드 | [@katie424](https://github.com/katie424) |
| 임민혁 | 백엔드 | [@mh991221](https://github.com/mh991221) |
| 임지민 | AI 모델 / 데이터 | [@hyun-hyang](https://github.com/hyun-hyang) |

> 🙌 중앙대학교 소프트웨어학부 2025 캡스톤 프로젝트

---

## 🔗 Related Repositories

- 🖥️ [searchforest-fe](https://github.com/soopsong/searchforest-fe): 사용자 인터페이스 (React)
- ⚙️ [searchforest-be](https://github.com/soopsong/searchforest-be): API 서버 및 라우팅 (FastAPI)

> 각 컴포넌트는 독립적으로 개발되며, 이 레포는 **AI 모델 추론 전용**입니다.

---

## 📄 License

MIT License © 2025 Soopsong Team
