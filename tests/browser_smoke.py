from pathlib import Path
import os
import re
import tempfile
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright


BASE = os.environ.get("SLOWCARB_TEST_URL", "http://127.0.0.1:8000/SlowCarb/").rstrip("/")
ARTIFACTS = Path(tempfile.mkdtemp(prefix="slowcarb-browser-"))


def check_layout(page):
    assert page.evaluate(
        "document.documentElement.scrollWidth <= window.innerWidth + 1"
    ), "Page has horizontal overflow"


with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    errors = []
    failed_responses = []
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on(
        "response",
        lambda response: failed_responses.append(response.url)
        if response.status >= 400 and urlsplit(response.url).netloc == urlsplit(BASE).netloc
        else None,
    )
    page.goto(BASE, wait_until="load")
    expect(page.get_by_role("heading", name=re.compile(r"Familiar food\.\s*A simpler plan\.")).first).to_be_visible()
    check_layout(page)
    page.screenshot(path=str(ARTIFACTS / "desktop.png"), full_page=True)
    page.locator(".md-tabs").get_by_role("link", name="Calendar", exact=True).click()
    expect(page.locator(".meal-day")).to_have_count(7)
    tuesday = page.locator('.meal-day[aria-labelledby="tuesday"]')
    expect(tuesday).to_contain_text("carrot–radish salad")
    expect(tuesday).to_contain_text("vegetarian, gluten-free kimchi")
    expect(page.locator(".md-content__button").first).to_have_attribute(
        "href", "https://github.com/sumanthnathella/SlowCarb/edit/main/docs/meals/starter-week.md"
    )
    check_layout(page)
    expect(page.locator(".meal-day img")).to_have_count(7)
    page.screenshot(path=str(ARTIFACTS / "calendar-desktop.png"), full_page=True)
    page.get_by_role("link", name="Restaurant & office bowls", exact=True).click()
    expect(page.locator(".restaurant-card")).to_have_count(3)
    expect(page.locator(".restaurant-card").first).to_contain_text("No sofritas")
    expect(page.locator(".restaurant-card").nth(1)).to_contain_text("black lentils")
    expect(page.locator(".restaurant-card").last).to_contain_text("soy sauce contains wheat")
    page.wait_for_function("Array.from(document.querySelectorAll('.restaurant-card img')).every(img => img.complete && img.naturalWidth > 0)")
    check_layout(page)
    page.screenshot(path=str(ARTIFACTS / "restaurants-desktop.png"), full_page=True)
    page.goto(BASE, wait_until="load")
    page.get_by_role("link", name="Find a food", exact=True).click()
    expect(page.get_by_role("heading", name=re.compile(r"^Vegetables & greens"))).to_be_visible()
    search = page.get_by_role("textbox", name="Search", exact=True)
    search.fill("seppankizhangu")
    results = page.locator(".md-search-result")
    expect(results).to_contain_text("Vegetables", timeout=15000)
    expect(results).to_contain_text("seppankizhangu")
    search.press("Escape")
    page.goto(BASE + "/groceries/", wait_until="load")
    expect(page.get_by_role("heading", name=re.compile("Deep Surti Undhiu Mix"))).to_be_visible()
    page.get_by_title("Switch to dark mode", exact=True).click()
    expect(page.locator("body")).to_have_attribute("data-md-color-scheme", "slate")
    page.screenshot(path=str(ARTIFACTS / "groceries-dark.png"), full_page=True)
    mobile = browser.new_page(
        viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True
    )
    mobile.on("pageerror", lambda error: errors.append(str(error)))
    mobile.goto(BASE, wait_until="load")
    check_layout(mobile)
    mobile.screenshot(path=str(ARTIFACTS / "mobile.png"), full_page=True)
    mobile.locator('label[for="__search"]').first.click()
    mobile_search = mobile.get_by_role("textbox", name="Search", exact=True)
    mobile_search.fill("Sambhar")
    expect(mobile.locator(".md-search-result")).to_contain_text("Sambhar", timeout=15000)
    mobile_search.press("Escape")
    mobile.goto(BASE + "/calendar/", wait_until="load")
    expect(mobile.locator(".meal-day")).to_have_count(7)
    expect(mobile.locator('.meal-day[aria-labelledby="tuesday"]')).to_contain_text("kimchi")
    mobile.locator(".meal-day").first.get_by_role("link", name="Fixed breakfast", exact=True).click()
    expect(mobile.get_by_role("heading", name=re.compile("^Everyday breakfast"))).to_be_visible()
    check_layout(mobile)
    mobile.screenshot(path=str(ARTIFACTS / "calendar-mobile.png"), full_page=True)
    mobile.goto(BASE + "/foods/vegetables/", wait_until="load")
    check_layout(mobile)
    mobile.goto(BASE + "/meals/eating-out/", wait_until="load")
    expect(mobile.locator(".restaurant-card")).to_have_count(3)
    check_layout(mobile)
    mobile.screenshot(path=str(ARTIFACTS / "restaurants-mobile.png"), full_page=True)
    for path in ("foods/pulses-protein/", "foods/staples-extras/", "meals/starter-week/", "groceries/"):
        mobile.goto(BASE + "/" + path, wait_until="load")
        check_layout(mobile)
    browser.close()
    assert not errors, f"Browser errors: {errors}"
    assert not failed_responses, f"Failed local responses: {failed_responses}"
    print("Browser checks passed: desktop, mobile, aliases, product search, theme, links, overflow.")
    print(f"Screenshots: {ARTIFACTS}")
