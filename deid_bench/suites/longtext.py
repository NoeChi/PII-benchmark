"""合成超長臨床文件。產生器移植自 deid-web tools/longtext_bench.py(段落 + pipe 名冊 + CSV 混排)。"""
from __future__ import annotations

import random

from ..model import Case
from .. import pool

S = "longtext"

PARA_TEMPLATES = [
    "病人{n}(病歷號 {m},身分證 {nid})於 {d} 因{dx}入院,入院時意識清楚、生命徵象穩定。家屬 {n2} 聯絡電話 {p},住{addr}。"
    "經{tx}後症狀改善,{d2} 討論出院準備。護理評估:傷口乾淨無滲液,疼痛指數 3 分,可自行下床活動。",
    "{n} 主訴{sx}三天,無發燒,理學檢查未見異常。安排抽血與胸部 X 光,結果待回。主治醫師交班給 {n2} 醫師續追蹤,報告寄至 {mail}。",
    "會診紀錄:{n}(病歷號 {m},健保卡號 {hid})會診{dept},建議{plan}。家屬 {n2}({rel})已告知並同意,聯絡電話 {p}。",
    "本院自 9 月起實施新版給藥流程,請各單位於晨會宣導;相關教材已上傳至院內平台,如有疑問請洽藥劑部。",
    "病房交班:{n} 今日血壓 128/82,血糖 142,尿量正常;{n2} 術後第二天,已拔除引流管,預計 {d2} 出院,出院後返家地址 {addr}。",
    "社工訪視:{n}(身分證 {nid})獨居,主要照顧者為 {rel} {n2}(電話 {p},email {mail}),已轉介長照 2.0。",
]
FILL = {
    "dx": ["社區型肺炎", "急性膽囊炎", "缺血性中風", "第二型糖尿病併發症", "髖關節骨折", "心衰竭急性惡化"],
    "tx": ["抗生素治療", "腹腔鏡手術", "血栓溶解治療", "胰島素調整", "人工關節置換", "利尿劑調整"],
    "sx": ["胸悶", "右上腹痛", "左側肢體無力", "多尿口渴", "右髖疼痛", "呼吸喘"],
    "dept": ["感染科", "一般外科", "神經內科", "新陳代謝科", "骨科", "心臟內科"],
    "plan": ["調整抗生素為口服", "安排手術", "加做頸動脈超音波", "衛教飲食控制", "復健科會診", "調整利尿劑劑量"],
    "rel": ["兒子", "配偶", "女兒", "母親", "父親", "媳婦"],
}
TYPE_OF = {"name": "P_NAME", "mrn": "PID", "phone": "PHONE", "nid": "NID", "hid": "HID", "address": "ADDR", "email": "EMAIL"}
KEEP = ["藥劑部", "晨會", "長照 2.0", "疼痛指數", "128/82"]


def build_text(target_chars: int, seed: int) -> tuple[str, dict[str, str]]:
    r = random.Random(seed)
    pool.rng.seed(seed)
    gen = {"name": pool.fake_name, "mrn": pool.fake_mrn, "phone": pool.fake_mobile, "nid": pool.fake_nid,
           "hid": pool.fake_hid, "address": pool.fake_address, "email": pool.fake_email}
    parts, mask = [], {}

    def new(kind: str) -> str:
        v = gen[kind]()
        mask[v] = TYPE_OF[kind]
        return v

    n = block = 0
    while n < target_chars:
        block += 1
        if block % 12 == 0:
            rows = ["序 | 職稱 | 單位 | 姓名 | 病歷號 | 電話 | 分機"]
            for i in range(1, 9):
                rows.append(f"{i} | 護理師 | 內科病房 | {new('name')} | {new('mrn')} | {new('phone')} | 2{i}10")
            para = "\n".join(rows)
        elif block % 12 == 6:
            rows = ["姓名,病歷號,身分證,電話,地址,床號,診斷"]
            for i in range(1, 7):
                rows.append(f"{new('name')},{new('mrn')},{new('nid')},{new('phone')},{new('address')},12A-{i:02d},{r.choice(FILL['dx'])}")
            para = "\n".join(rows)
        else:
            t = r.choice(PARA_TEMPLATES)
            para = t.format(
                n=new("name") if "{n}" in t else "", n2=new("name") if "{n2}" in t else "",
                m=new("mrn") if "{m}" in t else "", p=new("phone") if "{p}" in t else "",
                nid=new("nid") if "{nid}" in t else "", hid=new("hid") if "{hid}" in t else "",
                addr=new("address") if "{addr}" in t else "", mail=new("email") if "{mail}" in t else "",
                d=f"{r.randint(8, 9)}/{r.randint(1, 28)}", d2=f"9/{r.randint(1, 28)}",
                **{k: r.choice(v) for k, v in FILL.items()},
            )
        parts.append(para)
        n += len(para) + 2
    # 只在段落邊界截斷,避免把個資切成一半
    while len("\n\n".join(parts)) > target_chars and len(parts) > 1:
        parts.pop()
    text = "\n\n".join(parts)
    mask = {v: t for v, t in mask.items() if v in text}
    return text, mask


def cases(sizes: tuple[int, ...] = (4000, 32000), seed: int = pool.SEED) -> list[Case]:
    out = []
    for size in sizes:
        text, mask = build_text(size, seed + size)
        out.append(Case(f"{S}/synthetic_{size}", S, text, mask=mask, keep=[k for k in KEEP if k in text],
                        tags=["long"], note=f"{len(text)} 字,{len(mask)} 個個資值"))
    return out
