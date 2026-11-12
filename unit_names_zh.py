"""Chinese names for identified characters in the support data.

Keys are Japanese character identifiers, rather than inferred spellings of
English names.  Names in saves, hashes, support flags and image filenames are
never changed.  Unrecognised characters keep their original display name.
"""
from __future__ import annotations

import re
from functools import lru_cache

import supports

NAMES = {
    "アレキサンドラ": "亚历珊德拉", "アナトリア": "爱娜特莉亚", "アスワン": "亚丝望",
    "ベンディッツ": "班迪兹", "ベルトラン": "贝特兰", "ボナパルテ": "波拿帕尔特",
    "バッカニア": "巴卡尼亚", "カイ": "凯伊", "カターニャ": "卡塔妮雅", "セントリオン": "盛托利翁",
    "キリーク": "齐利科", "ダイトウ": "大刀", "ダンテ": "丹提", "ディエゴ": "迪雅各",
    "ディートリヒ": "迪托利希", "イシュマール": "伊修玛尔", "エスメラルダ": "艾丝梅拉尔达",
    "ファビオ": "法毕欧", "フィアナ": "绯亚娜", "ゲイツ": "盖茨", "ゴライアス": "哥莱亚斯",
    "グザラン": "古扎岚", "ハルヴィン": "哈尔温", "コウカ": "红花", "イニオニ": "易尼奥尼",
    "イオ": "伊欧", "ジャスミン": "嘉丝敏", "キロイカ": "奇洛伊卡", "レダ": "蕾达",
    "リリアン": "莉利安", "ロレッタ": "罗蕾塔", "ルルディヤー": "露露蒂雅", "ライサンダー": "莱桑达",
    "マジーデ": "马吉迪", "マクシム": "马克西姆", "ミカエラ": "米迦艾拉", "ムウ": "穆",
    "ネイサン": "内森", "ナジャ": "哪吒", "ニネ": "妮涅", "ノクチュラ": "诺克裘拉",
    "ヌッツォ": "努佐", "ヌディーヌ": "努蒂奴", "オリンピア": "奥琳琵娅", "オルヘル": "欧露赫露",
    "ペペ": "佩佩", "ピーテル": "皮特鲁", "セテス": "西提司", "サラン": "沙兰",
    "シモン": "希蒙", "シロッコ": "西洛可", "ソフィア": "索绯雅", "タリムーン": "谭利穆恩",
    "セオドラ": "赛奥朵拉", "ティアラ": "媞雅拉", "トビヤス": "托比亚斯", "トロイア": "特洛伊亚",
    "ウルタンド": "乌尔坦德", "ウーシュラ": "乌修拉", "ヨーカイ": "杨界", "ザーコネ": "札可捏",
}

# Characters present in the support-point table but not the conversation chart.
# Names without a published Chinese equivalent use provisional transliterations.
EXTRA_NAMES = {
    "アンナ": ("Anna", "安娜"),
    "クレオブロス": ("Cleobulus", "克雷欧布罗斯"),
    "ミュソン": ("Myson", "缪森"),
    "アウロラ": ("Aurora", "欧若拉"),
    "グラディウス": ("Gladius", "格拉迪乌斯"),
    "クラプカ": ("Klapka", "克拉普卡"),
    "タホウニア": ("Tahonia", "塔霍尼雅"),
    "ジュラ": ("Jurah", "茱拉"),
    "マーズ": ("Mars", "马兹"),
    "スミルノス": ("Smyrnos", "史米尔诺斯"),
    "クレール": ("Credna", "柯雷尔"),
    "カーラ": ("Kalla", "卡拉"),
}
ALL_NAMES = {**NAMES, **{jp: zh for jp, (_en, zh) in EXTRA_NAMES.items()}}


@lru_cache(maxsize=1)
def _english_index() -> dict[str, str]:
    result = {rec["en"]: jp for jp, rec in supports.chars() if rec.get("en") and jp in NAMES}
    result.update({english: jp for jp, (english, _zh) in EXTRA_NAMES.items()})
    return result


def chinese_name(name: str, pid: str = "", japanese: str = "") -> str | None:
    """Resolve a known character using both the name and its game identifier."""
    english = _english_index()
    jp = japanese.removeprefix("PID_")
    if jp in ALL_NAMES and (name == jp or english.get(name) == jp):
        return ALL_NAMES[jp]
    if pid:
        # Japanese IDs may include a chapter or variant prefix/suffix.
        parts = pid.removeprefix("PID_").split("_")
        for part in parts:
            if part in ALL_NAMES and (name == part or english.get(name) == part):
                return ALL_NAMES[part]
        # Base-unit IDs are English internal keys, while the displayed name
        # comes from the game's English name table (e.g. PID_Kai / Cai).
        if not re.fullmatch(r"PID_[A-Za-z]+", pid):
            return None
    jp = english.get(name)
    return ALL_NAMES.get(jp) if jp else None


def display_name(name: str, pid: str = "", japanese: str = "", chinese: bool = False) -> str:
    return (chinese_name(name, pid, japanese) or name) if chinese else name


def japanese_name(name: str, pid: str = "") -> str:
    """Return a verified Japanese search alias for a recognised save unit."""
    if not chinese_name(name, pid):
        return ""
    return _english_index().get(name, "")
