import asyncio

async def auto_follow_back(page, username, max_follows=10):
    await page.goto(f"https://x.com/{username}/followers")
    await asyncio.sleep(2)
    followed = 0
    follow_buttons = await page.query_selector_all('div[data-testid$="-follow"]')
    for btn in follow_buttons:
        try:
            await btn.click()
            followed += 1
            await asyncio.sleep(1)
            if followed >= max_follows:
                break
        except Exception:
            continue