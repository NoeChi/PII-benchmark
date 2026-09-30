"""字元層級的變形。多數為 observe(政策未定或已知極限),少數必遮。"""
from __future__ import annotations

from ..model import Case
from ..pool import MOBILE, NID

S = "encoding"
ZW = "​"  # zero width space


def cases() -> list[Case]:
    return [
        Case(f"{S}/fullwidth_phone", S, "電話 ０９１２３４５６７８", mask={"０９１２３４５６７８": "PHONE"}),
        Case(f"{S}/fullwidth_nid", S, "身分證 Ａ１２３４５６７８９", mask={"Ａ１２３４５６７８９": "NID"}),
        Case(f"{S}/spaced_nid", S, "身分證 A 1 2 3 4 5 6 7 8 9", mask={"A 1 2 3 4 5 6 7 8 9": "NID"}),
        Case(f"{S}/spaced_phone", S, f"電話 {' '.join(MOBILE)}", mask={" ".join(MOBILE): "PHONE"}),
        Case(f"{S}/zero_width_in_name", S, f"病人王{ZW}小{ZW}明今日入院", mask={f"王{ZW}小{ZW}明": "P_NAME"}),
        Case(f"{S}/zero_width_in_nid", S, f"身分證 {NID[:5]}{ZW}{NID[5:]}", mask={f"{NID[:5]}{ZW}{NID[5:]}": "NID"}),
        Case(f"{S}/name_split_newline", S, "病人王小\n明今日入院", mask={"王小\n明": "P_NAME"}),
        Case(f"{S}/name_with_middle_dot", S, "病人 王·小明 今日入院", observe=["王·小明"]),
        Case(f"{S}/name_spaced", S, "病人 王 小 明 今日入院", observe=["王 小 明"]),
        Case(f"{S}/simplified_chinese", S, "病人王晓彤,联系电话 0912345678,住址台中市西屯区台湾大道四段1650号",
             mask={"0912345678": "PHONE", "王晓彤": "P_NAME", "台中市西屯区台湾大道四段1650号": "ADDR"}, note="簡體"),
        Case(f"{S}/name_in_brackets_fullwidth", S, "病人【王小明】已報到", mask={"王小明": "P_NAME"}),
        Case(f"{S}/name_with_emoji", S, "🎉 恭喜 王小明 出院 🎉", mask={"王小明": "P_NAME"}),
        Case(f"{S}/mixed_width_phone", S, "電話 09１２345６78", mask={"09１２345６78": "PHONE"}),
        Case(f"{S}/nid_with_dash", S, "身分證 A12-345-6789", mask={"A12-345-6789": "NID"}),
        Case(f"{S}/nid_lowercase", S, "身分證 a123456789", mask={"a123456789": "NID"}),
        Case(f"{S}/name_partially_redacted", S, "病人王○明與陳O華已出院", observe=["王○明", "陳O華"], note="已手動部分遮蔽的名字"),
        Case(f"{S}/crlf_record", S, "姓名:王小明\r\n病歷號:10234567\r\n電話:0912345678\r\n",
             mask={"王小明": "P_NAME", "10234567": "PID", "0912345678": "PHONE"}, keep=["姓名", "病歷號"], note="Windows 換行"),
        Case(f"{S}/html_entities", S, "病人&nbsp;王小明&nbsp;電話&nbsp;0912345678",
             mask={"王小明": "P_NAME", "0912345678": "PHONE"}),
        Case(f"{S}/markdown_escaped", S, "病人 王\\_小明 電話 0912\\-345\\-678", observe=["王\\_小明", "0912\\-345\\-678"]),
        Case(f"{S}/rtl_mark", S, "病人 ‮王小明‬ 已出院", observe=["王小明"], note="RTL override 字元包住"),
    ]
