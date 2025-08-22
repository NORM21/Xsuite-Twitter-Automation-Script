import asyncio

async def update_profile(page, name=None, bio=None, location=None):
    await page.goto("https://x.com/settings/profile")
    await asyncio.sleep(2)
    if name:
        name_box = await page.get_by_role("textbox", name="Name")
        if name_box:
            await name_box.fill(name)
    if bio:
        bio_box = await page.get_by_role("textbox", name="Bio")
        if bio_box:
            await bio_box.fill(bio)
    if location:
        loc_box = await page.get_by_role("textbox", name="Location")
        if loc_box:
            await loc_box.fill(location)
    save_btn = await page.get_by_test_id("Profile_Save_Button")
    if save_btn:
        await save_btn.click()
        await asyncio.sleep(2)

async def pin_unpin_tweet(page, tweet_url, pin=True):
    await page.goto(tweet_url)
    await asyncio.sleep(2)
    caret_btn = await page.get_by_test_id("caret")
    if caret_btn:
        await caret_btn.click()
        await asyncio.sleep(1)
        if pin:
            pin_btn = await page.get_by_test_id("pin")
            if pin_btn:
                await pin_btn.click()
                await asyncio.sleep(1)
                confirm_btn = await page.get_by_test_id("confirmationSheetConfirm")
                if confirm_btn:
                    await confirm_btn.click()
        else:
            unpin_btn = await page.get_by_test_id("unpin")
            if unpin_btn:
                await unpin_btn.click()
                await asyncio.sleep(1)
                confirm_btn = await page.get_by_test_id("confirmationSheetConfirm")
                if confirm_btn:
                    await confirm_btn.click()
    await asyncio.sleep(2)