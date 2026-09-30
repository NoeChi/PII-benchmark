from __future__ import annotations

from ..model import Case
from ..pool import HID, MRN, MRN2, NID, NID2, fake_nid

S = "ids"


def cases() -> list[Case]:
    invalid = fake_nid(valid=False)
    out = [
        # 身分證
        Case(f"{S}/nid_keyword", S, f"身分證字號:{NID}", mask={NID: "NID"}),
        Case(f"{S}/nid_bare", S, f"請核對 {NID} 是否正確。", mask={NID: "NID"}, note="無關鍵字"),
        Case(f"{S}/nid_invalid_checksum", S, f"身分證 {invalid}", observe=[invalid], note="檢核碼錯誤"),
        Case(f"{S}/nid_two_in_line", S, f"病人 {NID} 與保證人 {NID2}", mask={NID: "NID", NID2: "NID"}),
        Case(f"{S}/nid_in_table", S, f"姓名,身分證\n王小明,{NID}\n刁沄妘,{NID2}",
             mask={NID: "NID", NID2: "NID", "王小明": "P_NAME", "刁沄妘": "P_NAME"}, keep=["姓名", "身分證"]),
        Case(f"{S}/arc_number_old", S, "居留證號 AC12345678", mask={"AC12345678": "OTHER"}, note="舊式 ARC:兩字母+8 碼"),
        Case(f"{S}/arc_number_new", S, "統一證號 A812345678", mask={"A812345678": "OTHER"}, note="新式 UI No.:與身分證同格式,第二碼 8/9"),
        Case(f"{S}/passport", S, "護照號碼 312345678", mask={"312345678": "OTHER"}),
        Case(f"{S}/passport_foreign", S, "Passport No. E12345678 (JPN)", mask={"E12345678": "OTHER"}),
        # 病歷號
        Case(f"{S}/mrn_keyword_colon", S, f"病歷號:{MRN}", mask={MRN: "PID"}),
        Case(f"{S}/mrn_keyword_space", S, f"病歷號 {MRN} 之病人已出院", mask={MRN: "PID"}),
        Case(f"{S}/mrn_keyword_variants", S, f"病歷號碼 {MRN},MRN {MRN2}", mask={MRN: "PID", MRN2: "PID"}),
        Case(f"{S}/mrn_chart_no", S, f"Chart No. {MRN}", mask={MRN: "PID"}),
        Case(f"{S}/mrn_short_5", S, "病歷號 12345", mask={"12345": "PID"}),
        Case(f"{S}/mrn_long_12", S, "病歷號 123456789012", observe=["123456789012"], note="超出常見長度"),
        Case(f"{S}/mrn_bare_prose", S, f"{MRN} 這位病人明天回診", observe=[MRN], note="裸號碼無關鍵字,報告已知我方刻意不抓"),
        Case(f"{S}/mrn_table_header", S,
             f"姓名 | 病歷號 | 床號\n王小明 | {MRN} | 12A-03\n刁沄妘 | {MRN2} | 12A-04",
             mask={MRN: "PID", MRN2: "PID", "王小明": "P_NAME", "刁沄妘": "P_NAME"},
             keep=["姓名", "病歷號", "床號", "12A-03", "12A-04"], note="表頭有病歷號,欄位裸號碼"),
        Case(f"{S}/mrn_repeated_bare", S, f"Admission ID: {MRN},訂單號 {MRN}",
             mask={MRN: "PID"}, note="同號碼第二次出現(無關鍵字)"),
        # 健保卡
        Case(f"{S}/hid_keyword", S, f"健保卡號 {HID}", mask={HID: "HID"}),
        Case(f"{S}/hid_bare", S, f"卡號 {HID} 已註銷", mask={HID: "HID"}),
        # 不該遮的號碼
        Case(f"{S}/employee_id", S, "員編 7722 的護理師今日休假。", keep=["7722"]),
        Case(f"{S}/bed_number", S, "床號 12A-03,房號 305。", keep=["12A-03", "305"]),
        Case(f"{S}/order_number", S, "檢驗單號 L2026091400123,批價序號 88.", keep=["L2026091400123"], observe=["88"]),
        Case(f"{S}/lab_values", S, "WBC 8.5, Hb 13.2, PLT 250000, Cr 1.1, glucose 142 mg/dL",
             keep=["250000", "142", "13.2"]),
        Case(f"{S}/dates", S, "入院日 2026-09-01,出院日 115/09/14,生日 1980/05/12。",
             keep=["2026-09-01", "115/09/14"], observe=["1980/05/12"], note="生日是否遮為政策問題"),
        Case(f"{S}/icd_codes", S, "診斷 ICD-10: E11.9, I10, J18.9", keep=["E11.9", "J18.9"]),
        Case(f"{S}/nhi_drug_code", S, "健保碼 BC23456100,批號 A1234567", keep=["BC23456100"], observe=["A1234567"],
             note="批號長得像身分證但少一碼"),
        Case(f"{S}/phone_like_not_phone", S, "訂單編號 0912345 與金額 0987654321 元",
             observe=["0987654321"], note="像手機的數字但不是"),
    ]
    return out
