import asyncio

async def auto_mute_followers(page, followers):
    for username in followers:
        await page.goto(f"https://x.com/{username}")
        await asyncio.sleep(2)
        more_btn = await page.query_selector('div[data-testid="userActions"]')
        if more_btn:
            await more_btn.click()
            await asyncio.sleep(1)
            mute_btn = await page.query_selector('//span[text()="Mute"]')
            if mute_btn:
                await mute_btn.click()
                await asyncio.sleep(1)
                confirm_btn = await page.query_selector('//span[text()="Mute"]')
                if confirm_btn:
                    await confirm_btn.click()
        await asyncio.sleep(2)