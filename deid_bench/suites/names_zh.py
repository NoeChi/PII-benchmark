from __future__ import annotations

from ..model import Case
from ..pool import COMMON, FOUR_CHAR, JAPANESE, MRN, RARE, SIX, TWO_CHAR

S = "names_zh"


def cases() -> list[Case]:
    out: list[Case] = []

    # 1. 常見三字名,各種句型
    tmpl = [
        ("prose_subject", "病人{n}今日主訴頭痛,已安排檢查。"),
        ("prose_no_delim", "昨天{n}來門診拿藥後就回家了。"),
        ("prose_with_de", "{n}的家屬表示晚上會再來。"),
        ("prose_paren", "主治醫師({n})已於今早查房。"),
        ("prose_end", "本次照護負責護理師為{n}"),
        ("colon_label", "姓名:{n}\n病歷號:" + MRN),
        ("fullwidth_colon", "姓名：{n}"),
    ]
    for i, n in enumerate(COMMON[:7]):
        key, t = tmpl[i]
        out.append(Case(f"{S}/{key}", S, t.format(n=n), mask={n: "P_NAME"},
                        keep=["姓名"] if "姓名" in t else []))

    # 2. 二字名(最容易漏)
    for n in TWO_CHAR:
        out.append(Case(f"{S}/two_char_{n}", S, f"病患{n}於急診留觀,家屬陪同。", mask={n: "P_NAME"}))
    out.append(Case(f"{S}/two_char_list", S, "今日出院:王明、李娜、張偉。",
                    mask={"王明": "P_NAME", "李娜": "P_NAME", "張偉": "P_NAME"}))

    # 3. 複姓 / 四字名
    for n in FOUR_CHAR:
        out.append(Case(f"{S}/compound_{n}", S, f"{n}已完成報到,請至 3 診等候。", mask={n: "P_NAME"}))

    # 4. 罕用字
    for n in RARE:
        out.append(Case(f"{S}/rare_{n}", S, f"護理師{n}負責 12A 病房今日晚班。", mask={n: "P_NAME"}, keep=["12A"]))

    # 5. 日式姓名
    for n in JAPANESE:
        out.append(Case(f"{S}/japanese_{n}", S, f"外籍病患{n}需要日文翻譯協助。", mask={n: "P_NAME"}))

    # 6. 稱謂相鄰
    out += [
        Case(f"{S}/title_after", S, "請王小明醫師回電。", mask={"王小明": "P_NAME"}, keep=["醫師"]),
        Case(f"{S}/title_before", S, "護理師郭曉彤已交班給主治醫師曾智杰。",
             mask={"郭曉彤": "P_NAME", "曾智杰": "P_NAME"}, keep=["護理師", "主治醫師"]),
        Case(f"{S}/honorific_xiansheng", S, "刁沄妘先生的太太林晏伃女士來電詢問。",
             mask={"刁沄妘": "P_NAME", "林晏伃": "P_NAME"}),
        Case(f"{S}/surname_title_only", S, "陳醫師說明天再看報告,林護理師會協助。",
             observe=["陳醫師", "林護理師"], note="只有姓+職稱,政策未定"),
        Case(f"{S}/surname_honorific_only", S, "王先生已經在等候區。", observe=["王先生"]),
        Case(f"{S}/nickname", S, "小明今天心情不錯,小華也來探病。", observe=["小明", "小華"]),
    ]

    # 7. 相鄰 / 重複 / 密集
    six = {n: "P_NAME" for n in SIX}
    out += [
        Case(f"{S}/adjacent_comma", S, "刁沄妘,龎芫綺,郭曉彤,曾智杰,林晏伃,王小明", mask=six),
        Case(f"{S}/adjacent_no_delim", S, "與會:刁沄妘龎芫綺郭曉彤", mask={n: "P_NAME" for n in SIX[:3]},
             note="人名之間完全沒分隔"),
        Case(f"{S}/repeated_3x", S,
             "刁沄妘入院。刁沄妘家屬已通知。明日刁沄妘安排手術。", mask={"刁沄妘": "P_NAME"},
             tags=["consistency"], note="同名三次,自家系統代號應一致"),
        Case(f"{S}/same_surname_two", S, "王小明和王大同是兄弟,兩人皆為本院病患。",
             mask={"王小明": "P_NAME", "王大同": "P_NAME"}),
        Case(f"{S}/name_in_relation", S, "病人龎芫綺,配偶曾智杰,女兒龎小芸。",
             mask={"龎芫綺": "P_NAME", "曾智杰": "P_NAME", "龎小芸": "P_NAME"}),
        Case(f"{S}/name_with_english_alias", S, "郭曉彤 (Tina Kuo) 為本次個管師。",
             mask={"郭曉彤": "P_NAME", "Tina Kuo": "P_NAME"}, keep=["個管師"]),
    ]
    return out
