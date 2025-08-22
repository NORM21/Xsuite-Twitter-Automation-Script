import asyncio

async def block_users_from_list(page, usernames):
    for username in usernames:
        await page.goto(f"https://x.com/{username}")
        await asyncio.sleep(2)
        await page.get_by_test_id("userActions").click()
        await asyncio.sleep(1)
        await page.get_by_test_id("block").click()
        await asyncio.sleep(1)
        await page.get_by_test_id("confirmationSheetConfirm").click()
        await asyncio.sleep(2)

async def mute_users_from_list(page, usernames):
    for username in usernames:
        await page.goto(f"https://x.com/{username}")
        await asyncio.sleep(2)
        await page.get_by_test_id("userActions").click()
        await asyncio.sleep(1)
        await page.get_by_test_id("mute").click()
        await asyncio.sleep(1)
        await page.get_by_test_id("confirmationSheetConfirm").click()
        await asyncio.sleep(2)