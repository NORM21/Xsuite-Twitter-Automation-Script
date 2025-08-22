import asyncio

async def auto_reply_mentions(page, reply_text, max_replies=5):
    await page.goto("https://x.com/notifications/mentions")
    await asyncio.sleep(2)
    replied = 0
    tweets = await page.query_selector_all('article')
    for tweet in tweets:
        try:
            reply_btn = await tweet.query_selector('div[data-testid="reply"]')
            if reply_btn:
                await reply_btn.click()
                await asyncio.sleep(1)
                reply_box = await page.query_selector('div[data-testid="tweetTextarea_0"][role="textbox"]')
                if reply_box:
                    await reply_box.type(reply_text)
                    await asyncio.sleep(1)
                    send_btn = await page.query_selector('div[data-testid="tweetButton"]:not([aria-disabled="true"])')
                    if send_btn:
                        await send_btn.click()
                        replied += 1
                        await asyncio.sleep(2)
                        if replied >= max_replies:
                            break
        except Exception:
            continue