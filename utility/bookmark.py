import asyncio

async def bookmark_tweets_by_hashtag(page, hashtag, max_bookmarks=10):
    await page.goto(f"https://x.com/search?q=%23{hashtag}&src=typed_query")
    await asyncio.sleep(2)
    bookmarked = 0
    while bookmarked < max_bookmarks:
        bookmark_buttons = await page.locator('[data-testid="bookmark"]').all()
        for btn in bookmark_buttons:
            try:
                await btn.click()
                bookmarked += 1
                await asyncio.sleep(1)
                if bookmarked >= max_bookmarks:
                    break
            except Exception:
                continue
        await page.keyboard.press("PageDown")
        await asyncio.sleep(2)