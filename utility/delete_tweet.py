import asyncio

async def auto_delete_recent_tweets(page, username, max_tweets=5):
    await page.goto(f"https://x.com/{username}")
    await asyncio.sleep(2)
    tweets = await page.query_selector_all('article')
    deleted = 0
    for tweet in tweets:
        try:
            more_btn = await tweet.query_selector('div[data-testid="caret"]')
            if more_btn:
                await more_btn.click()
                await asyncio.sleep(1)
                delete_btn = await page.query_selector('//span[text()="Delete"]')
                if delete_btn:
                    await delete_btn.click()
                    await asyncio.sleep(1)
                    confirm_btn = await page.query_selector('//span[text()="Delete"]')
                    if confirm_btn:
                        await confirm_btn.click()
                        deleted += 1
                        await asyncio.sleep(2)
                        if deleted >= max_tweets:
                            break
        except Exception:
            continue