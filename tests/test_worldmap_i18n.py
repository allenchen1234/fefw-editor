import unittest
from types import SimpleNamespace

import i18n
import map_names_zh
import map_page
import worldmap


class FakeTree:
    def __init__(self):
        self.rows = {}

    def selection(self): return ()
    def get_children(self): return tuple(self.rows)
    def delete(self, *items): self.rows.clear()
    def tag_configure(self, *args, **kwargs): pass
    def insert(self, parent, where, iid, **kwargs): self.rows[iid] = kwargs
    def exists(self, iid): return iid in self.rows
    def selection_set(self, items): pass


class WorldMapTranslationTests(unittest.TestCase):
    def tearDown(self):
        i18n.set_language("en")

    def test_catalogue_places_and_network_names(self):
        cat = worldmap.catalog()
        self.assertIsNotNone(cat)
        self.assertFalse([s.jp for s in cat.spots if s.is_place and s.jp not in map_names_zh.NAMES])
        self.assertEqual(map_names_zh.name("帝都ダグシオン"), "帝都鞑古席翁")
        self.assertEqual(map_names_zh.name("砂漠用分岐5"), "沙漠岔路点 5")
        self.assertEqual(map_names_zh.name("帝都ダグシオン_分岐点006_1"),
                         "道路：帝都鞑古席翁 → 岔路点 6（1）")

    def test_page_filters_in_three_languages(self):
        cat = worldmap.catalog()
        place = cat.spots[0]
        records = {place.key: SimpleNamespace(state=worldmap.SHOWN, visited=1)}
        page = SimpleNamespace(map_tree=FakeTree(), map_view="places", p={"muted": "gray"},
                               map_count=SimpleNamespace(configure=lambda **kwargs: None),
                               _map_records=lambda: (records, None))
        for lang in ("zh_CN", "en"):
            i18n.set_language(lang)
            for query in ("鞑古席翁", "ダグシオン", "dagsion"):
                page.map_search = SimpleNamespace(get=lambda: query)
                map_page.MapPageMixin.refresh_world_map(page)
                row = page.map_tree.rows[f"s{place.index}"]
                self.assertEqual(row["text"], "帝都鞑古席翁" if lang == "zh_CN" else place.name)

    def test_map_help_is_translated(self):
        i18n.set_language("zh_CN")
        self.assertNotEqual(i18n.tr(map_page.NOTE), map_page.NOTE)
        self.assertEqual(i18n.tr("World map"), "世界地图")


if __name__ == "__main__":
    unittest.main()
