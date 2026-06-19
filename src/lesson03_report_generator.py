import pandas as pd

def make_report(row):
    return f"""[상황보고]

1. 발생일시
- {row['발생일시']}

2. 발생장소
- {row['역명']} {row['위치']}

3. 상황유형 및 위험도
- {row['상황유형']} / {row['위험도']}

4. 조치결과
- {row['조치결과']}

5. 비고
- {row['비고']}
"""

incidents = pd.read_csv("data/raw/incidents.csv")

reports = []
for idx, row in incidents.iterrows():
    reports.append(make_report(row))

with open("reports/incident_reports.txt", "w", encoding="utf-8") as f:
    f.write("\n" + "=" * 60 + "\n".join(reports))

print("저장 완료: reports/incident_reports.txt")
print(reports[0])
