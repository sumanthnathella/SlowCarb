import json
from pathlib import Path
import re
import unittest

from mkdocs.config import load_config


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITE = ROOT / "site"


class SiteTests(unittest.TestCase):
    def test_every_markdown_page_is_in_navigation(self):
        config = load_config(str(ROOT / "mkdocs.yml"))

        def paths(items):
            for item in items:
                for value in item.values():
                    if isinstance(value, list):
                        yield from paths(value)
                    else:
                        yield value

        expected = {str(path.relative_to(DOCS)) for path in DOCS.rglob("*.md")}
        self.assertEqual(expected, set(paths(config.nav)))

    def test_all_pages_built_with_search(self):
        for source in DOCS.rglob("*.md"):
            relative = source.relative_to(DOCS)
            target = (
                SITE / relative.with_suffix(".html")
                if source.name == "index.md"
                else SITE / relative.with_suffix("") / "index.html"
            )
            with self.subTest(page=str(relative)):
                self.assertTrue(target.is_file(), "Run mkdocs build --strict first")
                html = target.read_text()
                self.assertIn('data-md-component="search"', html)
                self.assertIn("SlowCarb", html)

    def test_published_base_path_and_edit_links(self):
        config = load_config(str(ROOT / "mkdocs.yml"))
        self.assertEqual(config.site_url, "https://sumanthnathella.github.io/SlowCarb/")
        for relative in ("index.md", "foods/vegetables.md", "groceries/index.md"):
            source = Path(relative)
            target = (
                SITE / source.with_suffix(".html")
                if source.name == "index.md"
                else SITE / source.with_suffix("") / "index.html"
            )
            with self.subTest(page=relative):
                html = target.read_text()
                self.assertIn(config.repo_url + "/edit/main/docs/" + relative, html)
                self.assertIn('rel="canonical"', html)
                self.assertIn(config.site_url, html)

    def test_regional_aliases_and_product_names_are_searchable(self):
        index = json.loads((SITE / "search" / "search_index.json").read_text())
        text = " ".join(
            f"{entry['title']} {entry['text']}" for entry in index["docs"]
        ).casefold()
        for term in (
            "arvi", "seppankizhangu", "chamadumpa", "thotakura", "tandaljo",
            "suran", "millet", "pesarattu", "aviyal", "sambhar mix", "frozen",
            "guvar", "ridge gourd", "papdi lilva", "wheat flour",
            "hemp hearts", "bagel seasoning", "spinach omelette", "shakshuka",
            "zucchini", "peanut sundal", "skhug", "harissa", "edamame",
            "kambu", "anjeer", "tuvar lilva", "surti papdi", "valor",
            "mochai", "avarekai", "green gram dosa", "pachai payaru",
            "karuppu ulunthu", "sattu", "dal idli",
        ):
            with self.subTest(term=term):
                self.assertIn(term, text)

    def test_slash_separated_aliases_are_individual_search_tokens(self):
        index = json.loads((SITE / "search" / "search_index.json").read_text())
        separator = index["config"]["separator"]
        tokens = re.split(separator, "taro/arvi/arbi/seppankizhangu/chamadumpa")
        self.assertEqual(tokens, ["taro", "arvi", "arbi", "seppankizhangu", "chamadumpa"])

    def test_no_private_paths_or_book_files_in_public_content(self):
        for source in DOCS.rglob("*"):
            if not source.is_file():
                continue
            with self.subTest(file=str(source)):
                self.assertNotEqual(source.suffix.casefold(), ".epub")
                if source.suffix in {".md", ".css", ".js", ".html"}:
                    text = source.read_text()
                    self.assertNotRegex(text, r"file://|/Users/|/home/[^/]+/")
                    self.assertNotRegex(text, r"gh[pousr]_[A-Za-z0-9]{20,}")

    def test_internal_markdown_links_exist(self):
        for source in DOCS.rglob("*.md"):
            for link in re.findall(r"\]\(([^)]+)\)", source.read_text()):
                target = link.split("#", 1)[0]
                if not target or ":" in target:
                    continue
                with self.subTest(page=source.name, link=link):
                    self.assertTrue((source.parent / target).is_file())

    def test_grocery_caveats_are_preserved(self):
        text = (DOCS / "groceries" / "index.md").read_text().casefold()
        for phrase in (
            "http 403", "no local stock", "wheat flour", "yams",
            "not a protein-complete sambar", "20 september 2026",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_starter_week_has_fixed_breakfast_and_limited_tofu(self):
        plan = (DOCS / "meals" / "starter-week.md").read_text()
        rows = [line for line in plan.splitlines() if re.match(r"\| [1-7] \|", line)]
        self.assertEqual(len(rows), 7)
        tofu_lunches = sundal_dinners = 0
        for row in rows:
            with self.subTest(row=row):
                self.assertIn("Fixed breakfast", row.split("|")[2])
                self.assertNotIn("tofu", row.split("|")[4].casefold())
                tofu_lunches += "tofu" in row.split("|")[3].casefold()
                sundal_dinners += "peanut sundal" in row.split("|")[4].casefold()
        self.assertEqual(tofu_lunches, 1)
        self.assertEqual(sundal_dinners, 2)
        self.assertIn("Office Asian bowl", plan)
        self.assertIn("Chipotle", plan)
        self.assertIn("CAVA", plan)
        self.assertIn("Zucchini noodles with peppers", plan)
        self.assertIn("10 whole eggs + 8 additional whites", plan)
        self.assertNotIn("1.5 kg", plan)

    def test_fixed_breakfast_has_portions_and_protein_caveat(self):
        recipes = (DOCS / "meals" / "recipes.md").read_text()
        section = recipes.split("## Fixed breakfast: avocado and spinach omelette", 1)[1].split("\n## ", 1)[0]
        for ingredient in (
            "½ medium avocado", "2 whole eggs + 2 additional egg whites",
            "1 tablespoon hemp hearts", "1 teaspoon ground flaxseed",
            "1 teaspoon pine nuts", "everything-bagel seasoning", "spinach",
        ):
            with self.subTest(ingredient=ingredient):
                self.assertIn(ingredient, section)
        self.assertIn("26–28 g", section)
        self.assertIn("not a universal requirement", section)
        self.assertIn("gluten", section.casefold())

    def test_day_two_dinner_includes_both_vegetable_sides(self):
        plan = (DOCS / "meals" / "starter-week.md").read_text()
        dinner = next(line for line in plan.splitlines() if line.startswith("| 2 |")).split("|")[4]
        for food in ("Egg bhurji", "rice-free pesarattu", "carrot–radish salad", "vegetarian, gluten-free kimchi"):
            with self.subTest(food=food):
                self.assertIn(food, dinner)
        shopping = plan.split("## One-person shopping: first three days", 1)[1].split("### Breakfast-only", 1)[0]
        for item in ("carrot", "radish", "lemon or lime", "kimchi"):
            self.assertIn(item, shopping)
        recipes = (DOCS / "meals" / "recipes.md").read_text()
        self.assertIn("## Lemon-marinated carrot–radish salad and kimchi", recipes)
        self.assertIn("not a shelf-stable pickle", recipes)

    def test_calendar_is_generated_from_the_plan(self):
        from hooks import DAYS, render_calendar

        plan = (DOCS / "meals" / "starter-week.md").read_text()
        cards = render_calendar(plan)
        self.assertEqual(cards.count('class="meal-day"'), 7)
        for day in DAYS:
            self.assertIn(f"### {day}", cards)
        self.assertIn("carrot–radish salad", cards)
        self.assertIn("vegetarian, gluten-free kimchi", cards)
        changed = render_calendar(plan.replace("Egg bhurji", "Changed dinner"))
        self.assertIn("Changed dinner", changed)
        self.assertNotIn("Egg bhurji", changed)
        html = (SITE / "calendar" / "index.html").read_text()
        self.assertIn("hemp hearts", html)
        self.assertIn("2 additional egg whites", html)
        self.assertIn("/edit/main/docs/meals/starter-week.md", html)
        self.assertNotIn("{{ weekly_meal_calendar }}", html)
        self.assertNotIn("{{ fixed_breakfast }}", html)
        self.assertEqual(html.count('class="meal-day"'), 7)

    def test_calendar_rejects_incomplete_schedule(self):
        from hooks import render_calendar
        from mkdocs.exceptions import PluginError

        with self.assertRaises(PluginError):
            render_calendar("## Seven-day menu\n\n| 1 | Breakfast | Lunch | Dinner |\n")

    def test_original_illustrations_are_local_and_accessible(self):
        import xml.etree.ElementTree as ET

        for name in ("breakfast", "dal-vegetables", "egg-dosa-sides", "shakshuka", "chipotle-bowl", "cava-bowl", "asian-bowl", "zucchini-noodles"):
            with self.subTest(image=name):
                path = DOCS / "assets" / "illustrations" / f"{name}.svg"
                root = ET.fromstring(path.read_text())
                self.assertEqual(root.attrib["viewBox"], "0 0 640 400")
                self.assertIsNotNone(root.find("{http://www.w3.org/2000/svg}title"))
                self.assertIsNotNone(root.find("{http://www.w3.org/2000/svg}desc"))
                self.assertTrue((SITE / "assets" / "illustrations" / path.name).exists())
                for element in root.iter():
                    self.assertNotEqual(element.tag.rsplit("}", 1)[-1], "script")
                    for key, value in element.attrib.items():
                        if key.rsplit("}", 1)[-1] == "href":
                            self.assertTrue(value.startswith("#"), "Illustrations must not load external assets")

    def test_restaurant_orders_explain_portions_and_cross_contact(self):
        page = (DOCS / "meals" / "eating-out.md").read_text()
        for phrase in (
            "Chipotle", "CAVA", "cross-contact", "two full servings", "18 g",
            "8 g", "No sofritas", "not a claim that plain falafel contains wheat",
            "skhug", "harissa", "red pepper hummus", "Office Asian bowl",
            "soy sauce contains wheat", "pickled radish",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, page)
        calendar = (SITE / "calendar" / "index.html").read_text()
        self.assertIn("eating-out", calendar)
        for image in ("breakfast", "egg-dosa-sides", "chipotle-bowl", "cava-bowl", "zucchini-noodles", "shakshuka"):
            self.assertIn(f"illustrations/{image}.svg", calendar)

    def test_workflow_builds_and_checks_before_deployment(self):
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text()
        self.assertIn("mkdocs build --strict", workflow)
        self.assertIn("unittest discover", workflow)
        self.assertIn("needs: build", workflow)
        self.assertIn("github.event_name != 'pull_request'", workflow)
        self.assertNotIn("pull_request_target", workflow)


if __name__ == "__main__":
    unittest.main()
