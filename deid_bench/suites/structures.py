"""混合個資的密集結構:名冊、班表、多欄表格。每列同時有人名+號碼+電話等。"""
from __future__ import annotations

from ..model import Case
from ..pool import COMMON, RARE, fake_address, fake_hid, fake_mobile, fake_mrn, fake_name, fake_nid

S = "structures"
SHIFTS = ["D", "E", "N", "OFF"]


def cases() -> list[Case]:
    out: list[Case] = []

    # 1. pipe 表:名+病歷號+電話,表頭要保留
    rows, mask = ["序 | 姓名 | 病歷號 | 電話 | 床號"], {}
    for i, n in enumerate(COMMON[:8], 1):
        m, p = fake_mrn(), fake_mobile()
        rows.append(f"{i} | {n} | {m} | {p} | 12A-{i:02d}")
        mask.update({n: "P_NAME", m: "PID", p: "PHONE"})
    out.append(Case(f"{S}/pipe_roster_8", S, "\n".join(rows), mask=mask,
                    keep=["姓名", "病歷號", "電話", "床號", "12A-01", "12A-08"]))

    # 2. CSV:名+病歷號+身分證+電話+地址+診斷
    rows, mask = ["姓名,病歷號,身分證,電話,地址,床號,診斷"], {}
    for i, n in enumerate(COMMON[:6], 1):
        m, nid, p, a = fake_mrn(), fake_nid(), fake_mobile(), fake_address()
        rows.append(f"{n},{m},{nid},{p},{a},12B-{i:02d},社區型肺炎")
        mask.update({n: "P_NAME", m: "PID", nid: "NID", p: "PHONE", a: "ADDR"})
    out.append(Case(f"{S}/csv_full_pii_6", S, "\n".join(rows), mask=mask,
                    keep=["姓名", "病歷號", "身分證", "社區型肺炎", "12B-01"]))

    # 3. 班表:名 + 班別代碼(D/E/N/OFF 要保留)
    rows, mask = ["姓名 | 9/1 | 9/2 | 9/3 | 9/4 | 9/5 | 9/6 | 9/7"], {}
    for i, n in enumerate(COMMON[:10]):
        shifts = [SHIFTS[(i + j) % 4] for j in range(7)]
        rows.append(f"{n} | " + " | ".join(shifts))
        mask[n] = "P_NAME"
    out.append(Case(f"{S}/shift_schedule_10", S, "\n".join(rows), mask=mask, keep=["姓名", "OFF", "9/1"]))

    # 4. 無表頭班表(不知道哪欄是名字)
    rows, mask = [], {}
    for i, n in enumerate(RARE[:8]):
        rows.append(f"{n},{SHIFTS[i % 4]},{SHIFTS[(i + 1) % 4]},{SHIFTS[(i + 2) % 4]}")
        mask[n] = "P_NAME"
    out.append(Case(f"{S}/shift_no_header_rare", S, "\n".join(rows), mask=mask, keep=["OFF"]))

    # 5. 大名冊 30 列(壓分塊)
    rows, mask = ["序 | 職類 | 部門 | 姓名 | 員編 | 職稱 | 效期起 | 效期迄"], {}
    for i in range(1, 31):
        n = fake_name()
        rows.append(f"{i} | 護理師 | 內科部 | {n} | {2000 + i} | 護理師 | 115/01/01 | 117/12/31")
        mask[n] = "P_NAME"
    out.append(Case(f"{S}/big_roster_30", S, "\n".join(rows), mask=mask, keep=["護理師", "內科部", "2001", "2030"]))

    # 6. JSON 病人物件陣列
    import json
    objs, mask = [], {}
    for _ in range(5):
        n, m, nid, p, h, a = fake_name(), fake_mrn(), fake_nid(), fake_mobile(), fake_hid(), fake_address()
        objs.append({"name": n, "mrn": m, "nid": nid, "phone": p, "nhi": h, "address": a, "bed": "12C-01"})
        mask.update({n: "P_NAME", m: "PID", nid: "NID", p: "PHONE", h: "HID", a: "ADDR"})
    out.append(Case(f"{S}/json_patients_5", S, json.dumps(objs, ensure_ascii=False, indent=1), mask=mask,
                    keep=["12C-01", "\"mrn\"", "\"nhi\""]))

    # 7. Markdown 表含 email 與地址
    rows, mask = ["| 姓名 | Email | 地址 |", "|---|---|---|"], {}
    from ..pool import fake_email
    for n in COMMON[6:10]:
        e, a = fake_email(), fake_address()
        rows.append(f"| {n} | {e} | {a} |")
        mask.update({n: "P_NAME", e: "EMAIL", a: "ADDR"})
    out.append(Case(f"{S}/markdown_contact_4", S, "\n".join(rows), mask=mask, keep=["Email", "地址"]))

    # 8. 鍵值對紀錄(EMR 匯出)
    n, m, nid, p, a = fake_name(), fake_mrn(), fake_nid(), fake_mobile(), fake_address()
    text = (f"姓名:{n}\n病歷號:{m}\n身分證:{nid}\n性別:女\n出生:1975-03-02\n電話:{p}\n地址:{a}\n"
            f"主診斷:第二型糖尿病\n主治:內分泌科\n床號:5A-12")
    out.append(Case(f"{S}/key_value_record", S, text, mask={n: "P_NAME", m: "PID", nid: "NID", p: "PHONE", a: "ADDR"},
                    keep=["第二型糖尿病", "內分泌科", "5A-12", "女"], observe=["1975-03-02"]))

    # 9. 帶引號的 CSV(欄位內有逗號與換行)
    n, m, a = COMMON[1], fake_mrn(), fake_address()
    text = (f'姓名,病歷號,地址,備註\n"{n}","{m}","{a}","家屬:{COMMON[2]}, 電話 {fake_mobile()}"\n'
            f'"{COMMON[3]}","{fake_mrn()}","台北市大安區復興南路一段390號12樓之3","多行\n備註"')
    out.append(Case(f"{S}/csv_quoted_fields", S, text,
                    mask={n: "P_NAME", m: "PID", a: "ADDR", COMMON[2]: "P_NAME", COMMON[3]: "P_NAME",
                          "台北市大安區復興南路一段390號12樓之3": "ADDR"}, keep=["姓名", "備註", "多行"]))

    # 10. 轉置表(標籤在左欄、值在右欄)
    n, m, nid, p = COMMON[4], fake_mrn(), fake_nid(), fake_mobile()
    text = f"| 姓名 | {n} |\n| 病歷號 | {m} |\n| 身分證 | {nid} |\n| 電話 | {p} |\n| 診斷 | 髖關節骨折 |"
    out.append(Case(f"{S}/transposed_table", S, text, mask={n: "P_NAME", m: "PID", nid: "NID", p: "PHONE"},
                    keep=["姓名", "病歷號", "髖關節骨折"]))

    # 11. 同一人資料在段落與表格各出現一次(一致性)
    n, m = COMMON[0], fake_mrn()
    text = f"病人{n}(病歷號 {m})今日入院。\n\n| 姓名 | 病歷號 |\n|---|---|\n| {n} | {m} |"
    out.append(Case(f"{S}/prose_plus_table_same_person", S, text, mask={n: "P_NAME", m: "PID"},
                    keep=["姓名", "病歷號"], tags=["consistency"]))
    return out
