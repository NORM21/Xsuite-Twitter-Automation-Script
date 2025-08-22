import asyncio
import csv

async def auto_follow_users(page, usernames):
    for username in usernames:
        await page.goto(f"https://x.com/{username}")
        await asyncio.sleep(2)
        follow_btn = await page.get_by_test_id(f"{username}-follow")
        if follow_btn:
            try:
                await follow_btn.click()
                await asyncio.sleep(1)
            except Exception:
                continue

async def unfollow_nonfollowers(page, username, max_unfollows=10):
    await page.goto(f"https://x.com/{username}/following")
    await asyncio.sleep(2)
    unfollowed = 0
    while unfollowed < max_unfollows:
        unfollow_buttons = await page.locator('[data-testid$="-unfollow"]').all()
        for btn in unfollow_buttons:
            try:
                await btn.click()
                await asyncio.sleep(1)
                confirm_btn = await page.get_by_test_id("confirmationSheetConfirm")
                if confirm_btn:
                    await confirm_btn.click()
                unfollowed += 1
                await asyncio.sleep(1)
                if unfollowed >= max_unfollows:
                    break
            except Exception:
                continue
        await page.keyboard.press("PageDown")
        await asyncio.sleep(2)

async def export_followers(page, username, csv_path="followers.csv", max_followers=1000):
    followers = []
    seen_ids = set()

    async def handle_response(response):
        if "followers/list.json" in response.url and response.status == 200:
            try:
                data = await response.json()
                for user in data.get("users", []):
                    if user["id_str"] not in seen_ids:
                        followers.append(user)
                        seen_ids.add(user["id_str"])
            except Exception:
                pass

    page.on("response", handle_response)

    await page.goto(f"https://x.com/{username}/followers")
    await asyncio.sleep(3)

    last_count = 0
    for _ in range(30):
        await page.mouse.wheel(0, 10000)
        await asyncio.sleep(2)
        if len(followers) == last_count:
            break
        last_count = len(followers)
        if len(followers) >= max_followers:
            break

    page.off("response", handle_response)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_str", "screen_name", "name"])
        for user in followers[:max_followers]:
            writer.writerow([user["id_str"], user["screen_name"], user["name"]])