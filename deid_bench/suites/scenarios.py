"""擬真臨床文件。參考 presidio-service tests/test_realistic_scenarios.py 的情境類型,
內容全部用假資料重寫。"""
from __future__ import annotations

from ..model import Case
from ..pool import ADDR, ADDR2, EMAIL, HID, LANDLINE, MOBILE, MRN, MRN2, NID, NID2

S = "scenarios"


def cases() -> list[Case]:
    out: list[Case] = []

    out.append(Case(f"{S}/admission_note", S,
        f"入院病歷\n病人:刁沄妘  性別:女  年齡:67\n病歷號:{MRN}  身分證:{NID}  健保卡號:{HID}\n"
        f"聯絡人:曾智杰(兒子) 電話:{MOBILE}\n住址:{ADDR}\n"
        "主訴:右上腹痛三天,伴隨發燒 38.5°C。\n現病史:病人有高血壓與第二型糖尿病病史,規律服用 Metformin。\n"
        "理學檢查:Murphy's sign 陽性。\n診斷:急性膽囊炎。\n計畫:抗生素治療,安排腹腔鏡手術,由一般外科王小明醫師主刀。",
        mask={"刁沄妘": "P_NAME", MRN: "PID", NID: "NID", HID: "HID", "曾智杰": "P_NAME", MOBILE: "PHONE",
              ADDR: "ADDR", "王小明": "P_NAME"},
        keep=["急性膽囊炎", "Metformin", "Murphy's sign", "一般外科", "高血壓", "38.5"], observe=["67"]))

    out.append(Case(f"{S}/discharge_summary", S,
        f"出院摘要\n姓名:龎芫綺  病歷號:{MRN2}\n入院日:2026-09-01  出院日:2026-09-10\n"
        "住院經過:因缺血性中風入院,接受血栓溶解治療,NIHSS 由 12 分改善至 4 分。\n"
        "檢驗:WBC 8.5, Hb 13.2, Cr 1.1, LDL 142。\n出院用藥:Aspirin 100mg QD, Atorvastatin 20mg HS。\n"
        f"追蹤:神經內科郭曉彤醫師門診,9/24 10:00。有問題請撥 {LANDLINE} 分機 2610。\n"
        "備註:病人為台中榮民總醫院轉診。",
        mask={"龎芫綺": "P_NAME", MRN2: "PID", "郭曉彤": "P_NAME", LANDLINE: "PHONE"},
        keep=["姓名", "缺血性中風", "NIHSS", "Aspirin 100mg", "Atorvastatin", "神經內科", "台中榮民總醫院",
              "2026-09-01", "142"], observe=["2610"]))

    out.append(Case(f"{S}/nursing_handover", S,
        "病房交班 12A\n03 床 林晏伃:術後第二天,血壓 128/82,血糖 142,已拔引流管,預計 9/16 出院。\n"
        f"04 床 王小明:發燒 38.2,已通知值班醫師曾智杰,家屬電話 {MOBILE}。\n"
        "05 床 空床。\n06 床 刁沄妘:夜間睡眠差,疼痛指數 3 分,可自行下床。\n交班者:護理師郭曉彤 接班者:護理師龎芫綺",
        mask={"林晏伃": "P_NAME", "王小明": "P_NAME", "曾智杰": "P_NAME", MOBILE: "PHONE", "刁沄妘": "P_NAME",
              "郭曉彤": "P_NAME", "龎芫綺": "P_NAME"},
        keep=["12A", "03 床", "128/82", "空床", "護理師", "值班醫師"]))

    out.append(Case(f"{S}/phone_log", S,
        f"電話紀錄\n09:10 家屬曾智杰來電({MOBILE})詢問手術時間,已告知 14:00。\n"
        f"10:25 回撥 {LANDLINE} 給社區藥局確認處方。\n11:40 病人刁沄妘女兒龎小芸({MOBILE[:4]}-{MOBILE[4:7]}-{MOBILE[7:]})要求延後探視。\n"
        "13:05 檢驗科來電通知 critical value:K 6.2。",
        mask={"曾智杰": "P_NAME", MOBILE: "PHONE", LANDLINE: "PHONE", "刁沄妘": "P_NAME", "龎小芸": "P_NAME",
              f"{MOBILE[:4]}-{MOBILE[4:7]}-{MOBILE[7:]}": "PHONE"},
        keep=["檢驗科", "critical value", "K 6.2", "14:00"]))

    out.append(Case(f"{S}/consult_note", S,
        f"會診紀錄\n病人:曾智杰(病歷號 {MRN},健保卡號 {HID})\n會診科別:感染科\n"
        "問題:社區型肺炎使用 Amoxicillin 三天無改善。\n建議:改用 Levofloxacin 750mg QD,追蹤胸部 X 光。\n"
        f"會診醫師:林晏伃  回覆時間:2026-09-14 15:30\n家屬已告知並同意,聯絡電話 {MOBILE}。",
        mask={"曾智杰": "P_NAME", MRN: "PID", HID: "HID", "林晏伃": "P_NAME", MOBILE: "PHONE"},
        keep=["感染科", "Amoxicillin", "Levofloxacin", "社區型肺炎", "2026-09-14"]))

    out.append(Case(f"{S}/social_work", S,
        f"社工訪視紀錄\n個案:王小明(身分證 {NID})獨居,主要照顧者為女兒龎芫綺(電話 {MOBILE},email {EMAIL})。\n"
        f"戶籍地址 {ADDR2},實際居住於 {ADDR}。\n經濟狀況:中低收入戶,已協助申請長照 2.0。\n"
        "資源連結:台中市政府衛生局居家服務、中山區公所社福課。",
        mask={"王小明": "P_NAME", NID: "NID", "龎芫綺": "P_NAME", MOBILE: "PHONE", EMAIL: "EMAIL",
              ADDR2: "ADDR", ADDR: "ADDR"},
        keep=["長照 2.0", "台中市政府衛生局", "中山區公所", "中低收入戶"]))

    out.append(Case(f"{S}/bilingual_note", S,
        f"Patient 刁沄妘 (MRN {MRN}) presented with chest tightness. ECG showed ST depression in V4-V6. "
        f"Attending: Dr. 郭曉彤. Family contact: David Chen, mobile {MOBILE}. "
        "Plan: admit to CCU, start heparin, cardiology consult by Dr. Sarah Lee.",
        mask={"刁沄妘": "P_NAME", MRN: "PID", "郭曉彤": "P_NAME", "David Chen": "P_NAME", MOBILE: "PHONE",
              "Sarah Lee": "P_NAME"},
        keep=["CCU", "heparin", "ST depression", "V4-V6", "cardiology"]))

    out.append(Case(f"{S}/medication_list", S,
        f"用藥清單 病人 林晏伃 病歷號 {MRN2}\n1. Metformin 500mg BID\n2. Lasix 40mg QD\n3. 普拿疼 500mg PRN\n"
        "4. Aspirin 100mg QD\n處方醫師:曾智杰",
        mask={"林晏伃": "P_NAME", MRN2: "PID", "曾智杰": "P_NAME"},
        keep=["Metformin", "Lasix", "普拿疼", "Aspirin", "BID"]))

    out.append(Case(f"{S}/lab_report", S,
        f"檢驗報告\n姓名 龎芫綺 病歷號 {MRN} 採檢 2026-09-13 08:15\n"
        "項目 | 結果 | 參考值\nWBC | 11.2 | 4-10\nHb | 9.8 | 12-16\nPLT | 180000 | 150000-400000\n"
        "Na | 138 | 135-145\nK | 3.4 | 3.5-5.0\nCr | 1.8 | 0.6-1.2\n審核:檢驗師王小明",
        mask={"龎芫綺": "P_NAME", MRN: "PID", "王小明": "P_NAME"},
        keep=["姓名", "WBC", "180000", "150000-400000", "檢驗師", "2026-09-13"]))

    out.append(Case(f"{S}/referral_letter", S,
        f"轉診單\n敬啟者:\n茲有病人曾智杰(身分證 {NID2},病歷號 {MRN2}),因帕金森氏症需進一步評估,轉介貴院神經內科。\n"
        f"病人聯絡電話 {MOBILE},地址 {ADDR2}。\n檢附近三個月病歷摘要。\n"
        "中山醫學大學附設醫院 神經內科 主治醫師 郭曉彤 敬上\n2026-09-14",
        mask={"曾智杰": "P_NAME", NID2: "NID", MRN2: "PID", MOBILE: "PHONE", ADDR2: "ADDR", "郭曉彤": "P_NAME"},
        keep=["帕金森氏症", "神經內科", "中山醫學大學附設醫院", "主治醫師"]))

    out.append(Case(f"{S}/chat_with_llm", S,
        f"請幫我把以下病人資料整理成表格:王小明,病歷號 {MRN},電話 {MOBILE};刁沄妘,病歷號 {MRN2},電話 {LANDLINE}。"
        "並依病歷號排序。",
        mask={"王小明": "P_NAME", MRN: "PID", MOBILE: "PHONE", "刁沄妘": "P_NAME", MRN2: "PID", LANDLINE: "PHONE"},
        keep=["病歷號排序"], note="gateway 場景:使用者對 LLM 的提問"))

    out.append(Case(f"{S}/incident_report", S,
        "異常事件通報\n事件:病人跌倒\n時間:2026-09-13 22:40\n地點:12A 病房走廊\n"
        f"當事人:林晏伃(病歷號 {MRN})\n發現者:護理師郭曉彤\n通報者:護理長龎芫綺\n"
        "處置:通知值班醫師曾智杰評估,無明顯外傷,持續觀察。",
        mask={"林晏伃": "P_NAME", MRN: "PID", "郭曉彤": "P_NAME", "龎芫綺": "P_NAME", "曾智杰": "P_NAME"},
        keep=["12A 病房走廊", "護理師", "護理長", "值班醫師", "2026-09-13"]))
    return out
