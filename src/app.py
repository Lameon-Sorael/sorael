import pandas as pd
import streamlit as st

st.set_page_config(page_title="블루과정 AX 연습", layout="wide")

st.title("AI 챔피언 블루 과정 연습용 대시보드")
st.caption("CSV 읽기, 집계, 병합, 필터링, 보고서 생성 흐름을 연습하는 미니 프로젝트입니다.")

# 1. 데이터 읽기
incidents = pd.read_csv("data/raw/incidents.csv")
stations = pd.read_csv("data/raw/stations.csv")

# 2. 역명 기준 병합
merged = incidents.merge(stations, on="역명", how="left")

# 3. 사이드바 필터
st.sidebar.header("조회 조건")

station_list = ["전체"] + sorted(incidents["역명"].unique().tolist())
selected_station = st.sidebar.selectbox("역명", station_list)

risk_list = ["전체"] + sorted(incidents["위험도"].unique().tolist())
selected_risk = st.sidebar.selectbox("위험도", risk_list)

# 4. 필터 적용
filtered = incidents.copy()

if selected_station != "전체":
    filtered = filtered[filtered["역명"] == selected_station]

if selected_risk != "전체":
    filtered = filtered[filtered["위험도"] == selected_risk]

# 병합 데이터에도 같은 필터 적용
merged_filtered = merged.copy()

if selected_station != "전체":
    merged_filtered = merged_filtered[merged_filtered["역명"] == selected_station]

if selected_risk != "전체":
    merged_filtered = merged_filtered[merged_filtered["위험도"] == selected_risk]

# 5. 핵심 지표
st.subheader("핵심 지표")

col1, col2, col3 = st.columns(3)

total_count = len(filtered)
high_risk_count = len(filtered[filtered["위험도"] == "높음"])
station_count = filtered["역명"].nunique()

col1.metric("조회된 사건 수", total_count)
col2.metric("위험도 높음", high_risk_count)
col3.metric("관련 역 수", station_count)

# 6. 필터링 결과 표
st.subheader("필터링된 사건 데이터")
st.dataframe(filtered)
# 필터링 결과 CSV 다운로드
csv_data = filtered.to_csv(index=False, encoding="utf-8-sig")

st.download_button(
    label="필터링 결과 CSV 다운로드",
    data=csv_data,
    file_name="filtered_incidents.csv",
    mime="text/csv"
)
# 7. 상황유형별 건수
st.subheader("상황유형별 건수")

type_summary = filtered.groupby("상황유형").size().reset_index(name="건수")

if len(type_summary) > 0:
    st.bar_chart(type_summary.set_index("상황유형"))
else:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")

# 8. 역명 기준 병합 결과
st.subheader("역명 기준 병합 결과")
st.dataframe(merged_filtered)

# 9. 보고서 자동생성
st.subheader("보고서 자동생성")

if len(filtered) > 0:
    selected_index = st.selectbox("보고서를 생성할 행 번호", filtered.index)
    row = incidents.loc[selected_index]

    report = f"""[상황보고]

발생일시: {row['발생일시']}
발생장소: {row['역명']} {row['위치']}
상황유형: {row['상황유형']}
위험도: {row['위험도']}
조치결과: {row['조치결과']}
비고: {row['비고']}

[보고문]
{row['발생일시']}경 {row['역명']}역 {row['위치']}에서 {row['상황유형']} 관련 상황이 발생하였으며,
위험도는 {row['위험도']} 수준으로 판단됨.
현장에서는 {row['조치결과']} 조치를 실시하였고,
특이사항은 다음과 같음: {row['비고']}.
"""
    st.text_area("생성 보고서", report, height=300)
else:
    st.info("보고서를 생성할 데이터가 없습니다.")