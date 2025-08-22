import asyncio
from datetime import datetime

async def schedule_task(task_coro, scheduled_time: datetime):
    """Schedules any coroutine to run at a specific datetime."""
    now = datetime.now()
    delay = (scheduled_time - now).total_seconds()
    if delay > 0:
        print(f"Waiting {delay:.0f} seconds to run scheduled task...")
        await asyncio.sleep(delay)
    await task_coro()

async def schedule_tweet(page, tweet_text, scheduled_time, interval_minutes=None):
    now = datetime.now()
    delay = (scheduled_time - now).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)
    while True:
        await page.goto("https://x.com/compose/tweet")
        await asyncio.sleep(2)
        tweet_box = await page.query_selector('div[data-testid="tweetTextarea_0"][role="textbox"]')
        if tweet_box:
            await tweet_box.click()
            await tweet_box.type(tweet_text)
            await asyncio.sleep(1)
            tweet_btn = await page.query_selector('button[data-testid="tweetButton"]:not([aria-disabled="true"])')
            if tweet_btn:
                await tweet_btn.click()
                await asyncio.sleep(2)
        if interval_minutes is None:
            break
        await asyncio.sleep(interval_minutes * 60)