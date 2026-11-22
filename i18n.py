"""Small runtime localisation layer for the Tk interface.

The editor predates localisation and creates widgets in several modules.  This
module keeps the original English string on each widget and translates it at
the Tk boundary.  That gives dialogs, table headings and strings generated at
runtime the same behaviour without coupling save-file code to the UI language.
"""
from __future__ import annotations

import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

LANGUAGES = ("en", "zh_CN")
_language = "en"
_installed = False


# Complete static UI vocabulary.  Runtime messages are handled by the phrase
# table below, while proper names and game-internal identifiers stay unchanged.
ZH = {
    "Add a class": "添加兵种", "Pick the unit's current class": "选择角色的当前兵种",
    "World map": "世界地图", "Places": "地点", "Roads": "道路",
    "Junctions & road points": "岔路与道路点", "Mark unvisited": "标记为未到访",
    "Mark visited": "标记为已到访", "Hide": "隐藏", "Show": "显示",
    "Everything at once:": "批量操作：", "Show all places": "显示所有地点",
    "Show all roads": "显示所有道路", "also mark those places visited": "同时将这些地点标记为已到访",
    "Game name": "游戏日文名称", "Kind": "类型", "On the map": "地图显示", "Visited": "已到访",
    "Hidden": "隐藏", "Shown": "显示", "State 2": "状态 2", "Yes": "是", "No": "否",
    "Major city": "主要城市", "Town": "城镇", "Temple": "神殿", "Station": "驿站",
    "Gate / fortress": "关卡／要塞", "Landmark": "地标", "Field / pass": "原野／山道",
    "Shrine / monument": "祠堂／纪念碑", "Cave / mine": "洞窟／矿山",
    "Waypoint": "中间点", "Junction": "岔路点", "Road point": "道路点",
    "map_spots.json is missing — the map can't be named.": "缺少 map_spots.json，无法显示地图地点名称。",
    "map_spots.json is missing, so the map points can't be named.": "缺少 map_spots.json，无法显示地图地点名称。",
    "Open a save to see its map.": "请打开存档以查看世界地图。",
    "This save has no world-map block.": "此存档没有世界地图数据块。",
    "Couldn't find the world-map block in the save's object tree.": "无法在存档的对象树中找到世界地图数据块。",
    "Unexpected world-map block boundaries.": "世界地图数据块的边界不符合预期。",
    "Duplicate world-map key - the layout isn't the expected one.": "世界地图键值重复，数据布局不符合预期。",
    "Pick a row first.": "请先选择一行。",
    "That road has no points of its own to hide — it joins two places directly.": "这条道路直接连接两个地点，没有可单独隐藏的道路点。",
    "A visited mark applies to places, not to roads.": "到访标记适用于地点，不能应用于道路。",
    "Open a save with a world map first.": "请先打开包含世界地图的存档。",
    "Every place is already on the map.": "所有地点已显示在地图上。",
    "Every junction and road point is already shown.": "所有岔路点和道路点均已显示。",
    "%d of %d": "%d / %d", "%d points": "%d 个点", "state %d": "状态 %d",
    "%d of %d places on the map · listing %d of %d": "地图上显示 %d / %d 个地点 · 列出 %d / %d 项",
    "marked visited": "标记为已到访", "marked unvisited": "标记为未到访",
    "%s — %d skipped (a layout or value the editor hasn't seen) — Ctrl+S to write it.": "%s — 已跳过 %d 项（编辑器未识别其布局或数值）— 按 Ctrl+S 写入文件。",
    "Showed %d places": "已显示 %d 个地点", "Showed %d junctions and road points": "已显示 %d 个岔路点和道路点",
    "Show %d hidden junctions and road points?\n\nThis draws every road the game has, including ones the story hasn't opened yet. Ctrl+Z undoes it.": "显示 %d 个隐藏的岔路点和道路点？\n\n这会绘制游戏中的所有道路，包括剧情尚未开放的道路。按 Ctrl+Z 可撤销。",
    "“Shown” makes a point appear on the world map; it does not open anything behind it — gates, battles, rewards, quests and fast travel keep their own conditions. “Visited” is the white versus the dark icon. Roads are drawn through their own points, so showing a road also shows the places and junctions at its ends; hiding one only hides the points that belong to that road. “State 2” is a value the game writes on some road points that isn't understood yet: it is listed as it is and changed only if you pick it. Close the game and keep a backup before you write.": "“显示”会让地点出现在世界地图上，但不会解除关卡、战斗、奖励、任务或快速旅行各自的解锁条件。“已到访”决定图标显示为白色还是深色。道路由自身的道路点连接而成：显示道路时也会显示两端的地点和岔路点；隐藏道路时只隐藏该道路自身的点。“状态 2”是游戏在部分道路点写入的值，其含义尚不明确；编辑器会原样显示，仅在选择修改时更改。写入前请关闭游戏并备份存档。",
    "Fortune's Weave Save Editor": "《火焰之纹：命运之织》存档编辑器",
    "Fortune's Weave": "火焰之纹：命运之织",
    "SAVE EDITOR": "存档编辑器",
    "Save editor": "存档编辑器",
    "Save": "保存", "Reload": "重新载入", "⟳ Reload": "⟳ 重新载入",
    "Snapshot": "创建快照", "Restore…": "恢复…", "Slot": "存档槽",
    "Open folder…": "打开文件夹…", "Also edit this route's other saves": "同时编辑本路线的其他存档",
    "Ready": "就绪", "Units": "角色", "Convoy": "仓库", "Gold": "金钱",
    "Supports": "支援", "Player": "玩家", "Classes": "兵种", "Flags": "标记",
    "Mounts": "坐骑", "Stats": "属性", "Inventory": "物品栏", "Class": "兵种",
    "Arts & skills": "战技与技能", "Item catalogue": "物品目录", "Type": "类型",
    "Internal duplicates": "显示内部重复项", "Double-click or Enter also works": "也可双击或按 Enter",
    "Item": "物品", "Japanese": "日文", "Id": "ID", "Name": "名称",
    "Internal id": "内部 ID", "Use this": "使用此项", "Cancel": "取消", "OK": "确定",
    "All types": "全部类型", "No unit selected": "未选择角色", "Open a save folder to begin.": "请先打开存档文件夹。",
    "Show enemies & NPCs": "显示敌人与 NPC", "Copy unit in…": "导入角色…",
    "Remove unit": "移除角色", "Make copies match": "同步所有副本", "Lv": "等级",
    "LEVEL": "等级", "EXP": "经验", "MAX HP": "最大 HP", "HP": "HP",
    "Points gained from level-ups": "升级获得的属性点",
    "These are what the unit has gained from levelling, not the totals shown in game: the game adds them to the unit's class and personal bases, and stat-up items aren't included. Raising one raises the in-game stat by the same amount.": "这里显示的是角色升级获得的属性点，并非游戏中显示的最终属性值。游戏会将这些属性点加到角色的兵种基础值和个人基础值上，且不包含属性提升道具的效果。此处每增加 1 点，游戏中的对应属性也会增加 1 点。",
    "Changing HP gained moves max HP with it. Edits apply on Enter / Tab; every field can be undone.": "修改 HP 成长值会同步改变最大 HP。按 Enter 或 Tab 应用；所有修改均可撤销。",
    "Carried items": "携带物品", "Select a slot, then choose its replacement.": "选择一个栏位，再选择替换物品。",
    "Allow any item type (can break the game)": "允许任意物品类型（可能损坏游戏）",
    "Add item…": "添加物品…", "Remove item": "移除物品", "Current class": "当前兵种",
    "Include monster / internal classes": "包含怪物／内部兵种", "Change class": "更改兵种",
    "Only the class id is written. Movement, usable weapons, class skills and animations are not recalculated.": "只写入兵种 ID；移动力、可用武器、兵种技能和动画不会重新计算。",
    "Internal name": "内部名称", "Everything in storage, materials included, by slot.": "按栏位显示仓库中的全部内容（包括材料）。",
    "Repair convoy": "修复仓库", "Slot · Item": "栏位 · 物品", "Qty": "数量", "Quantity": "数量",
    "Set qty": "设置数量", "Remove": "移除", "GOLD": "金钱", "New amount": "新数额",
    "Set gold": "设置金钱", "Support conversations": "支援对话",
    "Add to the convoy": "添加到仓库",
    "Pairs whose C/B/A conversations the game data defines.": "游戏数据中定义了 C／B／A 对话的组合。",
    "Only characters in this save": "仅显示此存档中的角色", "Character": "角色", "Pairs": "组合",
    "No character selected": "未选择角色", "Open a save to see what it records.": "打开存档以查看其中的记录。",
    "Points are what the game turns into a support level: 3200 is the maximum (level 5). The save keeps a slot for every pair, so a pair whose support hasn't opened yet still has a value here — the game may not show it until it opens the relationship itself. “Seen” is the save's 支援会話 flag for a conversation; Max is the highest rank the game data gives the pair.": "游戏会将支援点数转换为支援等级：上限为 3200 点（等级 5）。存档会为每组角色保留一个数值，因此即使尚未解锁支援，这里也会显示点数；游戏可能要等到解锁该支援关系后才会显示。“已观看”对应存档中该对话的支援会話标记；“最高”等级是游戏数据中该组合可达到的最高支援等级。",
    "Support partner": "支援对象", "Max": "最高", "Conversations seen": "已观看对话",
    "In party": "队伍中", "Record conversation as seen:": "将对话标记为已观看：", "Forget…": "清除…",
    "Army-wide values, stored in GameUserData at the start of the save.": "全军共享数值，存储在存档开头的 GameUserData 中。",
    "Renown exp": "声望经验", "Karma Shards": "业力碎片", "Run settings": "周目设置",
    "Written into every copy the save keeps (header, summary and each restart point).": "写入存档保留的每个副本（文件头、摘要和各重启点）。",
    "Difficulty": "难度", "Mode": "模式", "Normal": "普通", "Hard": "困难", "Maddening": "超难",
    "Casual": "休闲", "Classic": "经典", "No unit selected": "未选择角色",
    "Current class": "当前兵种", "Change…": "更改…", "Classes this unit has": "该角色拥有的兵种",
    "Add…": "添加…", "Swap…": "替换…", "Value": "数值", "Weapon masteries": "武器熟练度",
    "Weapon": "武器", "Rank": "等级", "Exp": "经验", "Next rank at": "下一级所需",
    "Saved flags": "已保存标记", "Add flag…": "添加标记…", "Set value…": "设置数值…",
    "Reads as": "含义", "List": "列表", "Battalions & mounts": "骑士团与坐骑",
    "Each unit carries one battalion (and, for mounted classes, one mount) at the end of its record. Pick from the pool this save holds.": "每个角色记录末尾包含一个骑士团（骑乘兵种还包含一个坐骑）。请从本存档的资源池中选择。",
    "Unit": "角色", "Battalion": "骑士团", "Mount": "坐骑", "This save's pool": "本存档的资源池",
    "Entry": "条目", "Kind": "类别", "Record id": "记录 ID", "Assign to unit": "分配给角色",
    "Clear unit's": "清除角色分配", "Remove from pool": "从资源池移除",
    "(empty)": "（空）", "Spell": "法术", "SPELLS  (read-only)": "法术（只读）",
    "Nothing to show": "没有可显示的内容", "No save folder open": "尚未打开存档文件夹",
    "All changes saved": "所有修改均已保存", "Save slots": "存档槽", "All files": "所有文件",
    "Pick a snapshot to restore": "选择要恢复的快照", "Copy a unit from which save?": "从哪个存档导入角色？",
    "Open any slot in your save folder": "打开存档文件夹中的任意存档槽",
    "How many?": "数量是多少？", "Search by name, Japanese name or id…": "按名称、日文名或 ID 搜索…",
    "Search units or classes…  (Ctrl+F)": "搜索角色或兵种…  (Ctrl+F)", "Search classes…": "搜索兵种…",
    "Filter the convoy…": "筛选仓库…", "Search characters…": "搜索角色…",
    "Search flags…": "搜索标记…", "Search by name or id…": "按名称或 ID 搜索…",
    "Sword": "剑", "Lance": "枪", "Axe": "斧", "Bow": "弓", "Tome": "魔法书",
    "Staff": "杖", "Fist": "格斗", "Shield": "盾", "Weapon": "武器", "Accessory": "饰品",
    "Consumable": "消耗品", "Black Magic": "黑魔法", "White Magic": "白魔法", "Special": "特殊",
    "Foot": "步兵", "Cavalry": "骑马", "Heavy": "重装", "Fly": "飞行", "Tactics": "指挥",
    "Put in selected slot": "放入所选栏位", "Put in selected row": "放入所选行",
    "Set current": "设为当前", "Set rank…": "设置等级…", "Set exp…": "设置经验…",
    "All": "全部", "Recruited": "已招募", "Met": "已见面", "Achievements": "成就",
    "Expansion classes": "扩展兵种", "Equipped arts": "已装备战技", "Equipped skills": "已装备技能",
    "List 3": "列表 3", "Arts known": "已掌握战技", "List 5": "列表 5", "Learned (all)": "全部已学会",
    "Hit points": "生命值", "Strength": "力量", "Magic": "魔力", "Dexterity": "技巧",
    "Speed": "速度", "Luck": "幸运", "Defense": "防御", "Resistance": "魔防", "Charm": "魅力",
    "Carrying nothing": "未携带物品", "weapons": "武器", "accessories": "饰品", "consumables": "消耗品",
    "Use “Open folder…” (Ctrl+O) and pick any slot file (Auto, Chapter_*, Route_*) inside your save folder.": "点击“打开文件夹…”（Ctrl+O），并选择存档文件夹中的任意存档槽文件（Auto、Chapter_* 或 Route_*）。",
    "Open a save, or untick “Only characters in this save”.": "请打开存档，或取消勾选“仅显示此存档中的角色”。",
    "Changing HP gained moves max HP with it. Edits apply on Enter / Tab; Save writes them.": "修改 HP 成长值会同步改变最大 HP。按 Enter 或 Tab 应用，点击“保存”写入文件。",
    "Renown exp is the army's total; the level itself follows the game's own Reward.bin table, so set a value between two levels to land on a level.": "声望经验是全军总值；等级由游戏自身的 Reward.bin 表决定。可将数值设在两个等级阈值之间以达到对应等级。",
    "Flags are the game's named variables: 支援会話_<A>_<B>_<rank> marks a support conversation as seen, 加入_ a recruited character, 面識_ a met one, 実績_ an achievement counter. A name the data files don't contain shows as its hash — that is a real flag, just one the editor can't name.": "标记是游戏的命名变量：支援会話_<A>_<B>_<等级> 表示已观看支援对话，加入_ 表示已招募角色，面識_ 表示已见面，実績_ 表示成就计数。数据文件中没有名称的标记会显示为哈希值；它仍是真实标记，只是编辑器无法命名。",
    "No Eden save folder found automatically — open one to begin.": "未能自动找到 Eden 存档文件夹；请打开一个文件夹以开始。",
    "Re-read every slot from disk.": "已从磁盘重新读取所有存档槽。",
    "Gold is read straight from the save — nothing to search for.": "金钱直接从存档读取，无需搜索。",
    "This slot's convoy doesn't need repairing.": "此存档槽的仓库无需修复。",
    "Select one convoy row to replace (any spare item you put there in game).": "选择一个要替换的仓库行（可选择你在游戏中放入的任意备用物品）。",
    "No skill names available (skill_ids.json is missing).": "没有可用的技能名称（缺少 skill_ids.json）。",
    "Pick a battalion in the pool first.": "请先在资源池中选择骑士团。",
    "This save has no flag list to add to.": "此存档没有可供添加的标记列表。",
    "Pick a support partner on the Supports page first.": "请先在“支援”页面选择支援对象。",
    "This pair has no conversations in the game data.": "游戏数据中没有此组合的对话。",
    "Only battalions can be assigned here.": "此处只能分配骑士团。",
    "Met": "已见面", "Support conversation": "支援对话", "Achievement": "成就",
    "Feature unlocked": "功能已解锁", "Class unlocked": "兵种已解锁", "Disabled": "已禁用",
    "Boon": "恩惠", "Situation": "状况", "Settings": "设置", "Read": "已读",
    "Shared": "共享", "Tutorial": "教程", "Fast travel": "快速旅行", "Talk": "对话",
    "today ": "今天 ", "this slot": "此存档槽",
    "Edits now also go into this route's other saves (never chapter checkpoints).": "修改现在也会应用到本路线的其他存档（绝不会修改章节检查点）。",
    "Edits now go into the selected slot only.": "修改现在仅应用到所选存档槽。",
    "Nothing changed — that unit has no such item slot here.": "没有发生修改；该角色在此处没有对应的物品栏位。",
    "One of the fields isn't a valid number.": "某个字段不是有效数字。",
    "The unit already has every weapon mastery.": "该角色已拥有全部武器熟练度。",
    "This pair has no conversations in the game data.": "游戏数据中没有此组合的对话。",
    "Pick a unit on the Mounts page first.": "请先在“坐骑”页面选择角色。",
    "Pick a convoy row first.": "请先选择仓库行。",
    "Nothing to save — no changes yet.": "尚无修改，无需保存。",
    "No convoy list found in this slot": "此存档槽中未找到仓库列表",
    "This slot's convoy list is damaged — see above": "此存档槽的仓库列表已损坏，请参见上方提示",
}


PHRASES = [
    ("Pick an item from the catalogue first.", "请先从目录中选择物品。"),
    ("Pick an inventory slot first.", "请先选择物品栏位。"),
    ("Pick a unit first.", "请先选择角色。"),
    ("Pick a class from the list first.", "请先从列表中选择兵种。"),
    ("Pick a convoy row first.", "请先选择仓库行。"),
    ("Select a convoy row first.", "请先选择仓库行。"),
    ("Nothing to save — no changes yet.", "没有需要保存的内容。"),
    ("Nothing to undo.", "没有可撤销的操作。"), ("Nothing to redo.", "没有可重做的操作。"),
    ("Undone — Ctrl+Y puts it back.", "已撤销；按 Ctrl+Y 可重做。"), ("Redone.", "已重做。"),
    ("No snapshots yet — press Snapshot first.", "尚无快照；请先创建快照。"),
    ("Type the new gold amount as a number.", "请输入数字形式的新金钱数额。"),
    ("Gold must be between", "金钱必须介于"), ("Quantity must be", "数量必须为"),
    ("All changes saved", "所有修改均已保存"), ("with unsaved changes", "有未保存的修改"),
    ("Saved ", "已保存 "), ("Opened ", "已打开 "), ("Restored ", "已恢复 "),
    ("Snapshot of ", "已为 "), (" slots saved to ", " 个存档槽创建快照并保存到 "),
    (" match", " 个匹配项"), ("first ", "前 "), (" unit", " 个角色"),
    ("Playthrough ", "周目 "), ("Level ", "等级 "), ("live record", "当前记录"),
    ("every slot:", "所有存档槽："), ("slots disagree —", "存档槽设置不一致 —"),
    ("read-only", "只读"), ("Enemy / NPC", "敌人／NPC"),
    ("Current", "当前"), ("added ", "已添加 "), ("removed ", "已移除 "),
    ("unknown ", "未知 "), (" in this file", "（本文件）"), (" of ", " / "),
    ("This file's GameUserData isn't the known layout.", "此文件的 GameUserData 不是已知布局。"),
    ("That row already holds this item.", "该行已经是此物品。"),
    ("That slot already holds this item.", "该栏位已经是此物品。"),
    ("One of the fields isn't a valid number.", "某个字段不是有效数字。"),
    ("Enemy and NPC records are read-only", "敌人和 NPC 记录为只读"),
    ("Can't read ", "无法读取 "), ("Couldn't apply ", "无法应用 "),
    ("Press Reload", "请按“重新载入”"), ("Ctrl+S to write it.", "按 Ctrl+S 写入文件。"),
    ("Fortune's Weave Save Editor", "《火焰之纹：命运之织》存档编辑器"),
    ("No save folder found", "未找到存档文件夹"), ("No save folder open", "尚未打开存档文件夹"),
    ("The game saved a slot", "游戏已写入一个存档槽"), ("unsaved edits", "未保存的修改"),
    ("Saving now would overwrite the game's progress.", "现在保存会覆盖游戏进度。"),
    ("Reload to start again from the game's save.", "请重新载入游戏存档后再开始修改。"),
    ("Pick a support partner", "请选择支援对象"), ("conversation in the game data", "游戏数据中的对话"),
    ("Also edit this route's other saves", "同时编辑本路线的其他存档"),
    ("saves of this route", "个本路线存档"), (" in this route", "（本路线）"),
    ("off in checkpoints", "检查点中关闭"), ("none here", "此处无其他存档"),
    ("Picked up a newer save from the game:", "已读取游戏生成的较新存档："),
    ("Some slots could not be written:", "部分存档槽无法写入："),
    ("Is the game still running?", "游戏是否仍在运行？"),
    ("Originals kept as .bak next to each slot.", "原文件已作为 .bak 保留在各存档槽旁。"),
    ("Save them before you open another folder?", "是否在打开其他文件夹前保存？"),
    ("Save them before you quit?", "是否在退出前保存？"),
    ("Reload from disk and throw away the unsaved changes", "从磁盘重新载入并丢弃未保存的修改"),
    ("Overwrite anyway?", "仍要覆盖吗？"), ("Not saved", "未保存"),
    ("the game's newer save was kept", "已保留游戏生成的较新存档"),
    ("redo your edits", "重新进行修改"), ("level →", "等级 →"),
    ("every copy now matches the values shown", "所有副本现已与显示的数值一致"),
    ("must be a number from", "必须是以下范围内的数字："),
    ("Carrying nothing", "未携带物品"), ("Couldn't find this unit's item list", "找不到该角色的物品列表"),
    ("Quantity →", "数量 →"), ("Convoy slot", "仓库栏位"), ("Convoy repaired", "仓库已修复"),
    ("Pick a unit", "请选择角色"), ("Pick a class", "请选择兵种"),
    ("Pick a battalion", "请选择骑士团"), ("Pick an inventory slot", "请选择物品栏位"),
]



from new_feature_names_zh import NAMES as _FEATURE_NAMES_ZH
ZH.update(_FEATURE_NAMES_ZH)
ZH.update({
    'Tutorials': '教程', 'Blessings': '加护', 'Functions': '功能',
    'Notable Deeds': '伟业录', 'Boons': '救世的祝福', 'Boons of Salvation': '救世的祝福',
    'Karma Shards': '因果碎片', 'Add to save': '添加到存档', 'Remove selected': '移除所选项', 'Select shown': '选择显示项',
    'All categories': '所有类别', 'All names': '所有名称', 'All states': '所有状态', 'Absent': '未保存', 'Stored (2)': '已存储（2）', 'Present (1)': '存在（1）', 'Unknown': '未知',
    'Game title checked': '游戏标题已核对', 'Provisional name': '暂定名称', 'Name evidence': '名称依据', 'Stored state': '存储状态', 'Category': '类别',
    'Battle': '战斗', 'Bases': '据点', 'The World Map': '世界地图', 'Dungeons': '迷宫', 'Flame Lords': '真焰将', 'Scenario-specific': '特定剧情',
    'God': '神明', 'Stored EXP': '已存经验值', 'Level preview': '等级预览', 'Selected (stored)': '已选择（存储值）', 'First audience': '首次觐见', 'First audience recorded': '已记录首次觐见', 'New EXP': '新经验值', 'Apply EXP': '应用经验值', 'Special / unknown': '特殊／未知', 'Yes (1)': '是（1）', 'No (0)': '否（0）',
    'Fortuna': '芙托娜', 'Mars': '玛兹', 'Credna': '克蕾尔', 'Kalla': '卡拉', 'Jurah': '朱拉', 'Smyrnos': '斯米尔诺斯', 'Aurora': '奥萝拉',
    'Saved switches': '已存开关', 'Access conditions': '进入条件', 'Function switches': '功能开关', 'All switches': '所有开关', 'Service': '设施服务', 'Gate registration': '神殿大门登记', 'Journal': '冒险手册', 'Area access': '区域进入', 'Enable selected': '启用所选项', 'Disable selected': '禁用所选项', 'Copy diagnostics': '复制诊断信息', 'Function / facility': '功能／设施', 'Saved switch': '存储的开关', 'Saved evidence': '存储依据', 'Route / prerequisite': '路线／前提条件', 'Access / entrance': '进入／入口', 'Inferred': '推测', 'Game-tested': '游戏内已测试', 'Conditional pass': '有条件通过',
    'New total': '新累计值', 'Apply progress': '应用进度', 'Use selected target': '使用所选目标值', 'Activity · milestone target': '活动 · 里程碑目标', 'Claim state (stored)': '领取状态（存储值）', 'Milestone hash': '里程碑哈希', 'Counter editing': '计数器编辑', 'Previously claimed rewards': '先前领取的奖励', '0 (not stored)': '0（未存储）',
    'Set selected tier': '设置所选等级', 'Set all to max': '全部设为最高等级', 'Turn on': '启用', 'Turn off': '停用', 'Remove Boon': '移除祝福', 'Game cost': '游戏内花费', 'Required clears': '所需通关次数', 'Saved state': '存储状态', 'Not owned': '未拥有', 'Tier': '等级', 'Evidence': '依据', 'Effect': '效果',
    'Open a save to see its tutorials.': '打开存档以查看教程。', 'Open a save to see its blessings.': '打开存档以查看加护。', 'Open a save to see its saved function switches.': '打开存档以查看已存功能开关。', 'Open a save to inspect access conditions.': '打开存档以查看进入条件。', 'Open a save to see its Notable Deeds.': '打开存档以查看伟业录。', 'Open a save to inspect its Boons.': '打开存档以查看救世的祝福。',
    'Select a tutorial for its naming evidence.': '选择教程以查看名称依据。', 'Select a god to edit its stored EXP.': '选择神明以编辑已存经验值。', 'Select a god to inspect its first-audience condition.': '选择神明以查看首次觐见条件。', 'Select a switch to see its evidence and limits.': '选择开关以查看依据和限制。', 'Select a destination for the known conditions.': '选择目的地以查看已知条件。', 'Select a milestone to view its activity total. Rewards and claim states are read-only.': '选择里程碑以查看活动累计值。奖励和领取状态为只读。',
    'Read-only data conditions. Arena has no verified saved switch yet. Recorded flags do not guarantee access.': '以下条件为只读数据。竞技场尚无经验证的存档开关；记录的标记不保证能够进入。',
    'You are about to unclaim some previously claimed rewards. Continue anyway?': '此操作可能导致已领取的部分奖励被游戏重置为未领取。仍要继续吗？',
    'Select one or more tutorials first.': '请先选择一个或多个教程。', 'Select one or more function switches first.': '请先选择一个或多个功能开关。', 'Select one god first.': '请先选择一位神明。', 'Select one milestone first.': '请先选择一个里程碑。', 'Select a Boon tier first.': '请先选择祝福等级。', 'Select the owned Boon tier first.': '请先选择已拥有的祝福等级。', 'Open a save first.': '请先打开存档。',
    'EXP must be a whole number from 0 to 65535.': '经验值必须是 0 到 65535 之间的整数。', 'Enter a whole-number activity total.': '请输入整数活动累计值。',
})
PHRASES.extend([
    ('Edit one god at a time. Level previews use game-data thresholds; Fortuna is special. The audience toggle changes only the first-talk flag; other access conditions may still apply. Audience edits leave EXP, selected blessings, Divine Sand and travel destinations unchanged.', '每次编辑一位神明。等级预览使用游戏数据中的阈值；芙托娜属于特殊情况。首次觐见开关只改变首次对话标记，其他进入条件仍可能生效。修改首次觐见不会改变经验值、已选加护、天刻白沙或移动目的地。'),
    ('Threshold buttons fill New EXP; click Apply EXP to use that value.', '阈值按钮会填入新经验值；点击“应用经验值”才会使用该数值。'),
    ('On records the first audience; off removes that record. Save to write the change.', '开启会记录首次觐见，关闭会移除该记录。保存后才会写入。'),
    ('Checkbox applies immediately in memory, like other page actions.', '与本页其他操作一样，勾选后会立即应用到内存。'),
    ('Fortuna has no first-audience condition in the game data; no flag is written.', '游戏数据中芙托娜没有首次觐见条件，不会写入标记。'),
    ('EXP effect unknown; no Blessings-screen change reported at EXP 1 or 65535.', '经验值效果未知；据报告，经验值为 1 或 65535 时加护画面没有变化。'),
    ('Select the currently owned tier to switch this Boon On or Off.', '选择当前拥有的等级，以启用或停用此祝福。'),
    ('Select the owned tier to use Turn on/off.', '选择已拥有的等级后即可启用或停用。'),
    ('Tier edits keep the current On/Off switch.', '修改等级会保留当前启用状态。'),
    ('Editing does not spend Karma or change clears.', '编辑不会消耗因果碎片，也不会改变通关次数。'),
    ('The game can clear these claims when it loads the edited save. The editor keeps the stored claim flags and Karma Shards unchanged.', '游戏加载修改后的存档时可能清除这些领取记录。编辑器会保留存档中的领取标记和因果碎片。'),
    ('Search English, Japanese or hash. Add to save stores the selected records; the game controls menu visibility and can unlock tutorials again during play. Select shown uses the current filters; other entries stay saved. Unknown states are preserved.', '可搜索中文、英文、日文或哈希。“添加到存档”会保存所选记录；菜单显示由游戏决定，游戏过程中也可能再次解锁教程。“选择显示项”使用当前筛选条件，其他记录及未知状态会保留。'),
    ('English title is provisional and absent from the supplied screenshots. If it appears during normal play, a title screenshot would help confirm it.', '英文标题为暂定名称，尚未见于所提供的截图；若在游戏中出现，可通过标题截图确认。'),
    ('English title, category and order match the supplied in-game screenshots. This verifies the name, not feature unlocks or availability on every route.', '英文标题、类别和顺序与游戏截图一致；这只验证名称，不代表功能已解锁或所有路线均可使用。'),
    ('Scenario-specific is an editor category, separate from Battle. These records are absent from the tested in-game Tutorials menus even when saved as 2. Whether they appear during their matching scenarios is unverified.', '特定剧情是编辑器的分类，与战斗分类分开。这些记录即使保存为 2，也未在测试过的游戏教程菜单中出现；是否会在对应剧情中出现尚未验证。'),
    ('Enable/Disable changes only the selected saved switches. Enabling movement clears its restriction; area-unlock switches are separate. Route, story and NPC conditions may still limit access. Gate registrations are separate from ordinary fast travel.', '启用或禁用仅影响选中的存档开关。启用行动范围会清除其限制；区域解锁开关另行设置。路线、剧情和 NPC 条件仍可能限制进入。神殿大门登记与普通快速移动分别管理。'),
    ('Stables stays unchanged unless selected. Uses the same-route mirroring selection. Ctrl+Z undoes; Ctrl+S saves.', '未选中马厩时不会更改马厩。遵循同路线存档同步设置。Ctrl+Z 撤销，Ctrl+S 保存。'),
    ('Edit one activity total; it feeds every milestone for that activity. Claim rewards in game. The game can clear claimed rewards if their progress falls below target. Unlisted milestones may have game conditions.', '编辑某项活动的累计值会影响其全部里程碑。请在游戏中领取奖励；若进度低于目标，游戏可能清除已领取的奖励。未列出的里程碑可能有额外游戏条件。'),
    ('Select a tier, then Set selected tier. Each Boon has one owned tier and an independent On/Off switch.', '选择等级后点击“设置所选等级”。每项祝福拥有一个等级和独立的启用开关。'),
    ('Set all to max affects all 31 Boons, including rows hidden by search. Undo restores the whole edit.', '全部设为最高等级会影响全部 31 项祝福，包括搜索隐藏的项目。撤销可还原整次修改。'),
    ('Uses the same-route mirroring selection. Ctrl+S saves, Ctrl+Z undoes, Ctrl+Y redoes.', '遵循同路线存档同步设置。Ctrl+S 保存，Ctrl+Z 撤销，Ctrl+Y 重做。'),
    ('Uses the same-route mirroring selection.', '遵循同路线存档同步设置。'),
    ('Ctrl+Z undoes an edit; Ctrl+S writes it.', '按 Ctrl+Z 撤销，按 Ctrl+S 保存。'),
    ('Stored state does not guarantee menu visibility in every context, and adding a tutorial does not unlock the feature it describes.', '存储状态不保证教程在所有情况下出现在菜单中；添加教程不会解锁其介绍的功能。'),
    ('Tier edits preserve Karma and progression. Set all to max preserves each On/Off switch.', '修改等级不会改变因果碎片和游戏进度。全部设为最高等级会保留各项的启用状态。'),
    ('Inferred', '推测'), ('Game-tested', '游戏内已测试'),
])


def set_language(language: str) -> None:
    global _language
    _language = language if language in LANGUAGES else "en"


def get_language() -> str:
    return _language


def source(value):
    """Return the English source for a translated fixed choice."""
    if not isinstance(value, str):
        return value
    reverse = {translated: english for english, translated in ZH.items()}
    return reverse.get(value, value)


def tr(value):
    """Translate a UI value, leaving ids, paths and game proper names intact."""
    if _language != "zh_CN" or not isinstance(value, str) or not value:
        return value
    if value in ZH:
        return ZH[value]
    stripped = value.strip()
    if stripped in ZH:
        start = len(value) - len(value.lstrip())
        end = len(value) - len(value.rstrip())
        return value[:start] + ZH[stripped] + (value[len(value) - end:] if end else "")
    # Translate version subtitle without tying the table to a release number.
    if value.startswith("SAVE EDITOR  ·  v"):
        return "存档编辑器  ·  v" + value.split("v", 1)[1]
    patterns = (
        (r"^(\d+) cop(?:y|ies)$", lambda m: f"{m.group(1)} 个副本"),
        (r"^(\d+) units?$", lambda m: f"{m.group(1)} 个角色"),
        (r"^(\d+) characters?$", lambda m: f"{m.group(1)} 个角色"),
        (r"^([\d,]+) matches?( · first ([\d,]+))?$",
         lambda m: f"{m.group(1)} 个匹配项" + (f" · 前 {m.group(3)} 项" if m.group(3) else "")),
        (r"^● (\d+) slots? with unsaved changes$", lambda m: f"● {m.group(1)} 个存档槽有未保存的修改"),
        (r"^ in (\d+) slots$", lambda m: f"（{m.group(1)} 个存档槽）"),
        (r"^This save's map points don't match the catalogue \((\d+) of (\d+) found\) - another game version\?$",
         lambda m: f"此存档的地图点与目录不匹配（找到 {m.group(1)} / {m.group(2)} 个）；游戏版本可能不同。"),
    )
    for pattern, render in patterns:
        match = re.match(pattern, value)
        if match:
            return render(match)
    out = value
    for en, zh in PHRASES:
        out = out.replace(en, zh)
    return out


def _translated_values(values):
    if isinstance(values, (tuple, list)):
        return type(values)(tr(v) for v in values)
    return values


def install() -> None:
    """Install translation hooks once, before the application creates widgets."""
    global _installed
    if _installed:
        return
    _installed = True

    for cls in (ttk.Label, ttk.Button, ttk.Checkbutton, ttk.Labelframe):
        original_init = cls.__init__

        def init(self, *args, _orig=original_init, **kwargs):
            if "text" in kwargs:
                self._i18n_text = kwargs["text"]
                kwargs["text"] = tr(kwargs["text"])
            _orig(self, *args, **kwargs)
        cls.__init__ = init

        original_configure = cls.configure

        def configure(self, cnf=None, _orig=original_configure, **kwargs):
            if isinstance(cnf, dict):
                kwargs = {**cnf, **kwargs}
                cnf = None
            if "text" in kwargs:
                self._i18n_text = kwargs["text"]
                kwargs["text"] = tr(kwargs["text"])
            return _orig(self, cnf, **kwargs) if cnf is not None else _orig(self, **kwargs)
        cls.configure = configure
        cls.config = configure

    original_combo_init = ttk.Combobox.__init__
    def combo_init(self, *args, **kwargs):
        if "values" in kwargs:
            self._i18n_values = kwargs["values"]
            kwargs["values"] = _translated_values(kwargs["values"])
        original_combo_init(self, *args, **kwargs)
    ttk.Combobox.__init__ = combo_init

    original_add = ttk.Notebook.add
    def notebook_add(self, child, **kwargs):
        if "text" in kwargs:
            self._i18n_tabs = getattr(self, "_i18n_tabs", {})
            self._i18n_tabs[str(child)] = kwargs["text"]
            kwargs["text"] = tr(kwargs["text"])
        return original_add(self, child, **kwargs)
    ttk.Notebook.add = notebook_add

    original_heading = ttk.Treeview.heading
    def heading(self, column, option=None, **kwargs):
        if "text" in kwargs:
            self._i18n_headings = getattr(self, "_i18n_headings", {})
            self._i18n_headings[column] = kwargs["text"]
            kwargs["text"] = tr(kwargs["text"])
        return original_heading(self, column, option, **kwargs)
    ttk.Treeview.heading = heading

    original_insert = ttk.Treeview.insert
    def insert(self, parent, index, iid=None, **kwargs):
        source_text = kwargs.get("text")
        source_values = kwargs.get("values")
        if source_text is not None:
            kwargs["text"] = tr(source_text)
        if source_values is not None:
            kwargs["values"] = _translated_values(source_values)
        result = original_insert(self, parent, index, iid=iid, **kwargs)
        self._i18n_items = getattr(self, "_i18n_items", {})
        self._i18n_items[result] = (source_text, source_values)
        return result
    ttk.Treeview.insert = insert

    for cls in (tk.Tk, tk.Toplevel):
        original_title = cls.title
        def title(self, string=None, _orig=original_title):
            if string is not None:
                self._i18n_title = string
                string = tr(string)
            return _orig(self, string) if string is not None else _orig(self)
        cls.title = title

    for name in ("showinfo", "showwarning", "showerror", "askyesno", "askyesnocancel", "askokcancel"):
        original = getattr(messagebox, name)
        def dialog(*args, _orig=original, **kwargs):
            args = tuple(tr(a) if isinstance(a, str) else a for a in args)
            if "title" in kwargs:
                kwargs["title"] = tr(kwargs["title"])
            if "message" in kwargs:
                kwargs["message"] = tr(kwargs["message"])
            return _orig(*args, **kwargs)
        setattr(messagebox, name, dialog)

    for name in ("askopenfilename", "askdirectory"):
        original = getattr(filedialog, name)
        def file_dialog(*args, _orig=original, **kwargs):
            if "title" in kwargs:
                kwargs["title"] = tr(kwargs["title"])
            if "filetypes" in kwargs:
                kwargs["filetypes"] = [(tr(label), pattern) for label, pattern in kwargs["filetypes"]]
            return _orig(*args, **kwargs)
        setattr(filedialog, name, file_dialog)


def refresh(root: tk.Misc) -> None:
    """Retranslate already-created controls after the language changes."""
    if hasattr(root, "_i18n_title"):
        # Call Tcl directly so the stored source title is not overwritten.
        root.tk.call("wm", "title", root._w, tr(root._i18n_title))
    for widget in root.winfo_children():
        if hasattr(widget, "_i18n_text"):
            # Direct Tcl configure avoids replacing the stored English source.
            widget.tk.call(widget._w, "configure", "-text", tr(widget._i18n_text))
        if isinstance(widget, ttk.Combobox) and hasattr(widget, "_i18n_values"):
            widget.configure(values=_translated_values(widget._i18n_values))
        if isinstance(widget, ttk.Notebook):
            for tab, source in getattr(widget, "_i18n_tabs", {}).items():
                widget.tab(tab, text=tr(source))
        if isinstance(widget, ttk.Treeview):
            for column, source in getattr(widget, "_i18n_headings", {}).items():
                widget.tk.call(widget._w, "heading", column, "-text", tr(source))
            for iid, (source_text, source_values) in list(getattr(widget, "_i18n_items", {}).items()):
                if widget.exists(iid):
                    opts = {}
                    if source_text is not None:
                        opts["text"] = tr(source_text)
                    if source_values is not None:
                        opts["values"] = _translated_values(source_values)
                    widget.item(iid, **opts)
        custom = getattr(widget, "refresh_i18n", None)
        if callable(custom):
            custom()
        refresh(widget)
