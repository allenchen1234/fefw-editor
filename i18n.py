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
    "Pairs whose C/B/A conversations the game data defines.": "游戏数据中定义了 C／B／A 对话的组合。",
    "Only characters in this save": "仅显示此存档中的角色", "Character": "角色", "Pairs": "组合",
    "No character selected": "未选择角色", "Open a save to see what it records.": "打开存档以查看其中的记录。",
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
