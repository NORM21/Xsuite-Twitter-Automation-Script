import asyncio

async def scrape_poll_results(page, tweet_url):
    await page.goto(tweet_url)
    await asyncio.sleep(2)
    poll_options = await page.query_selector_all('div[data-testid="pollOption"]')
    results = []
    for option in poll_options:
        try:
            text = await option.inner_text()
            results.append(text)
        except Exception:
            continue
    return results