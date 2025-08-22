import asyncio

async def scrape_recent_tweets(page, username, max_tweets=20):
    await page.goto(f"https://x.com/{username}")
    await asyncio.sleep(2)
    tweets = []
    articles = await page.query_selector_all('article')
    for article in articles[:max_tweets]:
        try:
            content = await article.inner_text()
            tweets.append(content)
        except Exception:
            continue
    return tweets