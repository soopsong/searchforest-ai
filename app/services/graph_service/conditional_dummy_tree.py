from typing import Dict, List, Union

TreeMapping = Dict[str, Dict[str, Union[float, str, List[Dict[str, Union[str, float, str]]]]]]

def manual_tree_with_full_values(root: str, mapping: TreeMapping):
    children = []
    for lvl1_label, data in mapping.items():
        lvl1_value = data["value"]
        lvl2_items = data["children"]

        grandchildren = []
        for lvl2 in lvl2_items:
            lvl2_label = lvl2["id"]
            lvl2_value = lvl2["value"]

            grandchildren.append({
                "id": lvl2_label,
                "context": f"{root}-{lvl1_label}-{lvl2_label}",
                "value": lvl2_value,
                "children": []
            })

        children.append({
            "id": lvl1_label,
            "context": f"{root}-{lvl1_label}",
            "value": lvl1_value,
            "children": grandchildren
        })

    return {
        "id": root,
        "context": root,
        "value": 1.0,
        "children": children
    }

# --- 수작업 예시 사전 ---
IMPORTANT_TREES = {
    "AI": manual_tree_with_full_values("AI", {
        "ML": {
            "value": 0.9,
            "children": [
                {"id": "Supervised", "value": 0.87},
                {"id": "Unsupervised", "value": 0.83},
                {"id": "Self-Supervised", "value": 0.78}
            ]
        },
        "NLP": {
            "value": 0.8,
            "children": [
                {"id": "BERT", "value": 0.76},
                {"id": "GPT", "value": 0.75},
                {"id": "Translation", "value": 0.72}
            ]
        },
        "CV": {
            "value": 0.7,
            "children": [
                {"id": "ImageNet", "value": 0.74},
                {"id": "ObjectDetection", "value": 0.71},
                {"id": "Segmentation", "value": 0.68}
            ]
        },
        "RL": {
            "value": 0.6,
            "children": [
                {"id": "Q-Learning", "value": 0.73},
                {"id": "Policy Gradient", "value": 0.70},
                {"id": "Actor Critic", "value": 0.67}
            ]
        },
        "AGI": {
            "value": 0.5,
            "children": [
                {"id": "Symbolic", "value": 0.69},
                {"id": "Neural", "value": 0.66},
                {"id": "Hybrid", "value": 0.63}
            ]
        }
    }),

    "robotics": manual_tree_with_full_values("robotics", {
        "SLAM": {
            "value": 0.9,
            "children": [
                {"id": "2D", "value": 0.87},
                {"id": "3D", "value": 0.83},
                {"id": "Visual", "value": 0.78}
            ]
        },
        "Control": {
            "value": 0.8,
            "children": [
                {"id": "PID", "value": 0.76},
                {"id": "ModelPredictive", "value": 0.73},
                {"id": "Adaptive", "value": 0.70}
            ]
        },
        "Actuators": {
            "value": 0.7,
            "children": [
                {"id": "Servo", "value": 0.74},
                {"id": "Stepper", "value": 0.71},
                {"id": "Hydraulic", "value": 0.68}
            ]
        },
        "Sensors": {
            "value": 0.6,
            "children": [
                {"id": "Lidar", "value": 0.73},
                {"id": "IMU", "value": 0.70},
                {"id": "Camera", "value": 0.67}
            ]
        },
        "Planning": {
            "value": 0.5,
            "children": [
                {"id": "A*", "value": 0.69},
                {"id": "Dijkstra", "value": 0.66},
                {"id": "RRT", "value": 0.63}
            ]
        }
    })
}


#     "software engineering": manual_tree_with_full_values("software engineering", {
#         "Testing": {
#             "value": 0.9,
#             "children": [
#                 {"id": "UnitTest", "value": 0.87},
#                 {"id": "IntegrationTest", "value": 0.83},
#                 {"id": "Fuzzing", "value": 0.78}
#             ]
#         },
#         "Versioning": {
#             "value": 0.8,
#             "children": [
#                 {"id": "Git", "value": 0.7},
#                 {"id": "SVN", "value": 0.73},
#                 {"id": "Branching", "value": 0.70}
#             ]
#         },
#         "CI/CD": {
#             "value": 0.7,
#             "children": [
#                 {"id": "Build", "value": 0.74, "example": "코드 → 실행파일로 컴파일. ex) Maven, Gradle"},
#                 {"id": "Deploy", "value": 0.71, "example": "서버로 자동 배포. ex) Jenkins + Docker"},
#                 {"id": "Monitor", "value": 0.68, "example": "운영 중 애플리케이션 상태 감시. ex) Prometheus, Grafana"}
#             ]
#         },
#         "Patterns": {
#             "value": 0.6,
#             "children": [
#                 {"id": "Singleton", "value": 0.73, "example": "인스턴스 하나만 존재. ex) Logger"},
#                 {"id": "Factory", "value": 0.70, "example": "객체 생성을 캡슐화. ex) new 대신 Factory 호출"},
#                 {"id": "Observer", "value": 0.67, "example": "상태 변화 통지. ex) UI 이벤트 리스너"}
#             ]
#         },
#         "Analysis": {
#             "value": 0.5,
#             "children": [
#                 {"id": "Static", "value": 0.69, "example": "코드 실행 없이 분석. ex) PMD, SonarQube"},
#                 {"id": "Dynamic", "value": 0.66, "example": "코드 실행 중 상태 추적. ex) Valgrind"},
#                 {"id": "Symbolic", "value": 0.63, "example": "입력값을 기호화해 실행 경로 탐색. ex) KLEE"}
#             ]
#         }
#     }),

#     "NLP": manual_tree_with_full_values("NLP", {
#         "Pretrained Models": {
#             "value": 0.9,
#             "children": [
#                 {"id": "BERT", "value": 0.87, "example": "Devlin et al., 2019. 양방향 Transformer 구조 기반 모델."},
#                 {"id": "GPT", "value": 0.84, "example": "Radford et al., 2018. 생성 중심의 언어 모델."},
#                 {"id": "T5", "value": 0.81, "example": "Raffel et al., 2020. Text-to-Text 변환 기반 모델."}
#             ]
#         },
#         "Core Tasks": {
#             "value": 0.85,
#             "children": [
#                 {"id": "Machine Translation", "value": 0.82, "example": "Bahdanau et al., 2014. Seq2Seq + Attention."},
#                 {"id": "Text Summarization", "value": 0.80, "example": "Abstractive 방식이 주요 흐름입니다."},
#                 {"id": "Question Answering", "value": 0.78, "example": "SQuAD 데이터셋이 대표적."}
#             ]
#         },
#         "Linguistic Analysis": {
#             "value": 0.8,
#             "children": [
#                 {"id": "POS Tagging", "value": 0.77, "example": "품사를 분류하는 기초 태스크."},
#                 {"id": "Dependency Parsing", "value": 0.75, "example": "단어 간의 문법적 의존 관계 분석."},
#                 {"id": "Constituency Parsing", "value": 0.73, "example": "구문 트리 분석 방식의 파싱."}
#             ]
#         },
#         "Applications": {
#             "value": 0.75,
#             "children": [
#                 {"id": "Chatbots", "value": 0.72, "example": "대화형 에이전트. 예: Siri, ChatGPT"},
#                 {"id": "Sentiment Analysis", "value": 0.70, "example": "감성 분류를 통한 사용자 반응 분석."},
#                 {"id": "Topic Modeling", "value": 0.68, "example": "LDA 등 비지도 학습 기반 주제 분석."}
#             ]
#         },
#         "Resources & Datasets": {
#             "value": 0.7,
#             "children": [
#                 {"id": "SQuAD", "value": 0.67, "example": "Stanford Question Answering Dataset."},
#                 {"id": "GLUE", "value": 0.65, "example": "General Language Understanding Evaluation benchmark."},
#                 {"id": "Wikipedia Corpus", "value": 0.63, "example": "사전학습 및 문서 분류에 활용."}
#             ]
#         }
#     }),

#     "GPT": manual_tree_with_full_values("GPT", {
#         "Model Evolution": {
#             "value": 0.9,
#             "children": [
#                 {"id": "GPT-1", "value": 0.87, "example": "Radford et al., 2018. 최초의 autoregressive Transformer 기반 모델."},
#                 {"id": "GPT-2", "value": 0.84, "example": "Radford et al., 2019. Text generation의 가능성으로 주목."},
#                 {"id": "GPT-3", "value": 0.82, "example": "Brown et al., 2020. Few-shot 능력으로 널리 사용됨."}
#             ]
#         },
#         "Applications": {
#             "value": 0.85,
#             "children": [
#                 {"id": "Code Generation", "value": 0.82, "example": "GitHub Copilot, Codex와 같은 코드 자동 생성."},
#                 {"id": "Storytelling", "value": 0.79, "example": "소설, 시나리오, 창작 글쓰기 도우미."},
#                 {"id": "Customer Support", "value": 0.76, "example": "자동화된 챗봇 응답 시스템."}
#             ]
#         },
#         "Fine-tuning & Alignment": {
#             "value": 0.8,
#             "children": [
#                 {"id": "Instruction Tuning", "value": 0.77, "example": "Supervised Fine-tuning 기반 가이드 응답 강화."},
#                 {"id": "RLHF", "value": 0.74, "example": "Human Feedback을 통한 강화학습(RL) 기반 조정."},
#                 {"id": "LoRA", "value": 0.71, "example": "Low-Rank Adapter 방식의 경량 파인튜닝."}
#             ]
#         },
#         "Ethics & Risks": {
#             "value": 0.75,
#             "children": [
#                 {"id": "Bias", "value": 0.72, "example": "학습 데이터의 편향이 응답에 반영됨."},
#                 {"id": "Hallucination", "value": 0.70, "example": "사실이 아닌 정보를 사실처럼 생성하는 문제."},
#                 {"id": "Misuse", "value": 0.68, "example": "스팸, 가짜 뉴스 생성 등 악의적 사용."}
#             ]
#         },
#         "Architectural Features": {
#             "value": 0.7,
#             "children": [
#                 {"id": "Decoder-only Transformer", "value": 0.67},
#                 {"id": "Causal Masking", "value": 0.65},
#                 {"id": "Tokenization", "value": 0.63}
#             ]
#         }
#     })

# }