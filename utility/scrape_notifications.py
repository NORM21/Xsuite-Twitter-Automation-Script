import asyncio

async def scrape_notifications(page, max_items=20):
    await page.goto("https://x.com/notifications")
    await asyncio.sleep(2)
    notifications = []
    items = await page.query_selector_all('div[role="listitem"]')
    for item in items[:max_items]:
        try:
            text = await item.inner_text()
            notifications.append(text)
        except Exception:
            continue
    return notifications