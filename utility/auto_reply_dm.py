import asyncio

async def auto_reply_dms(page, reply_text, max_replies=10):
    await page.goto("https://x.com/messages")
    await asyncio.sleep(3)
    replied = 0
    conversations = await page.locator('div[data-testid="conversation"]').all()
    for convo in conversations:
        try:
            await convo.click()
            await asyncio.sleep(2)
            input_box = await page.get_by_test_id("dmComposerTextInput")
            if input_box:
                await input_box.fill(reply_text)
                send_btn = await page.get_by_test_id("dmComposerSendButton")
                if send_btn:
                    await send_btn.click()
                    replied += 1
                    await asyncio.sleep(2)
                    if replied >= max_replies:
                        break
        except Exception:
            continue