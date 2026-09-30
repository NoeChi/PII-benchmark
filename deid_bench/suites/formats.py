"""格式 battery:移植自 hermes-gateway tests/test_tabular_format_battery.py,
把原本的真實員工姓名換成 6 個假名。"""
from __future__ import annotations

import base64
import json
from urllib.parse import quote

from ..model import Case
from ..pool import SIX

S = "formats"
A, B, C, D, E, F = SIX
N = dict(a=A, b=B, c=C, d=D, e=E, f=F)

_CASES: list[tuple[str, str]] = [
    ("json_array", '["{a}","{b}","{c}","{d}","{e}","{f}"]'),
    ("json_dict", '{{"a":"{a}","b":"{b}","c":"{c}","d":"{d}","e":"{e}","f":"{f}"}}'),
    ("json_nested", '{{"rows":[{{"name":"{a}","id":1}},{{"name":"{b}","id":2}},{{"name":"{c}","id":3}},'
                    '{{"name":"{d}","id":4}},{{"name":"{e}","id":5}},{{"name":"{f}","id":6}}]}}'),
    ("json_in_json_string", '{{"output":"{{\\"names\\":[\\"{a}\\",\\"{b}\\",\\"{c}\\",\\"{d}\\",\\"{e}\\",\\"{f}\\"]}}"}}'),
    ("python_repr_list", "['{a}', '{b}', '{c}', '{d}', '{e}', '{f}']"),
    ("python_repr_nested", "{{'rows': [{{'name': '{a}'}}, {{'name': '{b}'}}, {{'name': '{c}'}}, "
                           "{{'name': '{d}'}}, {{'name': '{e}'}}, {{'name': '{f}'}}]}}"),
    ("pipe_table_with_row_numbers_and_dates",
     "2 西醫師 | 重症部 | 重內1 | {a} | 2355 | 科主任 | 115/01/01 | 117/12/31\n"
     "3 西醫師 | 重症部 | 重內1 | {b} | 5730 | 主治醫師 | 115/01/01 | 117/12/31\n"
     "4 西醫師 | 重症部 | 重內1 | {c} | 8075 | 主治醫師 | 115/01/01 | 117/12/31\n"
     "5 西醫師 | 重症部 | 重內1 | {d} | 8370 | 主治醫師 | 112/01/01 | 114/12/31\n"
     "6 西醫師 | 重症部 | 重內3 | {e} | 5729 | 主治醫師 | 115/01/01 | 117/12/31\n"
     "7 西醫師 | 重症部 | 重內3 | {f} | 10211 | 主治醫師 | 115/01/01 | 117/12/31"),
    ("pipe_table_clean",
     "西醫師|重症部|重內1|{a}|2355|科主任\n西醫師|重症部|重內1|{b}|5730|主治醫師\n"
     "西醫師|重症部|重內1|{c}|8075|主治醫師\n西醫師|重症部|重內1|{d}|8370|主治醫師\n"
     "西醫師|重症部|重內3|{e}|5729|主治醫師\n西醫師|重症部|重內3|{f}|10211|主治醫師"),
    ("tab_separated",
     "西醫師\t重症部\t重內1\t{a}\t2355\t科主任\n西醫師\t重症部\t重內1\t{b}\t5730\t主治醫師\n"
     "西醫師\t重症部\t重內1\t{c}\t8075\t主治醫師\n西醫師\t重症部\t重內1\t{d}\t8370\t主治醫師\n"
     "西醫師\t重症部\t重內3\t{e}\t5729\t主治醫師\n西醫師\t重症部\t重內3\t{f}\t10211\t主治醫師"),
    ("semicolon_separated",
     "西醫師;重症部;重內1;{a};2355;科主任\n西醫師;重症部;重內1;{b};5730;主治醫師\n"
     "西醫師;重症部;重內1;{c};8075;主治醫師\n西醫師;重症部;重內1;{d};8370;主治醫師\n"
     "西醫師;重症部;重內3;{e};5729;主治醫師\n西醫師;重症部;重內3;{f};10211;主治醫師"),
    ("csv_multi_row",
     "西醫師,重症部,重內1,{a},2355,科主任\n西醫師,重症部,重內1,{b},5730,主治醫師\n"
     "西醫師,重症部,重內1,{c},8075,主治醫師\n西醫師,重症部,重內1,{d},8370,主治醫師\n"
     "西醫師,重症部,重內3,{e},5729,主治醫師\n西醫師,重症部,重內3,{f},10211,主治醫師"),
    ("multi_space_aligned",
     "西醫師   重症部   重內1   {a}    2355  科主任\n西醫師   重症部   重內1   {b}    5730  主治醫師\n"
     "西醫師   重症部   重內1   {c}    8075  主治醫師\n西醫師   重症部   重內1   {d}    8370  主治醫師\n"
     "西醫師   重症部   重內3   {e}    5729  主治醫師\n西醫師   重症部   重內3   {f}    10211 主治醫師"),
    ("markdown_table",
     "| 職類 | 科別 | 姓名 | 員編 | 職稱 |\n|-----|-----|------|-----|------|\n"
     "| 西醫師 | 重內1 | {a} | 2355 | 科主任 |\n| 西醫師 | 重內1 | {b} | 5730 | 主治醫師 |\n"
     "| 西醫師 | 重內1 | {c} | 8075 | 主治醫師 |\n| 西醫師 | 重內1 | {d} | 8370 | 主治醫師 |\n"
     "| 西醫師 | 重內3 | {e} | 5729 | 主治醫師 |\n| 西醫師 | 重內3 | {f} | 10211 | 主治醫師 |"),
    ("markdown_bullet",
     "醫師名單:\n- {a}(重內1, 2355)\n- {b}(重內1, 5730)\n- {c}(重內1, 8075)\n"
     "- {d}(重內1, 8370)\n- {e}(重內3, 5729)\n- {f}(重內3, 10211)"),
    ("markdown_numbered", "1. {a}\n2. {b}\n3. {c}\n4. {d}\n5. {e}\n6. {f}"),
    ("markdown_bold_names",
     "**{a}** 重內1, **{b}** 重內1, **{c}** 重內1, **{d}** 重內1, **{e}** 重內3, **{f}** 重內3"),
    ("html_table",
     "<table><tr><th>姓名</th><th>科別</th></tr><tr><td>{a}</td><td>重內1</td></tr>"
     "<tr><td>{b}</td><td>重內1</td></tr><tr><td>{c}</td><td>重內1</td></tr>"
     "<tr><td>{d}</td><td>重內1</td></tr><tr><td>{e}</td><td>重內3</td></tr>"
     "<tr><td>{f}</td><td>重內3</td></tr></table>"),
    ("html_spans", "<span>{a}</span><span>{b}</span><span>{c}</span><span>{d}</span><span>{e}</span><span>{f}</span>"),
    ("xml", "<doctors><doctor><name>{a}</name></doctor><doctor><name>{b}</name></doctor>"
            "<doctor><name>{c}</name></doctor><doctor><name>{d}</name></doctor>"
            "<doctor><name>{e}</name></doctor><doctor><name>{f}</name></doctor></doctors>"),
    ("yaml_list", "doctors:\n  - {a}\n  - {b}\n  - {c}\n  - {d}\n  - {e}\n  - {f}"),
    ("yaml_dict", "rows:\n  - name: {a}\n    id: 2355\n  - name: {b}\n    id: 5730\n  - name: {c}\n    id: 8075\n"
                  "  - name: {d}\n    id: 8370\n  - name: {e}\n    id: 5729\n  - name: {f}\n    id: 10211"),
    ("ini_toml", "[doc1]\nname = {a}\nid = 2355\n[doc2]\nname = {b}\nid = 5730\n[doc3]\nname = {c}\nid = 8075\n"
                 "[doc4]\nname = {d}\nid = 8370\n[doc5]\nname = {e}\nid = 5729\n[doc6]\nname = {f}\nid = 10211"),
    ("url_query_string", "/api/doctors?n1={a}&n2={b}&n3={c}&n4={d}&n5={e}&n6={f}"),
    ("natural_with_dunhao", "醫師有:{a}、{b}、{c}、{d}、{e}、{f}等六位。"),
    ("natural_enumeration", "本科現有六位主治醫師,分別為{a}、{b}、{c}、{d}、{e}及{f}。"),
    ("chat_log", "[10:00] {a}: 早安\n[10:01] {b}: 早\n[10:02] {c}: morning\n[10:03] {d}: 都到了嗎\n[10:04] {e}: 等{f}"),
    ("ascii_box_table",
     "┌────────┬────────┐\n│ {a} │ 2355   │\n│ {b} │ 5730   │\n│ {c} │ 8075   │\n"
     "│ {d} │ 8370   │\n│ {e} │ 5729   │\n│ {f} │ 10211  │\n└────────┴────────┘"),
    ("star_separated", "{a}★{b}★{c}★{d}★{e}★{f}"),
    ("slash_separated", "{a}/{b}/{c}/{d}/{e}/{f}"),
    ("fullwidth_space_separated", "{a}　{b}　{c}　{d}　{e}　{f}"),
    ("sql_insert", "INSERT INTO staff (name, emp_id) VALUES ('{a}', 2355), ('{b}', 5730), ('{c}', 8075), "
                   "('{d}', 8370), ('{e}', 5729), ('{f}', 10211);"),
    ("log_line", "2026-09-14 10:00:01 INFO user={a} action=login\n2026-09-14 10:00:05 INFO user={b} action=view\n"
                 "2026-09-14 10:00:09 INFO user={c} action=view\n2026-09-14 10:00:12 INFO user={d} action=logout\n"
                 "2026-09-14 10:00:15 INFO user={e} action=login\n2026-09-14 10:00:20 INFO user={f} action=login"),
    ("email_header", "From: {a} <a@example.com>\nTo: {b} <b@example.com>\nCc: {c}, {d}, {e}, {f}\nSubject: 會議"),
]

KEEP_COMMON = ["主治醫師", "科主任", "重內1"]


def cases() -> list[Case]:
    out: list[Case] = []
    for key, tmpl in _CASES:
        text = tmpl.format(**N)
        keep = [k for k in KEEP_COMMON if k in text]
        if "姓名" in text:
            keep.append("姓名")
        out.append(Case(f"{S}/{key}", S, text, mask={n: "P_NAME" for n in SIX}, keep=keep))
    # 已知極限:編碼後的人名
    pct = "name=" + quote(A) + "&name=" + quote(B)
    out.append(Case(f"{S}/percent_encoded", S, pct, observe=[quote(A), quote(B)], known_gap=True,
                    note="URL 百分比編碼"))
    b64 = base64.b64encode(json.dumps({"names": [A, B]}, ensure_ascii=False).encode()).decode()
    out.append(Case(f"{S}/base64_payload", S, b64, observe=[b64], known_gap=True, note="base64,兩套皆抓不到"))
    return out
