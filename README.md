# h-cli

## 주요 기능

### Git 생산성 향상 (h gp)

```bash
# Git 관련 명령어 (h gp)
h gp     # 커밋 메시지 프롬프트 생성 및 저장
         # (스테이지된 파일이 없으면 에러 메시지 출력)
         # 커밋 메시지 생성을 위해 git status, staged diff, 최근 로그, 디렉토리 트리 정보를 제공합니다.

h gt     # Git 파일 목록 및 저장

h gc <repo_url> [--target <target_dir>]  # Git 저장소를 복제하고 VS Code에서 엽니다.
         # 저장소 URL을 필수로 받으며, --target 옵션을 통해 복제할 디렉토리를 지정할 수 있습니다.
         # --target 옵션이 없으면 ~/dev/<repo_name>에 복제합니다.
```

### AI 기능 (h ai)

```bash
# AI 관련 명령어 (h ai)
h ai <question>  # AI 모델에 질문하고 응답을 받습니다.
h ai             # 질문을 입력하라는 프롬프트가 표시됩니다.
```

### 기본 명령어

```bash
# 도움말 표시
h --help

# 자세한 로깅으로 실행
h --verbose

# 버전 표시
h version
```

### 파일 병합 (h m)

```bash
# 현재 디렉토리의 git-tracked 파일 병합
h m

# 특정 파일 병합
h m --file file1.txt

# 여러 파일 병합
h m --file file1.txt file2.py

# 디렉토리와 추가 파일 병합
h m --dir src --file test.txt
```

## 기능

- Git 커밋 메시지 프롬프트 (`h gp`)
- 도움말 표시 (`h --help`)
- 상세 로깅 (`h --verbose`)
- 버전 표시 (`h version`)
- AI 모델에 질문 (`h ai`)

## 개요

클린 아키텍처, 유지보수성, 확장성에 중점을 둔 CLI 도구를 구현하는 생산성 향상 프로젝트입니다.

## 기술 스택

- Python (uv, uvx 패키지 관리)
- Shell (오류 처리가 포함된 bash)
- Docker (인프라 관리)

## 프로젝트 구조

```bash
h-cli/
├── app/            # 메인 애플리케이션 코드
├── packages/       # 공유 패키지 및 유틸리티
├── infra/         # 인프라 설정
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/       # 유틸리티 스크립트
├── config/        # 설정 파일
├── tests/         # 단위 테스트
└── Makefile      # 공통 명령어
```

## 개발 가이드라인

### 아키텍처 & 원칙

- SOLID 원칙
- DRY (중복 제거)
- KISS (단순성 유지)
- YAGNI (불필요한 기능 제거)
- 클린 아키텍처 (동일 엔티티는 동일 폴더에 위치)
- MVC (Model-View-Controller) 패턴

### 개발 규칙

1. 설정 관리

   - 설정 파일 사용
   - 환경 변수 직접 사용 금지
   - 하드코딩 금지

2. 코드 품질

   - 단위 테스트 필수 (예: hello.py, hello.test.py)
   - 모든 함수에 Docstring/JSDoc 필수
   - structlog를 사용한 JSON 로깅
   - 적절한 .gitignore 관리

3. 빌드 & 개발
   - 공통 작업을 위한 Makefile
   - Docker 기반 인프라
   - 쉘 스크립트의 오류 처리

## 설치 및 사용법

### 전역 설치 (권장)

```bash
# pipx를 사용하여 전역 설치
make install-global

# 필요 시 제거
make uninstall-global
```

### 개발 설치

```bash
# uv가 설치되어 있지 않다면 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 개발을 위한 의존성 설치
make install

# 테스트 실행
make test

# 린팅 및 타입 체킹 실행
make lint
```

## AI 모듈

이 모듈은 다양한 AI 모델과 상호 작용하기 위한 인터페이스를 제공합니다.

### 사용법

AI 모듈을 사용하려면 `AIInterface`와 그 구현체를 임포트하면 됩니다.

```python
from h.utils.ai import GeminiAI, OpenAI

# Gemini 사용 예시
gemini_ai = GeminiAI()
prompt = "달에 대한 짧은 시를 써주세요."
response = gemini_ai.generate_text(prompt)
print(response)

# OpenAI 사용 예시 (플레이스홀더)
openai_ai = OpenAI()
prompt = "고양이에 대한 짧은 이야기를 써주세요."
response = openai_ai.generate_text(prompt)
print(response)
```

현재는 `GeminiAI` 구현만 사용할 수 있습니다. `OpenAI` 구현은 플레이스홀더이며 나중에 추가될 예정입니다.

`GeminiAI`를 사용하려면 `GOOGLE_API_KEY` 환경 변수를 설정해야 합니다.
