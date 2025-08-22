import asyncio
import csv

async def scrape_trending_topics(page, csv_path="trending_topics.csv"):
    await page.goto("https://x.com/explore/tabs/trending")
    await page.wait_for_selector('[data-testid="trend"]')
    await asyncio.sleep(2)
    trends = []
    trend_elements = await page.locator('[data-testid="trend"]').all()
    for el in trend_elements:
        try:
            text = await el.inner_text()
            trends.append(text)
        except Exception:
            continue
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["trend"])
        for t in trends:
            writer.writerow([t])
    return trends