from typing import Dict, List, Union

TreeMapping = Dict[str, Dict[str, Union[float, str, List[Dict[str, Union[str, float, str]]]]]]

def manual_tree_with_full_values(root: str, mapping: TreeMapping):
    children = []
    for lvl1_label, data in mapping.items():
        lvl1_value = data["value"]
        lvl1_example = data.get("example", "")
        lvl2_items = data["children"]

        grandchildren = []
        for lvl2 in lvl2_items:
            lvl2_label = lvl2["id"]
            lvl2_value = lvl2["value"]
            lvl2_example = lvl2.get("example", "")

            grandchildren.append({
                "id": lvl2_label,
                "context": f"{root}-{lvl1_label}-{lvl2_label}",
                "value": lvl2_value,
                "example": lvl2_example,
                "children": []
            })

        children.append({
            "id": lvl1_label,
            "context": f"{root}-{lvl1_label}",
            "value": lvl1_value,
            "example": lvl1_example,
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
            "example": "데이터를 기반으로 예측하거나 분류하는 알고리즘 전반. 대부분의 AI 모델이 여기에 속함.",
            "children": [
                {"id": "Supervised", "value": 0.87, "example": "정답(label)이 있는 데이터로 학습. ex) MNIST 분류"},
                {"id": "Unsupervised", "value": 0.83, "example": "정답 없이 패턴을 찾음. ex) K-Means 클러스터링"},
                {"id": "Self-Supervised", "value": 0.78, "example": "입력 자체로 정답 생성. ex) BERT 사전학습"}
            ]
        },
        "NLP": {
            "value": 0.8,
            "example": "자연어를 이해하고 생성하는 기술 분야. 번역, 요약, 대화 등 다양한 응용 포함.",
            "children": [
                {"id": "BERT", "value": 0.76, "example": "트랜스포머 기반 사전학습 모델. ex) 'Attention is All You Need'"},
                {"id": "GPT", "value": 0.75, "example": "텍스트 생성 특화 모델. ex) OpenAI GPT-3"},
                {"id": "Translation", "value": 0.72, "example": "자연어 간 기계 번역. ex) Google Translate"}
            ]
        },
        "CV": {
            "value": 0.7,
            "example": "이미지와 비디오 처리에 특화된 AI 기술. 인식, 분류, 검출 등 포함.",
            "children": [
                {"id": "ImageNet", "value": 0.74, "example": "대규모 이미지 분류 데이터셋. ex) ResNet 우승"},
                {"id": "ObjectDetection", "value": 0.71, "example": "이미지 내 객체 위치 탐지. ex) YOLOv5"},
                {"id": "Segmentation", "value": 0.68, "example": "픽셀 단위 이미지 분할. ex) U-Net"}
            ]
        },
        "RL": {
            "value": 0.6,
            "example": "보상을 극대화하기 위한 행동을 학습하는 방식. ex) 게임, 로봇 제어 등.",
            "children": [
                {"id": "Q-Learning", "value": 0.73, "example": "가치 기반 강화학습. ex) FrozenLake 예제"},
                {"id": "Policy Gradient", "value": 0.70, "example": "정책을 직접 최적화. ex) CartPole with REINFORCE"},
                {"id": "Actor Critic", "value": 0.67, "example": "정책+가치 동시 학습. ex) A3C"}
            ]
        },
        "AGI": {
            "value": 0.5,
            "example": "인간 수준의 일반 지능을 목표로 하는 연구 분야. 아직 이론적 기반 중심.",
            "children": [
                {"id": "Symbolic", "value": 0.69, "example": "논리 기반 추론 AI. ex) Prolog 시스템"},
                {"id": "Neural", "value": 0.66, "example": "뉴런 구조 모사. ex) 딥러닝 기반 지능 모델"},
                {"id": "Hybrid", "value": 0.63, "example": "심볼릭 + 뉴럴 결합. ex) Neuro-Symbolic AI"}
            ]
        }
    }),


    "robotics": manual_tree_with_full_values("robotics", {
        "SLAM": {
            "value": 0.9,
            "example": "동시 위치 추정 및 지도 작성. 로봇이 낯선 환경에서 자신 위치와 지도를 동시에 파악.",
            "children": [
                {"id": "2D", "value": 0.87, "example": "평면 공간에서의 SLAM. ex) Gmapping"},
                {"id": "3D", "value": 0.83, "example": "입체 공간 정보 활용. ex) Cartographer 3D"},
                {"id": "Visual", "value": 0.78, "example": "카메라 영상 기반 SLAM. ex) ORB-SLAM"}
            ]
        },
        "Control": {
            "value": 0.8,
            "example": "로봇 동작 제어 알고리즘. 목표에 도달하도록 움직임을 조절.",
            "children": [
                {"id": "PID", "value": 0.76, "example": "비례-적분-미분 제어. 가장 기초적인 제어 기법."},
                {"id": "ModelPredictive", "value": 0.73, "example": "모델 기반 예측 제어. 산업용 로봇에 주로 사용."},
                {"id": "Adaptive", "value": 0.70, "example": "환경 변화에 적응 가능한 제어기."}
            ]
        },
        "Actuators": {
            "value": 0.7,
            "example": "로봇을 실제로 움직이게 해주는 부품. 전기·공압·유압 방식 등이 있음.",
            "children": [
                {"id": "Servo", "value": 0.74, "example": "정밀 위치 제어용 모터. ex) Arduino Servo"},
                {"id": "Stepper", "value": 0.71, "example": "단계적으로 회전. ex) 3D 프린터 모터"},
                {"id": "Hydraulic", "value": 0.68, "example": "유압 기반 고출력 액추에이터. ex) 굴착기 암"}
            ]
        },
        "Sensors": {
            "value": 0.6,
            "example": "로봇이 환경을 인식하게 해주는 장치들. 거리, 방향, 자세 등을 측정.",
            "children": [
                {"id": "Lidar", "value": 0.73, "example": "레이저 거리 측정 센서. ex) RPLIDAR"},
                {"id": "IMU", "value": 0.70, "example": "관성 측정 장치. 가속도계 + 자이로센서 조합."},
                {"id": "Camera", "value": 0.67, "example": "영상 기반 인식. ex) OpenCV 카메라 캡처"}
            ]
        },
        "Planning": {
            "value": 0.5,
            "example": "목표 지점까지 최적 경로를 찾는 알고리즘. 로봇 자율주행의 핵심.",
            "children": [
                {"id": "A*", "value": 0.69, "example": "그래프 기반 최단경로 탐색 알고리즘. 휴리스틱 사용."},
                {"id": "Dijkstra", "value": 0.66, "example": "가중치 그래프에서 가장 짧은 경로 계산."},
                {"id": "RRT", "value": 0.63, "example": "복잡한 환경에서 무작위 트리로 경로 탐색. ex) 드론"}
            ]
        }
    }),


    "software engineering": manual_tree_with_full_values("software engineering", {
        "Testing": {
            "value": 0.9,
            "example": "소프트웨어가 제대로 동작하는지 확인하는 일련의 기법입니다.",
            "children": [
                {"id": "UnitTest", "value": 0.87, "example": "개별 함수 또는 모듈 단위 테스트. ex) JUnit"},
                {"id": "IntegrationTest", "value": 0.83, "example": "모듈 간 상호작용 검증. ex) Spring Integration Test"},
                {"id": "Fuzzing", "value": 0.78, "example": "무작위 입력으로 예외나 취약점 탐색. ex) AFL"}
            ]
        },
        "Versioning": {
            "value": 0.8,
            "example": "소스코드 변경 이력을 관리하고 협업을 가능하게 합니다.",
            "children": [
                {"id": "Git", "value": 0.76, "example": "분산형 버전관리 도구. GitHub, GitLab에서 사용."},
                {"id": "SVN", "value": 0.73, "example": "중앙집중형 버전관리 도구. 오래된 프로젝트에서 사용."},
                {"id": "Branching", "value": 0.70, "example": "개발 흐름 분리를 위한 브랜치 전략. ex) Git Flow"}
            ]
        },
        "CI/CD": {
            "value": 0.7,
            "example": "지속적인 통합과 배포 자동화로 개발 생산성을 높입니다.",
            "children": [
                {"id": "Build", "value": 0.74, "example": "코드 → 실행파일로 컴파일. ex) Maven, Gradle"},
                {"id": "Deploy", "value": 0.71, "example": "서버로 자동 배포. ex) Jenkins + Docker"},
                {"id": "Monitor", "value": 0.68, "example": "운영 중 애플리케이션 상태 감시. ex) Prometheus, Grafana"}
            ]
        },
        "Patterns": {
            "value": 0.6,
            "example": "자주 등장하는 설계 문제에 대한 재사용 가능한 해법입니다.",
            "children": [
                {"id": "Singleton", "value": 0.73, "example": "인스턴스 하나만 존재. ex) Logger"},
                {"id": "Factory", "value": 0.70, "example": "객체 생성을 캡슐화. ex) new 대신 Factory 호출"},
                {"id": "Observer", "value": 0.67, "example": "상태 변화 통지. ex) UI 이벤트 리스너"}
            ]
        },
        "Analysis": {
            "value": 0.5,
            "example": "프로그램의 성능, 버그, 취약점을 파악하기 위한 정적/동적 분석입니다.",
            "children": [
                {"id": "Static", "value": 0.69, "example": "코드 실행 없이 분석. ex) PMD, SonarQube"},
                {"id": "Dynamic", "value": 0.66, "example": "코드 실행 중 상태 추적. ex) Valgrind"},
                {"id": "Symbolic", "value": 0.63, "example": "입력값을 기호화해 실행 경로 탐색. ex) KLEE"}
            ]
        }
    }),

    "NLP": manual_tree_with_full_values("NLP", {
        "Pretrained Models": {
            "value": 0.9,
            "example": "사전 학습된 대형 언어 모델은 다양한 다운스트림 작업에 활용됩니다.",
            "children": [
                {"id": "BERT", "value": 0.87, "example": "Devlin et al., 2019. 양방향 Transformer 구조 기반 모델."},
                {"id": "GPT", "value": 0.84, "example": "Radford et al., 2018. 생성 중심의 언어 모델."},
                {"id": "T5", "value": 0.81, "example": "Raffel et al., 2020. Text-to-Text 변환 기반 모델."}
            ]
        },
        "Core Tasks": {
            "value": 0.85,
            "example": "NLP의 중심 과제들로, 다양한 응용의 기반이 됩니다.",
            "children": [
                {"id": "Machine Translation", "value": 0.82, "example": "Bahdanau et al., 2014. Seq2Seq + Attention."},
                {"id": "Text Summarization", "value": 0.80, "example": "Abstractive 방식이 주요 흐름입니다."},
                {"id": "Question Answering", "value": 0.78, "example": "SQuAD 데이터셋이 대표적."}
            ]
        },
        "Linguistic Analysis": {
            "value": 0.8,
            "example": "자연어 문장을 구성요소로 분석하여 구조를 이해하는 기술입니다.",
            "children": [
                {"id": "POS Tagging", "value": 0.77, "example": "품사를 분류하는 기초 태스크."},
                {"id": "Dependency Parsing", "value": 0.75, "example": "단어 간의 문법적 의존 관계 분석."},
                {"id": "Constituency Parsing", "value": 0.73, "example": "구문 트리 분석 방식의 파싱."}
            ]
        },
        "Applications": {
            "value": 0.75,
            "example": "NLP 기술이 상용 서비스에 적용된 사례들입니다.",
            "children": [
                {"id": "Chatbots", "value": 0.72, "example": "대화형 에이전트. 예: Siri, ChatGPT"},
                {"id": "Sentiment Analysis", "value": 0.70, "example": "감성 분류를 통한 사용자 반응 분석."},
                {"id": "Topic Modeling", "value": 0.68, "example": "LDA 등 비지도 학습 기반 주제 분석."}
            ]
        },
        "Resources & Datasets": {
            "value": 0.7,
            "example": "NLP 연구 및 학습에 활용되는 대표적인 코퍼스와 벤치마크 데이터입니다.",
            "children": [
                {"id": "SQuAD", "value": 0.67, "example": "Stanford Question Answering Dataset."},
                {"id": "GLUE", "value": 0.65, "example": "General Language Understanding Evaluation benchmark."},
                {"id": "Wikipedia Corpus", "value": 0.63, "example": "사전학습 및 문서 분류에 활용."}
            ]
        }
    }),

    "GPT": manual_tree_with_full_values("GPT", {
        "Model Evolution": {
            "value": 0.9,
            "example": "GPT 시리즈의 버전별 발전 과정을 보여줍니다.",
            "children": [
                {"id": "GPT-1", "value": 0.87, "example": "Radford et al., 2018. 최초의 autoregressive Transformer 기반 모델."},
                {"id": "GPT-2", "value": 0.84, "example": "Radford et al., 2019. Text generation의 가능성으로 주목."},
                {"id": "GPT-3", "value": 0.82, "example": "Brown et al., 2020. Few-shot 능력으로 널리 사용됨."}
            ]
        },
        "Applications": {
            "value": 0.85,
            "example": "GPT 모델이 실제로 사용되는 다양한 응용 사례들입니다.",
            "children": [
                {"id": "Code Generation", "value": 0.82, "example": "GitHub Copilot, Codex와 같은 코드 자동 생성."},
                {"id": "Storytelling", "value": 0.79, "example": "소설, 시나리오, 창작 글쓰기 도우미."},
                {"id": "Customer Support", "value": 0.76, "example": "자동화된 챗봇 응답 시스템."}
            ]
        },
        "Fine-tuning & Alignment": {
            "value": 0.8,
            "example": "GPT 모델을 특정 도메인 또는 사용자 요구에 맞추는 과정입니다.",
            "children": [
                {"id": "Instruction Tuning", "value": 0.77, "example": "Supervised Fine-tuning 기반 가이드 응답 강화."},
                {"id": "RLHF", "value": 0.74, "example": "Human Feedback을 통한 강화학습(RL) 기반 조정."},
                {"id": "LoRA", "value": 0.71, "example": "Low-Rank Adapter 방식의 경량 파인튜닝."}
            ]
        },
        "Ethics & Risks": {
            "value": 0.75,
            "example": "GPT와 같은 대형 언어 모델이 초래할 수 있는 윤리적 문제입니다.",
            "children": [
                {"id": "Bias", "value": 0.72, "example": "학습 데이터의 편향이 응답에 반영됨."},
                {"id": "Hallucination", "value": 0.70, "example": "사실이 아닌 정보를 사실처럼 생성하는 문제."},
                {"id": "Misuse", "value": 0.68, "example": "스팸, 가짜 뉴스 생성 등 악의적 사용."}
            ]
        },
        "Architectural Features": {
            "value": 0.7,
            "example": "GPT 구조와 그 작동 원리에 관한 기술적 요소들입니다.",
            "children": [
                {"id": "Decoder-only Transformer", "value": 0.67, "example": "GPT는 Transformer의 decoder 블록만 사용."},
                {"id": "Causal Masking", "value": 0.65, "example": "입력 순서를 유지하며 다음 토큰만 예측."},
                {"id": "Tokenization", "value": 0.63, "example": "Byte-Pair Encoding (BPE), SentencePiece 등 사용."}
            ]
        }
    })

}