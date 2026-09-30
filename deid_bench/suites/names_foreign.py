from __future__ import annotations

from ..model import Case
from ..pool import ENGLISH, ROMANIZED

S = "names_foreign"


def cases() -> list[Case]:
    out: list[Case] = []
    for n in ENGLISH:
        out.append(Case(f"{S}/english_{n.split()[0]}", S,
                        f"Patient {n} was admitted for observation.", mask={n: "P_NAME"}))
    for n in ROMANIZED:
        out.append(Case(f"{S}/romanized_{n.split()[0].strip(',')}", S,
                        f"{n} will come back next week for follow-up.", mask={n: "P_NAME"}))
    out += [
        Case(f"{S}/mixed_zh_en", S, "病人 David Chen(陳大衛)由 Dr. Sarah Lee 收治。",
             mask={"David Chen": "P_NAME", "陳大衛": "P_NAME", "Sarah Lee": "P_NAME"}),
        Case(f"{S}/allcaps_passport_style", S, "Name: CHEN, CHIEN-HUNG  Sex: M  DOB: 1980-05-12",
             mask={"CHEN, CHIEN-HUNG": "P_NAME"}, observe=["1980-05-12"]),
        Case(f"{S}/english_in_table", S,
             "| Name | Ward |\n|---|---|\n| Mary Johnson | 12A |\n| Michael O'Brien | 12B |",
             mask={"Mary Johnson": "P_NAME", "Michael O'Brien": "P_NAME"}, keep=["Name", "Ward"]),
        Case(f"{S}/romanized_lowercase", S, "contact person: lin mei-ling, phone later",
             observe=["lin mei-ling"], note="全小寫拼音"),
        Case(f"{S}/initials", S, "Follow-up by J. Chen and M. Wang next Monday.",
             observe=["J. Chen", "M. Wang"]),
        Case(f"{S}/famous_not_patient", S, "依據 Framingham risk score 與 Glasgow Coma Scale 評估。",
             keep=["Framingham", "Glasgow"], note="地名/量表名不是人名"),
    ]
    return out
