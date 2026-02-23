# Agentrainers

AI 도구와 협업하여 실무 스타일 문제를 푸는 트레이닝 플랫폼.

## 문제 목록

| # | 문제 | 유형 | 난이도 | 언어 | 예상 시간 |
|---|------|------|--------|------|-----------|
| 1 | [api-endpoints](problems/api-endpoints/) | 구현 | Medium | Python | 45-60분 |
| 2 | [code-refactoring](problems/code-refactoring/) | 리팩토링 | Medium | Python | 45분 |
| 3 | [test-coverage](problems/test-coverage/) | 테스트 작성 | Medium | Python | 45분 |

## 사용법

[Docker](https://www.docker.com/products/docker-desktop/)만 설치되어 있으면 됩니다.

```bash
git clone https://github.com/eazyhozy/agentrainers-preview.git
cd agentrainers-preview

# 1. 문제 선택
cd problems/api-endpoints

# 2. 문제 설명 읽기 (README.md)

# 3. AI 도구를 활용하여 풀기
#    (Claude, Cursor, Copilot 등)

# 4. 테스트 실행
docker compose run --rm runner
```

각 문제 디렉터리 구성:
- `README.md` — 문제 설명 및 요구사항
- `src/` — 스타터 코드 (작업 공간)
- `tests/test_public.py` — 공개 테스트 (직접 확인 가능)
- `tests/test_hidden.py` — 비공개 테스트 (최종 채점용)
- `docker-compose.yml` — 테스트 실행 환경 (로컬 설정 불필요)

## 피드백

문제 품질, 난이도, AI 도구 활용 경험에 대한 피드백을 환영합니다.

[Feedback Form](https://forms.gle/dNg3xpXuNP6k82vLA)
