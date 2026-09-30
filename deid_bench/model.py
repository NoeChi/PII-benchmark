from __future__ import annotations

from dataclasses import dataclass, field

# 期望型別使用自家系統的代號詞彙:
#   P_NAME 人名 / PID 病歷號 / NID 身分證 / HID 健保卡號 / PHONE / EMAIL / ADDR 地址
#   OTHER  其他可識別資訊(護照、居留證…),只要有遮就算對,不比型別
TYPES = ("P_NAME", "PID", "NID", "HID", "PHONE", "EMAIL", "ADDR", "OTHER")


@dataclass
class Case:
    id: str
    suite: str
    text: str
    # 必須被遮的值 → 期望型別
    mask: dict[str, str] = field(default_factory=dict)
    # 必須保留(不可誤遮)的值
    keep: list[str] = field(default_factory=list)
    # 政策未定、只觀察不計分的值(報告會列出兩套系統各自有沒有遮)
    observe: list[str] = field(default_factory=list)
    # 已知極限(例如 base64),計分時獨立列出、不算失敗
    known_gap: bool = False
    # 整段文字不該有任何遮蔽(誘餌套件用):輸出只要出現任何標籤就算誤遮
    no_mask: bool = False
    note: str = ""
    tags: list[str] = field(default_factory=list)

    def validate(self) -> None:
        for v, t in self.mask.items():
            assert v in self.text, f"{self.id}: mask 值不在文字中: {v!r}"
            assert t in TYPES, f"{self.id}: 未知型別 {t}"
        for v in self.keep + self.observe:
            assert v in self.text, f"{self.id}: keep/observe 值不在文字中: {v!r}"
        clash = set(self.mask) & set(self.keep)
        assert not clash, f"{self.id}: 同時在 mask 與 keep: {clash}"
        if self.no_mask:
            assert not self.mask, f"{self.id}: no_mask 的 case 不能有 mask"
