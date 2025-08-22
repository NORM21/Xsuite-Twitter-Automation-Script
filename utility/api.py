import json
import os
import logging

COOKIES_FILE = "cookies.json"

async def save_cookies(self):
    cookies = await self.context.cookies()
    with open("cookies.json", "w", encoding="utf-8") as f:
        json.dump(cookies, f)

async def load_cookies(self):
    try:
        with open("cookies.json", "r", encoding="utf-8") as f:
            cookies = json.load(f)
        await self.context.add_cookies(cookies)
    except Exception:
        pass

async def login_to_x(page, username, password):
    await page.goto("https://x.com/i/flow/login")
    logging.info("Navigated to login page.")

    await page.fill('input[name="text"]', username)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(2000)

    # Sometimes X asks for username again
    if await page.query_selector('input[name="text"]'):
        await page.fill('input[name="text"]', username)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(2000)

    await page.fill('input[name="password"]', password)
    await page.keyboard.press('Enter')
    logging.info("Credentials entered.")

    await page.wait_for_selector('a[aria-label="Messages"], nav[role="navigation"]', timeout=30000)
    logging.info("Login process complete.")
