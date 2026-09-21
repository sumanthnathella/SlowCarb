# Edit & publish

The guide is written in **Markdown** and built with **Material for MkDocs**. Search runs in your browser; there is no database, account system, or paid search service.

## Make a content change

| To change… | Edit… |
| --- | --- |
| Home page | `docs/index.md` |
| Diet framework and safety notes | `docs/principles.md` |
| Indian vegetable list | `docs/foods/vegetables.md` |
| Pulses and proteins | `docs/foods/pulses-protein.md` |
| Millets, staples, fats, and drinks | `docs/foods/staples-extras.md` |
| Dish substitutions | `docs/meals/dishes.md` |
| Recipes | `docs/meals/recipes.md` |
| First week and shopping list | `docs/meals/starter-week.md` |
| Grocery brands and product checks | `docs/groceries/index.md` |
| Evidence and references | `docs/sources.md` |
| Navigation and site configuration | `mkdocs.yml` |
| Colors and layout | `docs/stylesheets/extra.css` |

### A good food entry

Include these fields when adding an ingredient or product:

- **Names:** English, familiar regional names, and package search terms.
- **Category:** vegetable, pulse, protein, grain/tuber, or extra.
- **Status:** fits, modify, adaptation, or outside the strict plan.
- **Reason:** a short explanation, clearly labeled if interpretive.
- **Preparation:** what you can cook with it.
- **Tolerance:** gluten, dairy, and cross-contact considerations separately.
- **Verification:** source and date checked for branded products; local stock verified or unverified.

Do not copy store advertising as nutrition evidence or label a product gluten-free just because wheat is absent from a short online description.

## Run locally

Install [uv](https://docs.astral.sh/uv/) if it is not already available, then run from the project directory:

```sh
uv sync --frozen
uv run --frozen mkdocs serve --dev-addr 127.0.0.1:8000
```

Open the local address printed by MkDocs. Saving a Markdown file refreshes the development site. The Python environment stays in the ignored `.venv` directory.

## Verify before publishing

```sh
uv run --frozen mkdocs build --strict
uv run --frozen python -m unittest discover -s tests -p 'test_*.py' -v
```

The strict build checks documentation links and configuration. Tests check built pages, searchable aliases, source-content boundaries, and the publishing configuration. Optional browser checks are described in `AGENTS.md`.

## Publish on GitHub Pages

- **Website:** [SlowCarb guide](https://sumanthnathella.github.io/SlowCarb/)
- **Repository:** [sumanthnathella/SlowCarb](https://github.com/sumanthnathella/SlowCarb)

GitHub Pages is configured to use **GitHub Actions**. The **Publish guide** workflow builds and tests changes before deployment.

1. Click the pencil-shaped **Edit this page** icon near the page heading.
2. Sign in to GitHub and edit the Markdown. Repository owners can commit directly to `main`; other contributors can propose a pull request.
3. Save the change. Once it reaches `main`, the workflow automatically rebuilds and publishes the guide.
4. Check the repository's **Actions** tab if an update has not appeared. A failed build does not replace the last successfully deployed site.

You can also edit locally and push reviewed changes, or manually run **Publish guide** on `main`. The verified website address, repository address, and edit path are configured in `mkdocs.yml`.

### Before making the site public

- This site has no access-control layer. Treat deployed content as public unless you have explicitly configured and verified supported access restrictions.
- Keep personal health records, addresses, credentials, and the source EPUB out of the repository.
- A private repository alone does not imply a private Pages site.
- Nothing is purchased, ordered, or sent to a grocery service from this website.

## Keep the guide maintainable

Prefer a small number of well-organized pages over duplicate food lists with conflicting verdicts. Update the ingredient page and any affected recipes when changing a classification. Add aliases directly to the text so the built-in search can find them.

The [sources page](sources.md) should remain the place to record corrections and explain the difference between book rules and practical adaptations.
