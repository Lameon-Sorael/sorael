# AI Champion Blue / AX Practice Starter

## 목표
공공데이터·가상 데이터를 활용해 AI·데이터기반행정 교육에서 필요한 기본 흐름을 연습합니다.

## 포함 기능
- CSV 읽기
- 데이터 구조 확인
- groupby 집계
- merge 병합
- 개인정보 마스킹
- 보고서 자동생성
- Streamlit 대시보드 기초

## 실행 순서

```bash
pip install -r requirements.txt
python src/lesson01_pandas_basic.py
python src/lesson02_masking.py
python src/lesson03_report_generator.py
streamlit run src/app.py
```

## 폴더 구조
- data/raw: 원본 데이터
- data/processed: 처리 결과
- src: 실행 코드
- reports: 생성 보고서
- charts: 그래프 저장
