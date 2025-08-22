import asyncio
from datetime import datetime

async def schedule_recurring(task_func, first_run_time, interval_minutes):
    now = datetime.now()
    delay = (first_run_time - now).total_seconds()
    if delay > 0:
        await asyncio.sleep(delay)
    while True:
        await task_func()
        await asyncio.sleep(interval_minutes * 60)