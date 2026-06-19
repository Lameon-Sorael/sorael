import pandas as pd

# 1. CSV 파일 읽기
incidents = pd.read_csv("data/raw/incidents.csv")
stations = pd.read_csv("data/raw/stations.csv")

print("=== 사건 데이터 앞 5행 ===")
print(incidents.head())

print("\n=== 데이터 정보 ===")
print(incidents.info())

print("\n=== 결측치 확인 ===")
print(incidents.isna().sum())

# 2. 상황유형별 건수 집계
type_summary = incidents.groupby("상황유형").size().reset_index(name="건수")
print("\n=== 상황유형별 건수 ===")
print(type_summary)

# 3. 역명 기준으로 역사 정보와 병합
merged = incidents.merge(stations, on="역명", how="left")
print("\n=== 병합 결과 ===")
print(merged.head())

# 4. 결과 저장
merged.to_csv("data/processed/merged_incidents.csv", index=False, encoding="utf-8-sig")
type_summary.to_csv("data/processed/type_summary.csv", index=False, encoding="utf-8-sig")

print("\n저장 완료:")
print("- data/processed/merged_incidents.csv")
print("- data/processed/type_summary.csv")
