<div align="center">

# 🚀 **h-cli**

**개발자 생산성 향상을 위한 CLI 도구**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)  
[![Python](https://img.shields.io/badge/Python-3.11+-brightgreen.svg)](https://www.python.org/)  
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

---

## ✨ **주요 기능**

### **Git 생산성 향상**

- **`h gp`**: Git 커밋 메시지 프롬프트 생성 및 저장
- **`h gt`**: Git 파일 목록 조회 및 저장
- **`h gc <repo_url>`**: Git 저장소 복제 및 VS Code에서 열기

### **AI 기능**

- **`h ai <question>`**: AI 모델에 질문하고 응답 받기
- **`h ai`**: 질문 입력 프롬프트 제공

### **파일 병합**

- **`h m`**: Git-tracked 파일 병합
- **`h m --file <file>`**: 특정 파일 병합
- **`h m --docs`**: 마크다운 파일 포함 병합

병합된 파일의 시작 부분에 디렉토리 구조가 표시되어 프로젝트 구조를 빠르게 파악할 수 있습니다.

예시:

```bash
$ h m
```

출력:

```
## Directory Structure
file1.txt
file2.py
scripts/
    script1.sh
    script2.sh

## File: file1.txt
File 1 content

## File: file2.py
File 2 content
```

디렉토리 구조는 Git 어댑터의 `get_directory_tree` 함수를 사용하여 생성되며, 최대 3단계 깊이까지 표시됩니다.

### **기본 명령어**

- **`h --help`**: 도움말 표시
- **`h --verbose`**: 상세 로깅 활성화
- **`h version`**: 버전 정보 표시

---

## 🛠️ **기술 스택**

- **언어**: Python 3.11+
- **패키지 관리**: `uv`, `uvx`
- **CLI 프레임워크**: `Typer`
- **로깅**: `structlog`
- **AI 통합**: Google Gemini
- **터미널 출력**: `Rich`
- **인프라**: Docker

---

## 📂 **프로젝트 구조**

```bash
h-cli/
├── app/            # 애플리케이션 코드
│   ├── adapters/   # 외부 시스템 인터페이스
│   ├── core/       # 핵심 비즈니스 로직
│   ├── frameworks/ # 프레임워크 관련 코드
│   └── tools/      # 유틸리티 함수
├── packages/       # 공유 패키지
├── infra/          # 인프라 설정
├── scripts/        # 유틸리티 스크립트
├── config/         # 설정 파일
├── tests/          # 단위 테스트
└── Makefile        # 공통 명령어
```

---

## 🚀 **시작하기**

### **전역 설치 (권장)**

```bash
make install-global
```

### **개발 환경 설정**

```bash
# uv 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 의존성 설치
make setup

# 테스트 실행
make test

# 린팅 및 포맷팅
make lint
```

---

## 🤖 **AI 모듈**

Google Gemini를 활용한 AI 기능을 제공합니다.

### **사용 예시**

```python
from h.utils.ai import GeminiAI

# Gemini 초기화
gemini_ai = GeminiAI(api_key="your-api-key")

# 질문 및 응답
response = gemini_ai.generate_text("달에 대한 짧은 시를 써주세요.")
print(response)
```

---

## 🎯 **개발 원칙**

- **SOLID 원칙** 준수
- **DRY (Don't Repeat Yourself)**
- **KISS (Keep It Simple, Stupid)**
- **YAGNI (You Aren't Gonna Need It)**
- **클린 아키텍처** 적용
- **MVC 패턴** 활용

---

## 🧪 **테스트**

프로젝트는 `pytest`를 사용하여 테스트가 작성되어 있습니다.

```bash
make test
```

<div align="center">

**h-cli**로 더 효율적인 개발을 경험해보세요! 🚀

</div>
