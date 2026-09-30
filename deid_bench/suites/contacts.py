from __future__ import annotations

from ..model import Case
from ..pool import EMAIL, MOBILE

S = "contacts"


def cases() -> list[Case]:
    phones = [
        ("mobile_plain", "0912345678"),
        ("mobile_dash", "0912-345-678"),
        ("mobile_space", "0912 345 678"),
        ("mobile_intl", "+886-912-345-678"),
        ("mobile_intl_compact", "+886912345678"),
        ("landline_dash", "04-23592525"),
        ("landline_paren", "(04)2359-2525"),
        ("landline_taipei", "02-2345-6789"),
        ("landline_with_ext", "04-23592525 ext 2610"),
        ("landline_fenji", "04-23592525 分機 2610"),
    ]
    out: list[Case] = []
    for key, p in phones:
        core = p.split(" ext")[0].split(" 分機")[0]
        obs = ["2610"] if "2610" in p else []
        out.append(Case(f"{S}/{key}", S, f"聯絡電話 {p},請於上班時間來電。", mask={core: "PHONE"}, observe=obs,
                        note="分機是否一併遮為政策問題" if obs else ""))
    out += [
        Case(f"{S}/phone_bare_no_keyword", S, f"{MOBILE} 這支有人接嗎", mask={MOBILE: "PHONE"}),
        Case(f"{S}/mobile_intl_zero", S, "手機 +886 (0)912-345-678", mask={"+886 (0)912-345-678": "PHONE"}),
        Case(f"{S}/tollfree", S, "客服專線 0800-123-456,健保署 0800-030-598。", keep=["0800-123-456", "0800-030-598"],
             note="免付費機構專線不是個資"),
        Case(f"{S}/ext_only", S, "有問題請撥分機 2610 或 2710。", keep=["2610", "2710"]),
        Case(f"{S}/fax", S, "傳真 04-23592526", mask={"04-23592526": "PHONE"}),
        Case(f"{S}/emergency_119", S, "緊急請撥 119 或 1925 安心專線。", keep=["119", "1925"]),
        Case(f"{S}/hospital_switchboard", S, "本院總機 04-23592525 轉各科。", observe=["04-23592525"],
             note="醫院總機是否該遮為政策問題"),
    ]
    emails = [
        ("email_plain", EMAIL),
        ("email_upper", "Mei.Lin@Example.COM"),
        ("email_plus_tag", "mei.lin+family@example.com"),
        ("email_subdomain", "mlin@mail.hospital.org.tw"),
        ("email_numeric", "a123456@gmail.com"),
    ]
    for key, e in emails:
        out.append(Case(f"{S}/{key}", S, f"報告請寄到 {e}。", mask={e: "EMAIL"}))
    out += [
        Case(f"{S}/email_angle", S, "寄件人:Mei Lin <mei.lin@example.com>",
             mask={"mei.lin@example.com": "EMAIL", "Mei Lin": "P_NAME"}),
        Case(f"{S}/email_malformed", S, "email 寫成 mei.lin@example 少了網域", observe=["mei.lin@example"]),
        Case(f"{S}/email_obfuscated", S, "mei.lin (at) example (dot) com", observe=["mei.lin (at) example (dot) com"]),
        Case(f"{S}/email_generic_dept", S, "請洽 service@hospital.org.tw 或藥劑部。", observe=["service@hospital.org.tw"],
             note="單位信箱是否該遮"),
        Case(f"{S}/line_id", S, "LINE ID: meilin_0912", observe=["meilin_0912"]),
        Case(f"{S}/url_with_name", S, "https://example.com/patients/wang-xiao-ming/report", observe=["wang-xiao-ming"]),
    ]
    return out
