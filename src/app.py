from io import BytesIO

import pandas as pd
import streamlit as st

from masking_utils import mask_dataframe, read_csv_with_korean_encoding


GITHUB_URL = "https://github.com/Lameon-Sorael/sorael"


st.set_page_config(page_title="AI 챔피언 블루 과정 AX 실습", layout="wide")


def load_dashboard_data():
    """대시보드에서 사용하는 샘플 CSV를 읽고 역명 기준으로 병합합니다."""
    incidents = pd.read_csv("data/raw/incidents.csv")
    stations = pd.read_csv("data/raw/stations.csv")
    merged = incidents.merge(stations, on="역명", how="left")
    return incidents, stations, merged


def render_dashboard():
    """기존 돌발상황 대시보드 화면을 표시합니다."""
    st.title("AI 챔피언 블루 과정 AX 실습 대시보드")
    st.caption("CSV 읽기, 집계, 병합, 필터링, 보고서 생성을 연습하는 미니 프로젝트입니다.")

    incidents, _, merged = load_dashboard_data()

    # 사용자가 원하는 조건으로 데이터를 좁혀 볼 수 있도록 사이드바 필터를 둡니다.
    st.sidebar.header("조회 조건")

    station_list = ["전체"] + sorted(incidents["역명"].dropna().unique().tolist())
    selected_station = st.sidebar.selectbox("역명", station_list)

    risk_list = ["전체"] + sorted(incidents["위험도"].dropna().unique().tolist())
    selected_risk = st.sidebar.selectbox("위험도", risk_list)

    filtered = incidents.copy()
    merged_filtered = merged.copy()

    if selected_station != "전체":
        filtered = filtered[filtered["역명"] == selected_station]
        merged_filtered = merged_filtered[merged_filtered["역명"] == selected_station]

    if selected_risk != "전체":
        filtered = filtered[filtered["위험도"] == selected_risk]
        merged_filtered = merged_filtered[merged_filtered["위험도"] == selected_risk]

    st.subheader("핵심 지표")

    col1, col2, col3 = st.columns(3)
    total_count = len(filtered)
    high_risk_count = len(filtered[filtered["위험도"] == "높음"])
    station_count = filtered["역명"].nunique()

    col1.metric("조회된 사건 수", total_count)
    col2.metric("위험도 높음", high_risk_count)
    col3.metric("관련 역 수", station_count)

    st.subheader("필터링된 사건 데이터")
    st.dataframe(filtered, use_container_width=True)

    # 엑셀에서 한글이 깨지지 않도록 utf-8-sig로 CSV를 만듭니다.
    csv_data = filtered.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="필터링 결과 CSV 다운로드",
        data=csv_data,
        file_name="filtered_incidents.csv",
        mime="text/csv",
    )

    st.subheader("상황유형별 건수")
    type_summary = filtered.groupby("상황유형").size().reset_index(name="건수")

    if len(type_summary) > 0:
        st.bar_chart(type_summary.set_index("상황유형"))
    else:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")

    st.subheader("역명 기준 병합 결과")
    st.dataframe(merged_filtered, use_container_width=True)

    st.subheader("보고서 자동생성")

    if len(filtered) > 0:
        selected_index = st.selectbox("보고서를 생성할 사건 번호", filtered.index)
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
위험도는 {row['위험도']} 수준으로 판단됩니다.
현장에서는 {row['조치결과']} 조치를 실시하였고,
특이사항은 다음과 같습니다: {row['비고']}.
"""
        st.text_area("생성 보고서", report, height=300)
    else:
        st.info("보고서를 생성할 데이터가 없습니다.")


def render_masking_tool():
    """CSV 업로드 후 개인정보를 마스킹하는 화면을 표시합니다."""
    st.title("개인정보 마스킹 도구")
    st.caption("업로드한 CSV는 로컬에 저장하지 않고 메모리에서만 처리합니다.")

    uploaded_file = st.file_uploader("마스킹할 CSV 파일 업로드", type=["csv"])

    if uploaded_file is None:
        st.info("CSV 파일을 업로드하면 원본 미리보기와 마스킹 결과가 표시됩니다.")
        return

    try:
        original_df, used_encoding = read_csv_with_korean_encoding(uploaded_file)
    except UnicodeDecodeError:
        st.error("CSV 인코딩을 읽을 수 없습니다. utf-8-sig 또는 cp949 형식의 파일을 사용해 주세요.")
        return
    except Exception as error:
        st.error(f"CSV 파일을 읽는 중 오류가 발생했습니다: {error}")
        return

    masked_df, mask_counts = mask_dataframe(original_df)
    total_masked_count = sum(mask_counts.values())

    st.success(f"CSV를 {used_encoding} 인코딩으로 읽었습니다.")

    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("마스킹 처리 건수", total_masked_count)
    metric_col2.metric("검사한 행 수", len(original_df))

    if mask_counts:
        st.subheader("항목별 마스킹 건수")
        st.dataframe(
            pd.DataFrame(
                [{"항목": key, "건수": value} for key, value in mask_counts.items() if value > 0]
            ),
            use_container_width=True,
        )

    preview_col1, preview_col2 = st.columns(2)
    with preview_col1:
        st.subheader("원본 데이터 미리보기")
        st.dataframe(original_df.head(20), use_container_width=True)

    with preview_col2:
        st.subheader("마스킹 결과 미리보기")
        st.dataframe(masked_df.head(20), use_container_width=True)

    # BytesIO를 사용하면 다운로드 CSV를 utf-8-sig 바이트로 안전하게 만들 수 있습니다.
    output = BytesIO()
    output.write(masked_df.to_csv(index=False).encode("utf-8-sig"))

    st.download_button(
        label="마스킹 결과 CSV 다운로드",
        data=output.getvalue(),
        file_name="masked_result.csv",
        mime="text/csv",
    )


# GitHub 이동 버튼은 실제 업로드 기능이 아니라 저장소 링크만 제공합니다.
st.sidebar.link_button("GitHub 저장소 열기", GITHUB_URL)

selected_menu = st.sidebar.radio(
    "기능 선택",
    ["돌발상황 대시보드", "개인정보 마스킹 도구"],
)

if selected_menu == "돌발상황 대시보드":
    render_dashboard()
else:
    render_masking_tool()
