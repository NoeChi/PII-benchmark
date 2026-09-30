"""固定的假個資池。所有值皆虛構;同一個 seed 每次產生相同內容。"""
from __future__ import annotations

import random

SEED = 20260914
rng = random.Random(SEED)

# ── 人名 ─────────────────────────────────────────────────────────────
# 六個固定名(取自 deid-web tests/testdata.py 的假病人)
SIX = ("刁沄妘", "龎芫綺", "郭曉彤", "曾智杰", "林晏伃", "王小明")
COMMON = ["陳建宏", "林淑娟", "張家豪", "蔡侑霖", "廖維珊", "許馨予", "李國豪", "吳雅婷",
          "劉俊傑", "黃詩涵", "周志明", "徐佩珊"]
TWO_CHAR = ["王明", "李娜", "張偉", "林芳"]
FOUR_CHAR = ["歐陽靖雯", "司徒嘉玲", "諸葛承翰", "上官婉柔", "端木子軒", "澹台語菲"]
RARE = ["鄔紜瑄", "闕昀蓁", "禤靖嵐", "藺珮綺", "麴沛芸", "邵翊喆", "諶芷妘", "龔玥彤", "洪熒里"]
JAPANESE = ["佐藤健一", "田中美咲", "高橋由紀", "小野寺翔", "渡邊千尋"]
ENGLISH = ["David Chen", "Mary Johnson", "Michael O'Brien", "Sarah Lee", "Emily Watson-Clark"]
ROMANIZED = ["Lin Mei-Ling", "Cheng-Han Yu", "Wang Hsiao-Ming", "CHEN, CHIEN-HUNG", "Huang Yi-Chen"]

SURNAMES = list("陳林黃張李王吳劉蔡楊許鄭謝郭洪曾邱廖賴周徐蘇葉莊呂江何蕭羅高潘簡朱鍾游彭詹胡施沈余趙盧梁顏柯翁魏孫戴范方宋鄧杜傅侯曹薛丁卓馬董唐溫藍蔣石古紀姚連馮歐程湯田康姜汪白鄒尤巫鐘黎塗龔嚴韓阮袁")
GIVEN = "沄妘芫綺曉彤智杰晏伃舒嫚婕紜家珊賢和美麗冠宇宜庭承翰品妍柏翰欣怡雅婷宗翰佳穎俊宏怡君志明淑芬雅雯建宏思妤子涵宥辰羽晴語彤梓瑄詩涵柏宇冠廷宇軒承恩昱翔柏睿宸瑋"


def fake_name() -> str:
    return rng.choice(SURNAMES) + "".join(rng.choice(GIVEN) for _ in range(2))


# ── 身分證(正確檢核碼) ────────────────────────────────────────────────
_ID_LETTERS = "ABCDEFGHJKLMNPQRSTUVXYWZIO"
_ID_CODES = [10, 11, 12, 13, 14, 15, 16, 17, 34, 18, 19, 20, 21, 22, 35, 23, 24, 25, 26, 27, 28, 29, 32, 30, 31, 33]


def fake_nid(valid: bool = True) -> str:
    letter = rng.choice(_ID_LETTERS[:10])
    code = _ID_CODES[_ID_LETTERS.index(letter)]
    digits = [code // 10, code % 10, rng.choice([1, 2])] + [rng.randint(0, 9) for _ in range(7)]
    weights = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    check = (10 - sum(d * w for d, w in zip(digits, weights)) % 10) % 10
    if not valid:
        check = (check + 1) % 10
    return letter + "".join(map(str, digits[2:])) + str(check)


def fake_mrn(n: int = 8) -> str:
    return str(rng.randint(10 ** (n - 1), 10 ** n - 1))


def fake_hid() -> str:
    return "0000" + "".join(rng.choice("0123456789") for _ in range(8))


def fake_mobile() -> str:
    return "09" + "".join(rng.choice("0123456789") for _ in range(8))


CITIES = {
    "台北市": ["中山區", "大安區", "信義區", "士林區"],
    "新北市": ["板橋區", "新莊區", "中和區", "三重區"],
    "台中市": ["西屯區", "北屯區", "南屯區", "西區"],
    "高雄市": ["左營區", "三民區", "鳳山區", "前鎮區"],
    "台南市": ["東區", "永康區", "安平區", "北區"],
}
ROADS = ["中山路", "中正路", "文化路", "民生路", "復興路", "博愛路", "自由路", "建國路", "光明路", "大學路"]
MAIL_DOMAINS = ["gmail.com", "yahoo.com.tw", "hotmail.com", "outlook.com", "mail.example.org"]


def fake_address() -> str:
    city = rng.choice(list(CITIES))
    return f"{city}{rng.choice(CITIES[city])}{rng.choice(ROADS)}{rng.choice(['', '一段', '二段', '三段'])}{rng.randint(1, 500)}號"


def fake_email() -> str:
    user = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(rng.randint(4, 8)))
    return f"{user}{rng.randint(1, 99)}@{rng.choice(MAIL_DOMAINS)}"


# 固定樣本(給單句 case 用,讓 id 穩定)
NID = "A123456789"
NID2 = "B234567890"
MRN = "10234567"
MRN2 = "20887431"
HID = "000012345678"
MOBILE = "0912345678"
LANDLINE = "04-23592525"
EMAIL = "mei.lin@example.com"
ADDR = "台中市西屯區台灣大道四段1650號"
ADDR2 = "新北市板橋區文化路一段188號"

# 必須保留的院內名詞(不是個資)
INSTITUTIONS = ["台中榮民總醫院", "中山醫學大學附設醫院", "臺大醫院", "中國醫藥大學附設醫院", "中山區公所",
                "台中市政府衛生局", "彰化基督教醫院"]
TITLES = ["主治醫師", "護理師", "營養師", "藥師", "社工師", "看診醫師", "科主任", "住院醫師"]
DISEASES = ["川崎病", "阿茲海默症", "帕金森氏症", "庫欣氏症候群", "馬凡氏症候群", "杜興氏肌肉失養症"]
DRUGS = ["Metformin", "Amoxicillin", "普拿疼", "Lasix", "Aspirin 100mg"]
