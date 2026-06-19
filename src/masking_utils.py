import re
from typing import BinaryIO

import pandas as pd


PHONE_PATTERN = re.compile(r"(01[016789])-(\d{3,4})-(\d{4})")
RRN_PATTERN = re.compile(r"(\d{6})-(\d{7})")
EMAIL_PATTERN = re.compile(r"([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")

PHONE_COLUMNS = ["전화번호", "휴대폰", "연락처", "핸드폰", "휴대전화", "mobile", "phone"]
RRN_COLUMNS = ["주민등록번호", "주민번호", "rrn"]
EMAIL_COLUMNS = ["이메일", "email", "메일"]
NAME_COLUMNS = ["이름", "성명", "담당자"]
ADDRESS_COLUMNS = ["주소", "address"]


def read_csv_with_korean_encoding(uploaded_file: BinaryIO) -> tuple[pd.DataFrame, str]:
    """한글 CSV에서 자주 쓰는 utf-8-sig, cp949 인코딩을 순서대로 시도합니다."""
    for encoding in ["utf-8-sig", "cp949"]:
        uploaded_file.seek(0)
        try:
            return pd.read_csv(uploaded_file, encoding=encoding), encoding
        except UnicodeDecodeError:
            continue

    raise UnicodeDecodeError("csv", b"", 0, 1, "지원하는 인코딩이 아닙니다.")


def mask_phone(value):
    """010-1234-5678 형식의 전화번호 가운데 자리를 별표로 바꿉니다."""
    return PHONE_PATTERN.sub(r"\1-****-\3", str(value))


def mask_rrn(value):
    """800311-1234567 형식의 주민등록번호 뒤 7자리를 가립니다."""
    return RRN_PATTERN.sub(r"\1-*******", str(value))


def mask_email(value):
    """test@example.com 형식의 이메일 아이디 부분을 가립니다."""
    return EMAIL_PATTERN.sub(r"***@\2", str(value))


def mask_name(value):
    """이름은 첫 글자만 남기고 나머지를 별표로 바꿉니다."""
    text = str(value)
    if text == "nan" or len(text) <= 1:
        return value
    return text[0] + "*" * (len(text) - 1)


def mask_address(value):
    """주소는 앞쪽 지역 정보 일부만 남기고 상세주소를 간단히 가립니다."""
    text = str(value)
    if text == "nan" or not text.strip():
        return value

    parts = text.split()
    if len(parts) <= 2:
        return parts[0] + " ***" if parts else value

    return " ".join(parts[:2]) + " ***"


def has_column_keyword(column_name: str, keywords: list[str]) -> bool:
    """컬럼명에 개인정보를 뜻하는 키워드가 들어 있는지 확인합니다."""
    normalized = column_name.lower().replace(" ", "")
    return any(keyword.lower() in normalized for keyword in keywords)


def apply_mask_and_count(series: pd.Series, mask_function) -> tuple[pd.Series, int]:
    """마스킹 전후 값이 달라진 셀의 개수를 함께 계산합니다."""
    original = series.copy()
    masked = series.apply(lambda value: value if pd.isna(value) else mask_function(value))
    changed_count = int((original.astype(str) != masked.astype(str)).sum())
    return masked, changed_count


def mask_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """컬럼명 탐지와 정규표현식 탐지를 함께 사용해 개인정보를 마스킹합니다."""
    masked_df = df.copy()
    counts = {
        "전화번호": 0,
        "주민등록번호": 0,
        "이메일": 0,
        "이름": 0,
        "주소": 0,
    }

    for column in masked_df.columns:
        # 컬럼명이 개인정보 유형을 알려 주면 해당 규칙을 우선 적용합니다.
        if has_column_keyword(column, PHONE_COLUMNS):
            masked_df[column], changed = apply_mask_and_count(masked_df[column], mask_phone)
            counts["전화번호"] += changed

        if has_column_keyword(column, RRN_COLUMNS):
            masked_df[column], changed = apply_mask_and_count(masked_df[column], mask_rrn)
            counts["주민등록번호"] += changed

        if has_column_keyword(column, EMAIL_COLUMNS):
            masked_df[column], changed = apply_mask_and_count(masked_df[column], mask_email)
            counts["이메일"] += changed

        if has_column_keyword(column, NAME_COLUMNS):
            masked_df[column], changed = apply_mask_and_count(masked_df[column], mask_name)
            counts["이름"] += changed

        if has_column_keyword(column, ADDRESS_COLUMNS):
            masked_df[column], changed = apply_mask_and_count(masked_df[column], mask_address)
            counts["주소"] += changed

        # 컬럼명이 평범해도 셀 안에 전화번호, 주민번호, 이메일 패턴이 있으면 가립니다.
        before_pattern_mask = masked_df[column].copy()
        masked_df[column] = masked_df[column].apply(
            lambda value: value
            if pd.isna(value)
            else mask_email(mask_rrn(mask_phone(value)))
        )
        changed_by_pattern = before_pattern_mask.astype(str) != masked_df[column].astype(str)

        # 어떤 정규식 때문에 바뀌었는지 다시 비교해서 항목별 건수를 더합니다.
        for value in before_pattern_mask[changed_by_pattern]:
            text = str(value)
            counts["전화번호"] += len(PHONE_PATTERN.findall(text))
            counts["주민등록번호"] += len(RRN_PATTERN.findall(text))
            counts["이메일"] += len(EMAIL_PATTERN.findall(text))

    return masked_df, counts
