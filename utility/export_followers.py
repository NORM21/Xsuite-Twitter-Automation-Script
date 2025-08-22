import asyncio
import csv

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