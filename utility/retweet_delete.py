import asyncio

async def delete_retweets(page, username):
    await page.goto(f"https://x.com/{username}")
    await asyncio.sleep(2)
    last_height = await page.evaluate("document.body.scrollHeight")
    while True:
        # Find all "Undo repost" buttons (retweets)
        repost_buttons = await page.query_selector_all('button[data-testid="unretweet"][aria-label*="Reposted"]')
        if not repost_buttons:
            # Scroll down to load more tweets
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            await asyncio.sleep(2)
            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                # No more tweets loaded, we're done
                break
            last_height = new_height
            continue
        for btn in repost_buttons:
            try:
                await btn.click()
                await asyncio.sleep(1)
                # Confirm "Undo repost" in the popup
                undo_btn = await page.query_selector('//span[text()="Undo repost"]')
                if undo_btn:
                    await undo_btn.click()
                    await asyncio.sleep(2)
            except Exception as e:
                print(f"Error while removing retweet: {e}")
        await asyncio.sleep(2)
