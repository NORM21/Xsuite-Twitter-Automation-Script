import asyncio
from playwright.async_api import async_playwright
import getpass
import logging
import requests
import csv
import random
from tqdm import tqdm


async def is_group_chat(page):
    """
    Returns True if the currently open conversation is a group chat.
    """
    try:
        panel = await page.query_selector('div[data-testid="activeRoute"]')
        if not panel:
            logging.warning("Could not find activeRoute for group check.")
            return False
        avatars = await panel.query_selector_all('a[data-testid="DM_Conversation_Avatar"]')
        for avatar in avatars:
            
            group = await avatar.query_selector('div[data-testid="MGpNUvWdU4CZcALH4gFq8sKydbPZFCUgXu"]')
            if group:
                return True
        return False  
    except Exception as e:
        logging.warning(f"Error in is_group_chat: {e}")
        return False

async def get_conversation_types(page):
    """
    Intercepts the DM API response and returns a dict:
    {conversation_id: {"type": "ONE_TO_ONE" or "GROUP_DM", "name": username}}
    """
    conversation_types = {}

    async def handle_response(response):
        if "user_updates.json" in response.url and response.status == 200:
            try:
                data = await response.json()
                conversations = data.get("inbox_initial_state", {}).get("conversations", {})
                for convo_id, convo in conversations.items():
                    convo_type = convo.get("type")
                    name = convo.get("name", "Unknown")
                    conversation_types[convo_id] = {"type": convo_type, "name": name}
            except Exception as e:
                logging.warning(f"Error parsing DM API response: {e}")

    page.on("response", handle_response)
    await page.goto("https://x.com/messages")
    await page.wait_for_timeout(5000)
    return conversation_types

async def send_messages(
    page,
    message,
    skip_list=None,
    target_list=None,
    dry_run=False,
    max_retries=2,
    export_csv="dm_results.csv"
):
    """
    Send personalized messages to all one-to-one conversations.
    Supports skip/target lists, dry run, retry logic, and CSV export.
    """
    skip_list = set(skip_list or [])
    target_list = set(target_list or [])

    conversation_types = await get_conversation_types(page)
    one_to_one = {
        cid: info for cid, info in conversation_types.items()
        if info["type"] == "ONE_TO_ONE"
    }

    # Filter by target/skip lists
    filtered = {}
    for cid, info in one_to_one.items():
        if target_list and info["name"] not in target_list:
            continue
        if info["name"] in skip_list:
            continue
        filtered[cid] = info

    # No terminal confirmation here!
    results = []
    for idx, (convo_id, info) in enumerate(filtered.items(), 1):
        username = info["name"]
        personalized = message.format(username=username)
        success = False
        error_msg = ""
        for attempt in range(max_retries + 1):
            try:
                if dry_run:
                    success = True
                    break
                await page.goto(f"https://x.com/messages/{convo_id}")
                await page.wait_for_selector('div[data-testid="dmComposerTextInput"]')
                box = await page.query_selector('div[data-testid="dmComposerTextInput"]')
                if box:
                    await box.click()
                    await box.type(personalized)
                    await page.keyboard.press("Enter")
                    success = True
                    break
                else:
                    error_msg = "Composer not found"
            except Exception as e:
                error_msg = str(e)
                await asyncio.sleep(2)
        results.append({
            "username": username,
            "conversation_id": convo_id,
            "success": success,
            "error": error_msg
        })
        await asyncio.sleep(2)

    # Export results
    with open(export_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["username", "conversation_id", "success", "error"])
        writer.writeheader()
        writer.writerows(results)
    print(f"\nDone. Results exported to {export_csv}.")

    # Progress summary
    sent = sum(1 for r in results if r["success"])
    failed = len(results) - sent
    print(f"Summary: {sent} sent, {failed} failed.")
    failed_users = [r["username"] for r in results if not r["success"]]
    if failed_users:
        with open("dm_failed.txt", "w", encoding="utf-8") as f:
            for user in failed_users:
                f.write(user + "\n")
        print("Failed usernames exported to dm_failed.txt")

async def safe_wait_for_selector(page, selector, timeout=10000):
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        return True
    except Exception:
        print(f"Selector not found: {selector}")
        new_selector = input("Enter new selector or leave blank to skip: ").strip()
        if new_selector:
            return await safe_wait_for_selector(page, new_selector, timeout)
        return False

def load_user_list(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Could not load list from {filepath}: {e}")
        return []

async def send_dm_with_media(page, username, message, media_path):
    await page.goto(f"https://x.com/messages/compose")
    await asyncio.sleep(2)
    # Search for user
    search_box = await page.query_selector('input[data-testid="searchPeople"]')
    if search_box:
        await search_box.type(username)
        await asyncio.sleep(2)
        user_result = await page.query_selector('div[data-testid="typeaheadResult"]')
        if user_result:
            await user_result.click()
            await asyncio.sleep(1)
            next_btn = await page.query_selector('div[data-testid="nextButton"]')
            if next_btn:
                await next_btn.click()
                await asyncio.sleep(2)
                # Attach media
                attach_btn = await page.query_selector('input[type="file"]')
                if attach_btn:
                    await attach_btn.set_input_files(media_path)
                    await asyncio.sleep(2)
                # Type message
                msg_box = await page.query_selector('div[data-testid="dmComposerTextInput"]')
                if msg_box:
                    await msg_box.type(message)
                    await asyncio.sleep(1)
                    send_btn = await page.query_selector('div[data-testid="dmComposerSendButton"]')
                    if send_btn:
                        await send_btn.click()
                        await asyncio.sleep(2)
