import re
import pandas as pd

def mask_phone(text):
    """010-1234-5678 형태의 전화번호 가운데 자리를 마스킹한다."""
    return re.sub(r"(\d{3})-(\d{3,4})-(\d{4})", r"\1-****-\3", str(text))

def mask_name(name):
    """2글자 이상 이름의 마지막 글자를 제외하고 일부 마스킹한다."""
    name = str(name)
    if len(name) <= 1:
        return name
    return name[0] + "*" * (len(name) - 1)

incidents = pd.read_csv("data/raw/incidents.csv")

incidents["연락처_마스킹"] = incidents["연락처"].apply(mask_phone)
incidents["담당자_마스킹"] = incidents["담당자"].apply(mask_name)

safe = incidents.drop(columns=["연락처", "담당자"])
safe.to_csv("data/processed/incidents_masked.csv", index=False, encoding="utf-8-sig")

print(safe.head())
print("\n저장 완료: data/processed/incidents_masked.csv")
