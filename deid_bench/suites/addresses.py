from __future__ import annotations

from ..model import Case
from ..pool import ADDR, ADDR2, INSTITUTIONS

S = "addresses"


def cases() -> list[Case]:
    out = [
        Case(f"{S}/full_keyword", S, f"住址:{ADDR}", mask={ADDR: "ADDR"}),
        Case(f"{S}/full_prose", S, f"病人住在{ADDR2},出院後由家屬接送。", mask={ADDR2: "ADDR"}),
        Case(f"{S}/full_floor", S, "地址 台北市大安區復興南路一段390號12樓之3",
             mask={"台北市大安區復興南路一段390號12樓之3": "ADDR"}),
        Case(f"{S}/full_village", S, "戶籍 彰化縣員林市三和里中山路二段80巷5號",
             mask={"彰化縣員林市三和里中山路二段80巷5號": "ADDR"}),
        Case(f"{S}/with_postal", S, f"40705 {ADDR}", mask={ADDR: "ADDR"}, observe=["40705"]),
        Case(f"{S}/tai_variant", S, "地址 臺中市西屯區臺灣大道四段1650號", mask={"臺中市西屯區臺灣大道四段1650號": "ADDR"}, note="臺 寫法"),
        Case(f"{S}/rural_full", S, "戶籍 南投縣埔里鎮大城里3鄰中山路三段12巷5弄8號之2",
             mask={"南投縣埔里鎮大城里3鄰中山路三段12巷5弄8號之2": "ADDR"}, note="鄉鎮村里鄰巷弄"),
        Case(f"{S}/two_addresses", S, f"通訊 {ADDR};戶籍 {ADDR2}", mask={ADDR: "ADDR", ADDR2: "ADDR"}),
        Case(f"{S}/no_number", S, "住台中市西屯區台灣大道四段附近", observe=["台中市西屯區台灣大道四段"]),
        Case(f"{S}/district_only", S, "病人來自台中市西屯區。", observe=["台中市西屯區"], note="宏觀地名,報告說我方偏保守"),
        Case(f"{S}/city_only", S, "病人從高雄市北上就醫。", keep=["高雄市"]),
        Case(f"{S}/road_only", S, "沿著中山路往北就會看到醫院。", keep=["中山路"]),
        Case(f"{S}/fullwidth_digits", S, "住台中市西屯區台灣大道四段１６５０號", observe=["台中市西屯區台灣大道四段１６５０號"]),
        Case(f"{S}/english_address", S, "Address: No. 1650, Sec. 4, Taiwan Blvd., Xitun Dist., Taichung City",
             mask={"No. 1650, Sec. 4, Taiwan Blvd., Xitun Dist., Taichung City": "ADDR"}),
        Case(f"{S}/address_in_csv", S, f"姓名,地址\n王小明,{ADDR}\n刁沄妘,{ADDR2}",
             mask={ADDR: "ADDR", ADDR2: "ADDR", "王小明": "P_NAME", "刁沄妘": "P_NAME"}, keep=["姓名", "地址"]),
    ]
    # 機構名稱不是個資
    for inst in INSTITUTIONS:
        out.append(Case(f"{S}/institution_{inst}", S, f"病人自{inst}轉診至本院。", keep=[inst]))
    out += [
        Case(f"{S}/institution_with_address", S, f"轉診單位:台中榮民總醫院({ADDR})",
             mask={ADDR: "ADDR"}, keep=["台中榮民總醫院"]),
        Case(f"{S}/ward_location", S, "病人目前在 12A 病房 03 床,加護病房已滿。", keep=["12A", "加護病房"]),
        Case(f"{S}/landmark", S, "掛號櫃台在一樓大廳,靠近中山路側門。", keep=["中山路"]),
    ]
    return out
