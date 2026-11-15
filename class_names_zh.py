"""Chinese class labels, keyed by the game's Japanese class identifiers.

The English labels are useful for searching, but are not unique: several
distinct Japanese classes have the same English name. Unknown IDs retain the
original label rather than being assigned an unrelated translation.
"""
from __future__ import annotations

NAMES = {
    "無し": "无", "無職": "无兵种", "闘士": "斗士", "兵士": "士兵", "猟兵": "猎兵",
    "呪い師": "咒术师", "飛駝兵": "飞驼兵", "剣士": "剑士", "アーチャー": "弓箭手",
    "ローグ": "盗贼", "重装歩兵": "重装步兵", "ブリガンド": "山贼", "セスタス": "拳斗士",
    "シャーマン": "萨满", "プリースト": "司祭", "騎甲駝兵": "骑甲驼兵", "軽騎兵": "轻骑兵",
    "天翼兵": "天翼兵", "戦車兵": "战车兵", "シドー": "侍道", "スナイパー": "狙击手",
    "フォレストナイト": "森林骑士", "レンジャー": "游骑兵", "踊り子": "舞者", "ガーディアン": "守护者",
    "ヘヴィアーマー": "重铠兵", "ウォーリアー": "勇士", "鍛冶師": "锻冶师", "ウァテス": "瓦忒斯",
    "ビショップ": "主教", "バーディンガー": "荣光骑士", "カタフラクト": "重装骑兵", "トルバドール": "吟游骑士",
    "カラドリオス": "卡拉德里乌斯", "ドラグーン": "龙骑兵", "戦象兵": "战象兵", "ソードマスター": "剑圣",
    "マスターアーチ": "弓术大师", "ホーリーランサー": "圣枪兵", "ハイエピタフ": "高阶墓志铭", "ボウナイト": "弓骑士",
    "シャドーシーカー": "暗影追寻者", "トリックスター": "诡术师", "バトルマスター": "战斗大师", "フォートレス": "要塞",
    "バトルモンク": "战斗僧侣", "ドルイド": "德鲁伊", "ワイズマン": "贤者", "覚者": "觉者",
    "オリハルディア": "奥利哈铁骑", "グレートナイト": "大骑士", "セーレ": "塞雷", "ヴァルキュリウム": "瓦尔基里乌姆",
    "バイヴ・カハ": "巴伊芙·卡哈", "聖天翼兵": "圣天翼兵", "ドラゴンマスター": "龙骑统帅",
    "ザ・ブレイド": "利刃", "ザ・カラミティ": "灾厄", "ザ・トライデント": "三叉戟", "ジ・アプサラス": "阿普萨拉斯",
    "ジ・エターナル": "永恒者", "ザ・ゴッドハンド": "神之手", "ジ・アヴァタール": "化身", "ザ・キャバリアー": "骑士",
    "クサリク": "库萨里克", "ノブタ": "野猪", "ヤク": "牦牛", "ジャーメル": "杰梅尔", "ネコ": "猫",
    "ワラジムシ": "鼠妇", "サンドバアル": "砂巴尔", "タテジマオオカミ": "条纹狼", "サンドヴィーグル": "砂维格尔",
    "海獣": "海兽", "アトラスベア": "阿特拉斯熊", "アトラスベア小": "阿特拉斯熊（小）", "砂虫": "砂虫", "巨人": "巨人",
    "タイタニス小型": "泰坦尼斯（小型）", "タイタニス大型": "泰坦尼斯（大型）", "ゴーレム": "魔像", "ケートゥス": "凯图斯",
    "ディガンマ": "迪伽玛", "クイン・ヒュドラー": "九头蛇女王", "巨鳥ルフ": "巨鸟鲁赫", "魔鳥ハルピア": "魔鸟鹰身女妖",
    "鎧兵": "铠甲兵", "ウマ": "马", "汗血馬": "汗血马", "黒馬": "黑马", "モノケロース": "独角兽",
    "ペガサス": "天马", "ファルコン": "隼", "オルニウス": "奥尔尼乌斯", "ダグザ竜": "达格扎龙", "バロール竜": "巴罗尔龙",
    "マーズ竜": "玛兹龙", "ライラー竜_２部": "莱拉龙（第 2 部）", "ライラー竜_３部": "莱拉龙（第 3 部）",
    "ライラー繭": "莱拉茧", "レダ召喚魔獣": "蕾达召唤魔兽", "スケルトン歩兵": "骷髅步兵", "スケルトン駝鳥": "骷髅驼鸟",
    "スケルトン騎馬": "骷髅骑兵", "マミー金": "金色木乃伊", "マミー": "木乃伊", "ドラゴンゾンビ": "僵尸龙", "冥界の柱": "冥界之柱",
}

# Internal English identifiers also occur in the class catalogue. These are
# distinct IDs, so label them without replacing or merging their saved keys.
INTERNAL_NAMES = dict(line.split("|", 1) for line in """
None|无
Warrior|斗士
Soldier|士兵
Hunter|猎兵
CurseMage|咒术师
Flyingostrichsoldier|飞驼兵
SwordFighter|剑士
Archer|弓箭手
Rogue|盗贼
ArmorKnight|重装步兵
Brigand|山贼
Cestus|拳斗士
Shaman|萨满
Healer|司祭
Flyingostrichknight|骑甲驼兵
LightKnight|轻骑兵
PegasusKnight|天翼兵
Tank|战车兵
Sydow|侍道
Sniper|狙击手
ForestKnight|森林骑士
Ranger|游骑兵
Dancer|舞者
Guardian|守护者
HeavyArmor|重铠兵
BattleWarrior|勇士
Blacksmith|锻冶师
Vates|瓦忒斯
Bishop|主教
Bardinger|荣光骑士
Cataphract|重装骑兵
Torpador|吟游骑士
Charadrios|卡拉德里乌斯
Dragoon|龙骑兵
ElephantKnight|战象兵
SwordMaster|剑圣
MasterArch|弓术大师
HolyLancer|圣枪兵
HighEpitaph|高阶墓志铭
BowKnight|弓骑士
ShadowSeeker|暗影追寻者
Trickster|诡术师
BattleMaster|战斗大师
Fortress|要塞
BattleMonk|战斗僧侣
Druid|德鲁伊
Wiseman|贤者
Enlightened|觉者
Orihaldia|奥利哈铁骑
GreatKnight|大骑士
Sale|塞雷
Valkyrie|瓦尔基里乌姆
DarkPegasus|巴伊芙·卡哈
FalconKnight|圣天翼兵
DragonMaster|龙骑统帅
Braid|利刃
Calamity|灾厄
Trident|三叉戟
Apsaras|阿普萨拉斯
Eternal|永恒者
Godhand|神之手
Messiah|化身
Cavalier|骑士
Kusarikku|库萨里克
Pig|野猪
Yak|牦牛
woodlouse|鼠妇
sandbael|砂巴尔
stripewolf|条纹狼
sandvegle|砂维格尔
seamonster|海兽
atlasbear|阿特拉斯熊
atlasbearS|阿特拉斯熊（小）
sandworm|砂虫
colossus|巨人
titanusS|泰坦尼斯（小型）
titanusB|泰坦尼斯（大型）
golem|魔像
Ketos|凯图斯
digamma|迪伽玛
queenhydra|九头蛇女王
giantrukh|巨鸟鲁赫
magicharpia|魔鸟鹰身女妖
armoredsoldier|铠甲兵
NabataeanDragon_Dagda|达格扎龙
NabataeanDragon_Balor|巴罗尔龙
NabataeanDragon_Mars|玛兹龙
NabataeanDragon_Lyra|莱拉龙
NabataeanDragon_LyraCradle|莱拉茧
EvilBeast|召唤魔兽
skeleton|骷髅
mummy|木乃伊
dragonzombie|僵尸龙
shadowofbalor|巴罗尔之影
pillar|冥界之柱
""".strip().splitlines())

NAMES.update({"オルニウス白": "白色奥尔尼乌斯", "メガニウス": "梅加尼乌斯",
              "マジニウス": "马吉尼乌斯", "バウ": "巴乌", "ダグザンゾウ": "达格扎象",
              "マミー銀": "银色木乃伊", "バロールの影": "巴罗尔之影"})


def chinese_name(meta: dict | None) -> str | None:
    jp = (meta or {}).get("jp", "").removeprefix("JID_")
    if jp.startswith("H_"):
        base = jp[2:]
        translated = NAMES.get(base) or INTERNAL_NAMES.get(base)
        return translated + "（内部 H）" if translated else None
    if jp in NAMES:
        return NAMES[jp]
    if jp in INTERNAL_NAMES:
        return INTERNAL_NAMES[jp] + "（内部）"
    if jp.endswith("下馬") and jp[:-2] in NAMES:
        return NAMES[jp[:-2]] + "（下马）"
    return None


def display_name(meta: dict | None, fallback: str, chinese: bool) -> str:
    return (chinese_name(meta) or fallback) if chinese else fallback
