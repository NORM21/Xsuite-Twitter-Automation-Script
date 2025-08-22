import asyncio
from datetime import datetime

async def schedule_dm(page, usernames, message, scheduled_time, interval_minutes=None):
    now = datetime.now()
    delay = (scheduled_time - now).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)
    while True:
        for username in usernames:
            await page.goto(f"https://x.com/messages/compose")
            await asyncio.sleep(2)
            search_box = await page.query_selector('input[data-testid="searchPeople"]')
            if search_box:
                await search_box.type(username)
                await asyncio.sleep(2)
                user_result = await page.query_selector('div[data-testid="typeaheadResult"]')
                if user_result:
                    await user_result.click()
                    await asyncio.sleep(1)
                    next_btn = await page.query_selector('div[data-testid="nextButton"]')
                    if next_btn:
                        await next_btn.click()
                        await asyncio.sleep(2)
                        msg_box = await page.query_selector('div[data-testid="dmComposerTextInput"]')
                        if msg_box:
                            await msg_box.type(message)
                            await asyncio.sleep(1)
                            send_btn = await page.query_selector('div[data-testid="dmComposerSendButton"]')
                            if send_btn:
                                await send_btn.click()
                                await asyncio.sleep(2)
        if interval_minutes is None:
            break
        await asyncio.sleep(interval_minutes * 60)