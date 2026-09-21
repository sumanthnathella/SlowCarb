from pathlib import Path
import re

from mkdocs.exceptions import PluginError


DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def section(source, heading):
    match = re.search(rf"^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", source, re.M | re.S)
    if not match:
        raise PluginError(f"Starter week is missing the '{heading}' section")
    return match[1].strip()


def calendar_links(text):
    return text.replace("](recipes.md", "](meals/recipes.md").replace(
        "](eating-out.md", "](meals/eating-out.md"
    )


def render_calendar(source):
    rows = []
    for line in section(source, "Seven-day menu").splitlines():
        if re.match(r"^\|\s*\d+\s*\|", line):
            rows.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    if len(rows) != 7 or any(len(row) != 4 or row[0] != str(i + 1) for i, row in enumerate(rows)):
        raise PluginError("The calendar needs seven ordered rows (1–7), each with breakfast, lunch, and dinner")
    cards = ['<div class="meal-week" markdown>']
    for day, row in zip(DAYS, rows):
        number, breakfast, lunch, dinner = row
        if breakfast == "Fixed breakfast":
            breakfast = "[Fixed breakfast](#everyday-breakfast)"
        meal = f"{lunch} {dinner}"
        image, description = "dal-vegetables", "Illustration of dal and a vegetable side"
        if "Egg bhurji" in meal:
            image, description = "egg-dosa-sides", "Illustration of egg bhurji, pulse dosas, carrot-radish salad and kimchi"
        elif "Shakshuka" in meal:
            image, description = "shakshuka", "Illustration of eggs in tomato sauce"
        elif "Zucchini" in meal:
            image, description = "zucchini-noodles", "Illustration of zucchini noodles with peppers and lentil sauce"
        elif "Chipotle" in meal:
            image, description = "chipotle-bowl", "Illustration of a bean bowl with fajita vegetables and salsa"
        elif "CAVA" in meal:
            image, description = "cava-bowl", "Illustration of a lentil bowl with greens, cucumber and hummus"
        cards.append(
            f'<section class="meal-day" aria-labelledby="{day.lower()}" markdown>\n\n'
            f'![{description}](assets/illustrations/{image}.svg){{ width="640" height="400" loading="lazy" }}\n\n'
            f'<p class="meal-day__label">Day {number}</p>\n\n'
            f'### {day}\n\n'
            f'**Breakfast**\n\n{calendar_links(breakfast)}\n\n'
            f'**Lunch**\n\n{calendar_links(lunch)}\n\n'
            f'**Dinner**\n\n{calendar_links(dinner)}\n\n'
            '</section>'
        )
    cards.append("</div>")
    return "\n\n".join(cards)


def on_page_markdown(markdown, *, page, config, files):
    if page.file.src_uri != "calendar.md":
        return markdown
    source = (Path(config["docs_dir"]) / "meals" / "starter-week.md").read_text(encoding="utf-8")
    fragments = {
        "{{ weekly_meal_calendar }}": render_calendar(source),
        "{{ fixed_breakfast }}": calendar_links(section(source, "Fixed breakfast, every day")),
    }
    for placeholder, fragment in fragments.items():
        if markdown.count(placeholder) != 1:
            raise PluginError(f"Calendar page must contain exactly one {placeholder}")
        markdown = markdown.replace(placeholder, fragment)
    if config.get("repo_url") and config.get("edit_uri"):
        page.edit_url = f'{config["repo_url"].rstrip("/")}/{config["edit_uri"].strip("/")}/meals/starter-week.md'
    return markdown
