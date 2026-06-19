# AI Champion Blue / AX Practice Starter

Python Streamlit 기반 데이터 대시보드 실습 프로젝트입니다.

## 목표

공공 데이터와 유사한 샘플 CSV를 사용해 데이터 읽기, 필터링, 병합, 집계, 보고서 생성, 개인정보 마스킹 흐름을 연습합니다.

## 포함 기능

- CSV 데이터 읽기
- 역명 기준 데이터 병합
- 역명/위험도 필터링
- KPI 지표 표시
- 상황유형별 그래프 표시
- 보고서 자동생성
- 필터링 결과 CSV 다운로드
- CSV 업로드 기반 개인정보 마스킹 도구
- 마스킹 결과 CSV 다운로드

## 실행 방법

```bash
pip install -r requirements.txt
py -m streamlit run src\app.py
```

## 폴더 구조

- `data/raw`: 샘플 원본 데이터
- `data/processed`: 실습 처리 결과
- `src`: Streamlit 앱과 실습 코드
- `reports`: 생성 보고서

## 개인정보 및 GitHub 업로드 주의사항

- 실제 개인정보가 포함된 CSV 파일은 GitHub에 올리지 마세요.
- Streamlit 앱에서 업로드한 CSV는 로컬에 저장하지 않고 메모리에서만 처리합니다.
- 마스킹 결과를 내려받은 뒤에도 실제 개인정보가 남아 있는지 반드시 확인하세요.
- `data/uploads/`, `.env`, `secrets.toml`, `*.key` 파일은 저장소에 커밋하지 마세요.
- 이 저장소의 샘플 CSV는 실습용 가상 데이터이며, 실제 개인정보 파일로 대체해 업로드하지 마세요.
