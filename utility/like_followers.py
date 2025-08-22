import asyncio

async def auto_like_followers_tweets(page, followers, max_likes_per_user=3):
    for username in followers:
        await page.goto(f"https://x.com/{username}")
        await asyncio.sleep(2)
        liked = 0
        tweets = await page.query_selector_all('div[data-testid="like"]')
        for btn in tweets:
            try:
                await btn.click()
                liked += 1
                await asyncio.sleep(1)
                if liked >= max_likes_per_user:
                    break
            except Exception:
                continue