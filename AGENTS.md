# SlowCarb project

A static, searchable South Indian vegetarian slow-carb reference built with Material for MkDocs. Content lives in `docs/`; do not build a separate application or duplicate the food data without a clear need.

## Environment and commands

- Use `uv` and the committed `uv.lock`. Local verification uses Python 3.12; GitHub Actions also installs Python 3.12.
- Install: `uv sync --frozen`.
- Preview: `uv run --frozen mkdocs serve --dev-addr 127.0.0.1:8000`.
- Required build: `uv run --frozen mkdocs build --strict`.
- Required tests after building: `uv run --frozen python -m unittest discover -s tests -p 'test_*.py' -v`.
- Optional browser setup: `uv run --frozen playwright install chromium`.
- Browser checks with the preview running: `uv run --frozen python tests/browser_smoke.py`.
- `SLOWCARB_TEST_URL` can override the default browser-check URL. Screenshots go to a temporary directory printed by the script, never into published content.
- Do not edit generated `site/` output or `.venv/`; both are ignored.
- Browser tests wait for page load, not network idle: MkDocs live reload keeps a long-poll connection open.
- Preserve the custom search separator in `mkdocs.yml`: slash-separated aliases must index as individual terms, not one combined token.

## Content conventions

- Default meals are vegetarian including eggs, gluten-free, and dairy-free. The fixed breakfast is half an avocado with measured hemp hearts, pine nuts, ground flaxseed and bagel seasoning, plus a spinach omelette of two whole eggs and two extra whites. A third white is optional, not compulsory. Check gluten ingredients and cross-contact separately from slow-carb compatibility.
- Keep the starter plan tofu-free and based on familiar eggs, pulses, and Indian vegetables. Retain tofu only as an optional food-reference choice if tolerated; do not replace every tofu serving with mandatory eggs or oversized pulse portions. Keep individual symptoms and private health details out of published content.
- Distinguish author rules, our interpretations/adaptations, and independent nutrition evidence. Tofu is a practical adaptation, not explicit approval inferred from a nutrient table.
- Do not promise rapid fat loss, recommend binge eating, prescribe supplement stacks, or imply whole fruit or grains are inherently unhealthy.
- Use regional ingredient and package names in searchable text, with a caveat that regional names vary.
- Keep whole pulse, protein, and vegetable portions distinct. A thin serving of sambar or rasam is not automatically protein-rich.
- Manufacturer product listings do not prove local store availability or gluten-free certification. Record source URLs and check dates; verify current package labels.
- Add sources to `docs/sources.md` and keep relevant food, grocery, and recipe pages consistent.
- Keep the source EPUB, private health information, addresses, credentials, and local filesystem paths out of `docs/` and generated output.

## Publishing

`.github/workflows/pages.yml` builds/tests pull requests and deploys only `main` pushes or manual runs on `main`. Repository: https://github.com/sumanthnathella/SlowCarb. GitHub Pages is configured with the GitHub Actions source at https://sumanthnathella.github.io/SlowCarb/. Verified addresses and `edit_uri: edit/main/docs/` are in `mkdocs.yml`. The initial publication was user-approved; later pushes still require user authorization. MkDocs previews use the `/SlowCarb/` base path from `site_url`.
