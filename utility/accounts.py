async def create_account_context(playwright, username, password, twofa=None):
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    await page.goto("https://x.com/i/flow/login")
    await page.wait_for_selector('input[name="text"]', timeout=15000)
    await page.fill('input[name="text"]', username)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(2000)
    if await page.query_selector('input[name="text"]'):
        await page.fill('input[name="text"]', username)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(2000)
    await page.wait_for_selector('input[name="password"]', timeout=15000)
    await page.fill('input[name="password"]', password)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(2000)
    if twofa and await page.query_selector('input[name="verification_code"]'):
        await page.fill('input[name="verification_code"]', twofa)
        await page.keyboard.press('Enter')
        await page.wait_for_timeout(2000)
    await page.wait_for_selector('a[aria-label="Messages"], nav[role="navigation"]', timeout=30000)
    return {"browser": browser, "context": context, "page": page}

accounts = [
  {"username": "user1", "password": "pass1"},
  {"username": "user2", "password": "pass2"}
]