import asyncio

async def retweet_by_hashtag(page, hashtag, max_retweets=10):
    await page.goto(f"https://x.com/search?q=%23{hashtag}&src=typed_query")
    await asyncio.sleep(2)
    retweeted = 0
    while retweeted < max_retweets:
        retweet_buttons = await page.locator('[data-testid="retweet"]').all()
        for btn in retweet_buttons:
            try:
                await btn.click()
                await asyncio.sleep(1)
                confirm_btn = await page.get_by_test_id("retweetConfirm")
                if confirm_btn:
                    await confirm_btn.click()
                    retweeted += 1
                    await asyncio.sleep(1)
                if retweeted >= max_retweets:
                    break
            except Exception:
                continue
        await page.keyboard.press("PageDown")
        await asyncio.sleep(2)