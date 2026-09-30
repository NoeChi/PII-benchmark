"""沒有任何個資、但充滿誘餌的文字。所有列出的值都必須保留;任何遮蔽都是誤遮。"""
from __future__ import annotations

from ..model import Case
from ..pool import DISEASES, DRUGS, INSTITUTIONS, TITLES

S = "adversarial"


def cases() -> list[Case]:
    out = [
        Case(f"{S}/hospital_names", S, "、".join(INSTITUTIONS) + "皆為本區合作醫院。", keep=INSTITUTIONS),
        Case(f"{S}/titles_only", S, "本科人力:" + "、".join(TITLES) + "各一名。", keep=TITLES),
        Case(f"{S}/eponymous_diseases", S, "鑑別診斷包含" + "、".join(DISEASES) + "。", keep=DISEASES,
             note="人名命名的疾病"),
        Case(f"{S}/drug_names", S, "常備藥:" + "、".join(DRUGS) + "。", keep=DRUGS),
        Case(f"{S}/table_header_only", S, "姓名 | 病歷號 | 身分證 | 電話 | 地址 | 床號\n(無資料)",
             keep=["姓名", "病歷號", "身分證", "電話", "地址"]),
        Case(f"{S}/shift_codes", S, "班別:D 白班、E 小夜、N 大夜、OFF 休假。", keep=["D", "E", "N", "OFF"]),
        Case(f"{S}/place_like_words", S, "中正紀念堂、大同電鍋、台中市政府、中山高速公路、民生社區。",
             keep=["中正紀念堂", "大同電鍋", "台中市政府", "中山高速公路", "民生社區"]),
        Case(f"{S}/name_like_common_words", S, "王安石變法、張飛、關羽為歷史人物;高雄、屏東為縣市。",
             observe=["王安石", "張飛", "關羽"], keep=["高雄", "屏東"], note="歷史人物是否算個資由政策決定"),
        Case(f"{S}/vital_signs_numbers", S, "BP 128/82 mmHg, HR 88, RR 18, SpO2 97%, BT 36.8, BW 62.5 kg",
             keep=["128/82", "88", "97%", "62.5"]),
        Case(f"{S}/long_numbers_not_id", S, "訂單 20260914001, 序號 88001234567, 金額 1234567 元",
             keep=["20260914001", "1234567"], observe=["88001234567"]),
        Case(f"{S}/dates_times", S, "2026-09-14 08:30 至 2026-09-15 17:00,115/09/14,9月14日。",
             keep=["2026-09-14", "115/09/14", "9月14日"]),
        Case(f"{S}/policy_text", S, "本院自 9 月起實施新版給藥流程,請各單位於晨會宣導;相關教材已上傳院內平台,如有疑問請洽藥劑部。",
             keep=["藥劑部", "給藥流程", "晨會"]),
        Case(f"{S}/department_names", S, "感染科、一般外科、神經內科、新陳代謝科、骨科、心臟內科、加護病房、急診室。",
             keep=["感染科", "一般外科", "神經內科", "新陳代謝科", "急診室"]),
        Case(f"{S}/generic_pronouns", S, "病人的母親與病人的兒子皆已到場,主治醫師已說明。",
             keep=["母親", "兒子", "主治醫師"]),
        Case(f"{S}/product_codes", S, "設備型號 GE-MAC5500, 耗材 REF 123-456-789, LOT A1B2C3",
             keep=["GE-MAC5500", "123-456-789", "A1B2C3"]),
        Case(f"{S}/english_medical", S, "Patient is a 45-year-old male with hypertension and CKD stage 3, on Lisinopril.",
             keep=["hypertension", "CKD stage 3", "Lisinopril", "45-year-old"]),
        Case(f"{S}/surname_chars_in_words", S, "陳舊性骨折、林口長庚、黃疸、張力性氣胸、吳郭魚、劉海。",
             keep=["陳舊性骨折", "黃疸", "張力性氣胸", "吳郭魚"], observe=["林口長庚"],
             note="姓氏字開頭的醫學/一般名詞"),
        Case(f"{S}/three_char_terms", S, "王不留行、白頭翁、何首烏為中藥材;李子、蘋果為水果。",
             keep=["王不留行", "白頭翁", "何首烏", "李子"], note="三字詞長得像人名"),
    ]
    for c in out:
        if not c.observe:
            c.no_mask = True
    return out
