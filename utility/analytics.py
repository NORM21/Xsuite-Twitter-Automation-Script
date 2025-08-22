import csv
import asyncio

async def export_analytics(page, username, csv_path="analytics.csv", max_tweets=20):
    await page.goto(f"https://x.com/{username}")
    await asyncio.sleep(2)
    tweets = await page.query_selector_all('article')
    data = []
    for tweet in tweets[:max_tweets]:
        try:
            content = await tweet.inner_text()
            likes = await tweet.query_selector('div[data-testid="like"] span')
            likes_count = await likes.inner_text() if likes else "0"
            retweets = await tweet.query_selector('div[data-testid="retweet"] span')
            retweets_count = await retweets.inner_text() if retweets else "0"
            data.append([content, likes_count, retweets_count])
        except Exception:
            continue
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["tweet", "likes", "retweets"])
        for row in data:
            writer.writerow(row)