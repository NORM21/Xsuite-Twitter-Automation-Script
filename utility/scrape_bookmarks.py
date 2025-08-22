import asyncio
import csv

async def scrape_bookmarks(page, csv_path="bookmarks.csv", max_bookmarks=1000):
    bookmarks = []
    await page.goto("https://x.com/i/bookmarks")
    await asyncio.sleep(3)

    last_count = 0
    for _ in range(30):
        articles = await page.locator('article').all()
        for article in articles:
            try:
                tweet_url = await article.locator('a[href*="/status/"]').get_attribute("href")
                tweet_text = await article.inner_text()
                if tweet_url and tweet_url not in [b["url"] for b in bookmarks]:
                    bookmarks.append({"url": tweet_url, "text": tweet_text})
                    if len(bookmarks) >= max_bookmarks:
                        break
            except Exception:
                continue
        await page.mouse.wheel(0, 10000)
        await asyncio.sleep(2)
        if len(bookmarks) == last_count or len(bookmarks) >= max_bookmarks:
            break
        last_count = len(bookmarks)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "text"])
        for b in bookmarks:
            writer.writerow([b["url"], b["text"]])