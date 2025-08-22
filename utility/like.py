# utility/like.py
import asyncio

async def like_tweets_by_hashtag(page, hashtag, max_likes=10):
    await page.goto(f"https://x.com/search?q=%23{hashtag}&src=typed_query")
    await asyncio.sleep(2)
    liked = 0
    while liked < max_likes:
        like_buttons = await page.locator('[data-testid="like"]').all()
        for btn in like_buttons:
            try:
                await btn.click()
                liked += 1
                await asyncio.sleep(1)
                if liked >= max_likes:
                    break
            except Exception:
                continue
        await page.keyboard.press("PageDown")
        await asyncio.sleep(2)