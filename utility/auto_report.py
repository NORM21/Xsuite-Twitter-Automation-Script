import asyncio

async def auto_report_tweets_by_keyword(page, keyword, max_reports=3):
    await page.goto(f"https://x.com/search?q={keyword}&src=typed_query")
    await asyncio.sleep(2)
    reported = 0
    while reported < max_reports:
        more_buttons = await page.query_selector_all('div[data-testid="caret"]')
        for btn in more_buttons:
            try:
                await btn.click()
                await asyncio.sleep(1)
                report_btn = await page.query_selector('//span[text()="Report Post"]')
                if report_btn:
                    await report_btn.click()
                    await asyncio.sleep(1)
                    # Optionally, add more steps to select a reason
                    reported += 1
                    await asyncio.sleep(2)
                    if reported >= max_reports:
                        break
            except Exception:
                continue
        await page.keyboard.press("PageDown")
        await asyncio.sleep(2)