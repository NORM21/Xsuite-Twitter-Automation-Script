import asyncio

async def delete_bookmarks(page, max_delete=1000):
    await page.goto("https://x.com/i/bookmarks")
    await asyncio.sleep(3)
    deleted = 0
    for _ in range(30):
        bookmark_buttons = await page.locator('[data-testid="bookmark"]').all()
        for btn in bookmark_buttons:
            try:
                await btn.click()
                deleted += 1
                await asyncio.sleep(1)
                if deleted >= max_delete:
                    break
            except Exception:
                continue
        if deleted >= max_delete:
            break
        await page.mouse.wheel(0, 10000)
        await asyncio.sleep(2)