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

    def test_workflow_builds_and_checks_before_deployment(self):
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text()
        self.assertIn("mkdocs build --strict", workflow)
        self.assertIn("unittest discover", workflow)
        self.assertIn("needs: build", workflow)
        self.assertIn("github.event_name != 'pull_request'", workflow)
        self.assertNotIn("pull_request_target", workflow)


if __name__ == "__main__":
    unittest.main()
