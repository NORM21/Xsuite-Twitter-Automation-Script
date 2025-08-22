import asyncio
import getpass
import logging
import os
import random
from datetime import datetime
from playwright.async_api import async_playwright
from utility.api import save_cookies, load_cookies
from utility.send_messages import send_messages, load_user_list
from utility.retweet_delete import delete_retweets
from utility.tweet import post_tweet
from utility.scheduled_tweets import schedule_task
from utility.notifications import send_email_notification
import argparse
from utility.main_gui import run_gui


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("automation.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

async def login_to_x(page, username, password):
    await page.goto("https://x.com/i/flow/login")
    logging.info("Navigated to login page.")

    await page.fill('input[name="text"]', username)
    await page.keyboard.press('Enter')
    await page.wait_for_timeout(2000)

    await page.fill('input[name="password"]', password)
    await page.keyboard.press('Enter')
    logging.info("Credentials entered.")

    await page.wait_for_selector('a[aria-label="Messages"], nav[role="navigation"]', timeout=30000)
    logging.info("Login successful.")

def parse_args():
    parser = argparse.ArgumentParser(description="X Automation Script")
    parser.add_argument("--message-file", help="Path to message template file")
    parser.add_argument("--skip-file", help="Path to skip list file")
    parser.add_argument("--target-file", help="Path to target list file")
    parser.add_argument("--dry-run", action="store_true", help="Enable dry run mode")
    parser.add_argument("--schedule", help="Schedule time (YYYY-MM-DD HH:MM)")
    return parser.parse_args()

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    # Add more
]

async def main():
    args = parse_args()

    username = input("Enter your Twitter username: ")
    password = getpass.getpass("Enter your Twitter password: ")

    cookie_file = os.getenv("X_COOKIE_FILE", "cookies.json")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(user_agent=random.choice(user_agents))

        session_loaded = await load_cookies(context, cookie_file)
        page = await context.new_page()

        if not session_loaded:
            await login_to_x(page, username, password)
            await save_cookies(context, cookie_file)
        else:
            logging.info("Using saved session cookies.")

        
        while True:
            print("\nMenu:")
            print("1. Send Messages")
            print("2. Delete Retweets")
            print("3. Post Tweet")
            print("4. Schedule Tweet")  # New option
            print("5. Schedule Messages")  # New option
            print("6. Exit")
            choice = input("Enter your choice: ")

            if choice == "1":
                msg_file = args.message_file or input("Path to message template file (leave blank to type message): ").strip()
                if msg_file:
                    with open(msg_file, "r", encoding="utf-8") as f:
                        message = f.read()
                else:
                    message = input("Enter your message (use {username} for personalization): ")

                dry_run = args.dry_run or input("Dry run? (yes/no): ").strip().lower() == "yes"
                skip_file = args.skip_file or input("Path to skip list file (leave blank to skip): ").strip()
                target_file = args.target_file or input("Path to target list file (leave blank to skip): ").strip()
                skip_list = load_user_list(skip_file) if skip_file else []
                target_list = load_user_list(target_file) if target_file else []

                retry_failed = input("Retry failed users from last run? (yes/no): ").strip().lower() == "yes"
                if retry_failed:
                    target_list = load_user_list("dm_failed.txt")
                    skip_list = []

                schedule = input("Schedule messages for later? (yes/no): ").strip().lower() == "yes"
                if schedule:
                    from datetime import datetime
                    from utility.scheduled_tweets import schedule_task
                    date_str = input("Enter scheduled date and time (YYYY-MM-DD HH:MM): ")
                    scheduled_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                    await schedule_task(
                        lambda: send_messages(page, message, skip_list, target_list, dry_run),
                        scheduled_time
                    )
                else:
                    await send_messages(page, message, skip_list, target_list, dry_run)
            elif choice == "2":
                await delete_retweets(page, username)
            elif choice == "3":
                tweet = input("Enter the tweet content: ")
                await post_tweet(page, tweet)
            elif choice == "4":
                tweet_text = input("Enter the tweet text: ")
                date_str = input("Enter scheduled date and time (YYYY-MM-DD HH:MM): ")
                try:
                    scheduled_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                    await schedule_task(page, tweet_text, scheduled_time)
                except ValueError:
                    print("Invalid date/time format.")
            elif choice == "5":
                msg_file = args.message_file or input("Path to message template file (leave blank to type message): ").strip()
                if msg_file:
                    with open(msg_file, "r", encoding="utf-8") as f:
                        message = f.read()
                else:
                    message = input("Enter your message (use {username} for personalization): ")

                dry_run = args.dry_run or input("Dry run? (yes/no): ").strip().lower() == "yes"
                skip_file = args.skip_file or input("Path to skip list file (leave blank to skip): ").strip()
                target_file = args.target_file or input("Path to target list file (leave blank to skip): ").strip()
                skip_list = load_user_list(skip_file) if skip_file else []
                target_list = load_user_list(target_file) if target_file else []

                retry_failed = input("Retry failed users from last run? (yes/no): ").strip().lower() == "yes"
                if retry_failed:
                    target_list = load_user_list("dm_failed.txt")
                    skip_list = []

                date_str = input("Enter scheduled date and time (YYYY-MM-DD HH:MM): ")
                try:
                    scheduled_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                    await schedule_task(
                        lambda: send_messages(page, message, skip_list, target_list, dry_run),
                        scheduled_time
                    )
                except ValueError:
                    print("Invalid date/time format.")
            elif choice == "6":
                break
            else:
                print("Invalid choice. Please try again.")

        await browser.close()
        logging.info("Browser closed.")

        # Optionally send email notification on completion
        send_email_notification("Automation Script Completed", "The script has finished running.")

# if __name__ == "__main__":
#     asyncio.run(main())


if __name__ == "__main__":
    run_gui()