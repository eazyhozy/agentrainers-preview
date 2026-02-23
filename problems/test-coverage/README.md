# 데이터 처리 유틸리티 테스트 작성

## 개요

주어진 데이터 처리 유틸리티 소스코드(`src/data_processor.py`)에 대해 테스트를 작성하여 커버리지 목표를 달성하세요.

이 모듈은 데이터 검증(`DataValidator`), 변환/집계(`DataTransformer`), 내보내기(`DataExporter`) 클래스와 CSV 파싱, 데이터셋 병합, 중복 제거 유틸리티 함수를 제공합니다.

## 규칙

- `src/` 디렉토리의 파일은 수정할 수 없습니다
- 테스트는 `tests/test_solution.py`에 작성합니다
- `tests/test_public.py`의 예시 테스트를 참고할 수 있습니다
- `tests/test_hidden.py`는 최종 채점용 테스트입니다. 소스코드를 분석하여 직접 테스트를 작성해 보세요.
- 외부 라이브러리 사용이 금지됩니다 (pytest만 사용 가능)

## 목표

- **Line coverage** 90% 이상
- **Branch coverage** 80% 이상
- 모든 public 메서드에 대한 테스트 포함
- 에지 케이스 (빈 입력, 경계값, 에러 상황) 포함

## 테스트 실행

```bash
docker compose run --rm runner
```

## 소스코드 구조

### `DataValidator`

스키마 정의에 따라 데이터 레코드를 검증합니다.

- `validate(record)` - 단일 레코드 검증
- `validate_batch(records)` - 배치 검증

지원 타입: `string`, `integer`, `float`, `boolean`, `email`

### `DataTransformer`

데이터 변환 및 집계를 수행합니다.

- `normalize(records, fields)` - Min-max 정규화
- `aggregate(records, group_by, agg_field, agg_func)` - 그룹별 집계
- `pivot(records, index, columns, values)` - 피벗 테이블 생성
- `fill_missing(records, field, strategy, value)` - 결측값 처리

### `DataExporter`

데이터를 파일로 내보내고 통계를 생성합니다.

- `to_csv(records, filepath, delimiter)` - CSV 파일 출력
- `to_json(records, filepath, pretty)` - JSON 파일 출력
- `summary(records)` - 수치 필드 요약 통계

### 유틸리티 함수

- `parse_csv(filepath, delimiter, skip_header)` - CSV 파일 파싱
- `merge_datasets(left, right, on, how)` - 데이터셋 병합
- `deduplicate(records, key)` - 중복 제거
