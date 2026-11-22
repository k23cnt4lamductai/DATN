from django.test import SimpleTestCase

from .listing import DEFAULT_SORT, clean_int, make_url, page_items, parse_filters


class ListingHelpersTest(SimpleTestCase):
    def test_clean_int(self):
        self.assertEqual(clean_int("50000"), 50000)
        self.assertEqual(clean_int(" 0 "), 0)
        for bad in ("", None, "abc", "-5", "1.5"):
            self.assertIsNone(clean_int(bad))

    def test_parse_filters_defaults_and_swap(self):
        f = parse_filters({})
        self.assertEqual((f["sort"], f["min_price"], f["max_price"], f["category"], f["q"]), (DEFAULT_SORT, None, None, "", ""))
        self.assertEqual(parse_filters({"sort": "hack"})["sort"], DEFAULT_SORT)
        f = parse_filters({"min_price": "100000", "max_price": "20000", "sort": "price_asc"})
        self.assertEqual((f["min_price"], f["max_price"], f["sort"]), (20000, 100000, "price_asc"))
        self.assertEqual(parse_filters({"q": "  kem  "})["q"], "kem")

    def test_make_url(self):
        items = [("category", "banh-kem"), ("q", "dâu"), ("page", "3")]
        self.assertEqual(make_url("/", items, page=2), "/?category=banh-kem&q=d%C3%A2u&page=2")
        self.assertEqual(make_url("/", items, category=None, page=None), "/?q=d%C3%A2u")
        self.assertEqual(make_url("/", []), "/")

    def test_page_items(self):
        self.assertEqual(page_items(1, 1), [1])
        self.assertEqual(page_items(1, 5), [1, 2, 3, 4, 5])
        self.assertEqual(page_items(10, 20), [1, None, 8, 9, 10, 11, 12, None, 20])
        self.assertEqual(page_items(1, 20), [1, 2, 3, None, 20])
        self.assertEqual(page_items(20, 20), [1, None, 18, 19, 20])
        self.assertEqual(page_items(5, 9), [1, 2, 3, 4, 5, 6, 7, 8, 9])
