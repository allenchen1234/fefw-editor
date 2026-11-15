import unittest
from types import SimpleNamespace

import class_names_zh
import editor_advanced
import i18n


class ClassPickerTranslationTests(unittest.TestCase):
    def tearDown(self):
        i18n.set_language("en")

    def test_every_catalogue_entry_has_a_chinese_label(self):
        missing = [meta["jp"] for meta in editor_advanced.jobs().values()
                   if not class_names_zh.chinese_name(meta)]
        self.assertEqual(missing, [])

    def test_picker_rows_keep_keys_and_search_aliases(self):
        i18n.set_language("zh_CN")
        rows = editor_advanced.AdvancedMixin._class_rows(None)
        row = next(r for r in rows if r[2] == "JID_剣士")
        self.assertEqual(row[1], "剑士")
        self.assertIn("Myrmidon", row[3])
        i18n.set_language("en")
        english = next(r for r in editor_advanced.AdvancedMixin._class_rows(None) if r[0] == row[0])
        self.assertEqual(english[1], "Myrmidon")
        self.assertIn("剑士", english[3])

    def test_add_and_swap_titles(self):
        i18n.set_language("zh_CN")
        cid = next(cid for cid, meta in editor_advanced.jobs().items() if meta["jp"] == "JID_剣士")
        unit = SimpleNamespace(classes=[(cid, 0, 0)])
        titles = []
        page = SimpleNamespace(_cls_unit=lambda: unit, _class_rows=lambda: [],
                               cls_tree=SimpleNamespace(selection=lambda: ("0",)),
                               _picker=lambda title, rows: titles.append(title))
        editor_advanced.AdvancedMixin.add_class(page)
        editor_advanced.AdvancedMixin.swap_class(page)
        self.assertEqual(i18n.tr(titles[0]), "添加兵种")
        self.assertEqual(titles[1], "将剑士替换为…")


if __name__ == "__main__":
    unittest.main()
