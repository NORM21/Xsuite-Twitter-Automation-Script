import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import asyncio
from datetime import datetime
import json

# Import your utility functions here
from utility.send_messages import send_messages, send_dm_with_media
from utility.tweet import post_tweet
from utility.retweet_delete import delete_retweets
from utility.scheduled_tweets import schedule_tweet
from utility.scheduled_dms import schedule_dm
from utility.like import like_tweets_by_hashtag
from utility.retweet import retweet_by_hashtag
from utility.follow import auto_follow_users, unfollow_nonfollowers, export_followers
from utility.profile import update_profile, pin_unpin_tweet
from utility.block import block_users_from_list, mute_users_from_list
from utility.analytics import export_analytics
from utility.reply import auto_reply_mentions
from utility.bookmark import bookmark_tweets_by_hashtag
from utility.delete_tweet import auto_delete_recent_tweets
from utility.like_followers import auto_like_followers_tweets
from utility.trending import scrape_trending_topics
from utility.scrape_tweets import scrape_recent_tweets
from utility.follow_back import auto_follow_back
from utility.export_following import export_following
from utility.auto_mute_followers import auto_mute_followers
from utility.scrape_notifications import scrape_notifications
from utility.auto_reply_dm import auto_reply_dms
from utility.scrape_bookmarks import scrape_bookmarks
from utility.delete_bookmarks import delete_bookmarks
from utility.auto_quote import auto_quote_tweets_by_hashtag
from utility.scrape_poll import scrape_poll_results
from utility.bookmark_keyword import bookmark_tweets_by_keyword
from utility.scrape_media_tweets import scrape_media_tweets
from utility.auto_report import auto_report_tweets_by_keyword

class LoginDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("X Login")
        self.resizable(False, False)
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.twofa = tk.StringVar()
        self.result = None

        ttk.Label(self, text="Username or Email:").pack(padx=10, pady=(10, 0), anchor="w")
        ttk.Entry(self, textvariable=self.username, width=30).pack(padx=10, pady=2)
        ttk.Label(self, text="Password:").pack(padx=10, pady=(10, 0), anchor="w")
        ttk.Entry(self, textvariable=self.password, show="*", width=30).pack(padx=10, pady=2)
        self.twofa_label = ttk.Label(self, text="2FA Code (if prompted):")
        self.twofa_entry = ttk.Entry(self, textvariable=self.twofa, width=30)
        self.twofa_label.pack_forget()
        self.twofa_entry.pack_forget()
        self.submit_btn = ttk.Button(self, text="Login", command=self.on_submit)
        self.submit_btn.pack(pady=10)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.grab_set()
        self.wait_window(self)

    def ask_2fa(self):
        self.twofa_label.pack(padx=10, pady=(10, 0), anchor="w")
        self.twofa_entry.pack(padx=10, pady=2)
        self.submit_btn.config(text="Submit 2FA")

    def on_submit(self):
        self.result = {
            "username": self.username.get(),
            "password": self.password.get(),
            "twofa": self.twofa.get()
        }
        self.destroy()

    def on_close(self):
        self.result = None
        self.destroy()

class XAutomationGUI:
    def __init__(self, root):
        self.root = root
        self.page = None
        self.status_var = tk.StringVar(value="Initializing browser...")
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()
        self.setup_gui()
        self.disable_buttons()
        self.root.after(100, self.ask_login)
        self.stop_requested = False

    def ask_login(self):
        dlg = LoginDialog(self.root)
        if dlg.result is None:
            self.root.destroy()
            return
        self.username = dlg.result["username"]
        self.password = dlg.result["password"]
        self.twofa = dlg.result["twofa"]
        self.run_async_task(self.init_playwright())

    def run_async_task(self, coro):
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    async def init_playwright(self):
        from playwright.async_api import async_playwright
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            self.root.after(0, lambda: self.status_var.set("Browser ready. Logging in..."))
            await self.page.goto("https://x.com/i/flow/login")
            await self.page.wait_for_selector('input[name="text"]', timeout=15000)
            await self.page.fill('input[name="text"]', self.username)
            await self.page.keyboard.press('Enter')
            await self.page.wait_for_timeout(2000)
            if await self.page.query_selector('input[name="text"]'):
                await self.page.fill('input[name="text"]', self.username)
                await self.page.keyboard.press('Enter')
                await self.page.wait_for_timeout(2000)
            await self.page.wait_for_selector('input[name="password"]', timeout=15000)
            await self.page.fill('input[name="password"]', self.password)
            await self.page.keyboard.press('Enter')
            await self.page.wait_for_timeout(2000)
            if await self.page.query_selector('input[name="verification_code"]'):
                self.root.after(0, self.ask_2fa)
                while not hasattr(self, "twofa_code") or not self.twofa_code:
                    await asyncio.sleep(0.1)
                await self.page.fill('input[name="verification_code"]', self.twofa_code)
                await self.page.keyboard.press('Enter')
                await self.page.wait_for_timeout(2000)
            await self.page.wait_for_selector('a[aria-label="Messages"], nav[role="navigation"]', timeout=30000)
            self.root.after(0, lambda: self.status_var.set("Login complete. Ready!"))
            self.root.after(0, self.enable_buttons)
        except Exception as e:
            self.root.after(0, lambda e=e: self.status_var.set(f"Login failed: {e}"))
            self.page = None
    import json
from tkinter import simpledialog

def load_accounts():
    with open("accounts.json", "r", encoding="utf-8") as f:
        return json.load(f)

def switch_account_action(self):
    accounts = load_accounts()
    usernames = [acc["username"] for acc in accounts]
    selected = simpledialog.askstring("Switch Account", f"Choose account:\n{usernames}", parent=self.root)
    if selected and selected in usernames:
        account = next(acc for acc in accounts if acc["username"] == selected)
        self.username = account["username"]
        self.password = account["password"]
        self.twofa = ""
        self.status_var.set(f"Switching to {self.username}...")
        self.run_async_task(self.init_playwright())
        
    def ask_2fa(self):
        dlg = LoginDialog(self.root)
        dlg.ask_2fa()
        self.twofa_code = dlg.twofa.get()

    def disable_buttons(self):
        for btn in self.all_buttons:
            btn.config(state=tk.DISABLED)

    def enable_buttons(self):
        for btn in self.all_buttons:
            btn.config(state=tk.NORMAL)

    def stop_operations(self):
        self.stop_requested = True

    # --- Core Actions ---
    def send_dm_action(self):
        if not self.page:
            messagebox.showerror("Error", "Browser or login not ready!")
            return
        message = self.msg_text.get("1.0", tk.END).strip()
        skip = []
        target = []
        dry = self.dry_var.get()
        self.status_var.set("Sending DMs...")
        self.run_async_task(send_messages(self.page, message, skip, target, dry_run=dry))

    def send_dm_media_action(self):
        if not self.page:
            messagebox.showerror("Error", "Browser or login not ready!")
            return
        username = simpledialog.askstring("Username", "Enter recipient username:", parent=self.root)
        message = self.msg_text.get("1.0", tk.END).strip()
        media_path = filedialog.askopenfilename(title="Select Media File")
        if username and media_path:
            self.status_var.set(f"Sending DM with media to {username}...")
            self.run_async_task(send_dm_with_media(self.page, username, message, media_path))

    def post_tweet_action(self):
        if not self.page:
            messagebox.showerror("Error", "Browser or login not ready!")
            return
        tweet = self.tweet_text.get("1.0", tk.END).strip()
        self.status_var.set("Posting tweet...")
        self.run_async_task(self._post_tweet_async(tweet))

    async def _post_tweet_async(self, tweet):
        result = await post_tweet(self.page, tweet)
        if result:
            self.root.after(0, lambda: self.status_var.set("Tweet posted."))
        else:
            self.root.after(0, lambda: self.status_var.set("Tweet failed."))

    def schedule_post_action(self):
        if not self.page:
            messagebox.showerror("Error", "Browser or login not ready!")
            return
        tweet = self.tweet_text.get("1.0", tk.END).strip()
        date_str = self.sched_entry.get()
        try:
            scheduled_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except Exception:
            messagebox.showerror("Error", "Invalid schedule date/time format.")
            return
        self.status_var.set(f"Tweet scheduled for {date_str}")
        self.run_async_task(schedule_tweet(self.page, tweet, scheduled_time))

    def schedule_dm_action(self):
        if not self.page:
            messagebox.showerror("Error", "Browser or login not ready!")
            return
        usernames = simpledialog.askstring("Usernames", "Enter comma-separated usernames:", parent=self.root)
        if not usernames:
            return
        usernames = [u.strip() for u in usernames.split(",") if u.strip()]
        message = self.msg_text.get("1.0", tk.END).strip()
        date_str = self.sched_entry.get()
        try:
            scheduled_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except Exception:
            messagebox.showerror("Error", "Invalid schedule date/time format.")
            return
        self.status_var.set(f"DMs scheduled for {date_str}")
        self.run_async_task(schedule_dm(self.page, usernames, message, scheduled_time))

    def delete_retweets_action(self):
        if not self.page:
            messagebox.showerror("Error", "Browser or login not ready!")
            return
        username = self.username
        self.status_var.set("Deleting retweets...")
        self.run_async_task(delete_retweets(self.page, username))

    def like_hashtag_action(self):
        hashtag = simpledialog.askstring("Hashtag", "Enter hashtag (without #):", parent=self.root)
        if hashtag:
            self.status_var.set(f"Liking tweets with #{hashtag}...")
            self.run_async_task(like_tweets_by_hashtag(self.page, hashtag))

    def retweet_hashtag_action(self):
        hashtag = simpledialog.askstring("Hashtag", "Enter hashtag (without #):", parent=self.root)
        if hashtag:
            self.status_var.set(f"Retweeting tweets with #{hashtag}...")
            self.run_async_task(retweet_by_hashtag(self.page, hashtag))

    def auto_follow_action(self):
        file_path = filedialog.askopenfilename(title="Select User List File")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                usernames = [line.strip() for line in f if line.strip()]
            self.status_var.set("Auto-following users...")
            self.run_async_task(auto_follow_users(self.page, usernames))

    def unfollow_action(self):
        self.status_var.set("Unfollowing non-followers...")
        self.run_async_task(unfollow_nonfollowers(self.page, self.username))

    def export_followers_action(self):
        file_path = filedialog.asksaveasfilename(title="Save Followers CSV", defaultextension=".csv")
        if file_path:
            self.status_var.set("Exporting followers...")
            self.run_async_task(export_followers(self.page, self.username, file_path))

    def update_profile_action(self):
        name = simpledialog.askstring("Name", "Enter new display name:", parent=self.root)
        bio = simpledialog.askstring("Bio", "Enter new bio:", parent=self.root)
        location = simpledialog.askstring("Location", "Enter new location:", parent=self.root)
        self.status_var.set("Updating profile...")
        self.run_async_task(update_profile(self.page, name, bio, location))

    def pin_tweet_action(self):
        tweet_url = simpledialog.askstring("Tweet URL", "Enter tweet URL to pin/unpin:", parent=self.root)
        pin = messagebox.askyesno("Pin", "Pin this tweet? (No = Unpin)")
        self.status_var.set("Pinning/unpinning tweet...")
        self.run_async_task(pin_unpin_tweet(self.page, tweet_url, pin))

    def block_users_action(self):
        file_path = filedialog.askopenfilename(title="Select User List File")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                usernames = [line.strip() for line in f if line.strip()]
            self.status_var.set("Blocking users...")
            self.run_async_task(block_users_from_list(self.page, usernames))

    def mute_users_action(self):
        file_path = filedialog.askopenfilename(title="Select User List File")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                usernames = [line.strip() for line in f if line.strip()]
            self.status_var.set("Muting users...")
            self.run_async_task(mute_users_from_list(self.page, usernames))

    def analytics_action(self):
        file_path = filedialog.asksaveasfilename(title="Save Analytics CSV", defaultextension=".csv")
        if file_path:
            self.status_var.set("Exporting analytics...")
            self.run_async_task(export_analytics(self.page, self.username, file_path))

    def reply_mentions_action(self):
        reply_text = simpledialog.askstring("Reply Text", "Enter reply text:", parent=self.root)
        if reply_text:
            self.status_var.set("Auto-replying to mentions...")
            self.run_async_task(auto_reply_mentions(self.page, reply_text))

    def bookmark_hashtag_action(self):
        hashtag = simpledialog.askstring("Hashtag", "Enter hashtag (without #):", parent=self.root)
        if hashtag:
            self.status_var.set(f"Bookmarking tweets with #{hashtag}...")
            self.run_async_task(bookmark_tweets_by_hashtag(self.page, hashtag))

    def auto_delete_tweets_action(self):
        self.status_var.set("Auto-deleting recent tweets...")
        self.run_async_task(auto_delete_recent_tweets(self.page, self.username))

    # --- Advanced Features ---
    def like_followers_action(self):
        file_path = filedialog.askopenfilename(title="Select Followers List File")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                followers = [line.strip() for line in f if line.strip()]
            self.status_var.set("Auto-liking followers' tweets...")
            self.run_async_task(auto_like_followers_tweets(self.page, followers))

    def trending_topics_action(self):
        self.status_var.set("Scraping trending topics...")
        self.run_async_task(self._show_trending_topics())

    async def _show_trending_topics(self):
        topics = await scrape_trending_topics(self.page)
        messagebox.showinfo("Trending Topics", "\n".join(topics) if topics else "No topics found.")

    def scrape_tweets_action(self):
        username = simpledialog.askstring("Username", "Enter username to scrape tweets:", parent=self.root)
        if username:
            self.status_var.set(f"Scraping tweets for {username}...")
            self.run_async_task(self._show_scraped_tweets(username))

    async def _show_scraped_tweets(self, username):
        tweets = await scrape_recent_tweets(self.page, username)
        messagebox.showinfo("Recent Tweets", "\n\n".join(tweets) if tweets else "No tweets found.")

    def follow_back_action(self):
        self.status_var.set("Auto-following back new followers...")
        self.run_async_task(auto_follow_back(self.page, self.username))

    def export_following_action(self):
        file_path = filedialog.asksaveasfilename(title="Save Following CSV", defaultextension=".csv")
        if file_path:
            self.status_var.set("Exporting following...")
            self.run_async_task(export_following(self.page, self.username, file_path))

    def auto_mute_followers_action(self):
        file_path = filedialog.askopenfilename(title="Select Followers List File")
        if file_path:
            with open(file_path, "r", encoding="utf-8") as f:
                followers = [line.strip() for line in f if line.strip()]
            self.status_var.set("Auto-muting followers...")
            self.run_async_task(auto_mute_followers(self.page, followers))

    def scrape_notifications_action(self):
        self.status_var.set("Scraping notifications...")
        self.run_async_task(self._show_notifications())

    async def _show_notifications(self):
        notifications = await scrape_notifications(self.page)
        messagebox.showinfo("Notifications", "\n\n".join(notifications) if notifications else "No notifications found.")

    def auto_reply_dm_action(self):
        reply_text = simpledialog.askstring("Reply Text", "Enter DM reply text:", parent=self.root)
        if reply_text:
            self.status_var.set("Auto-replying to DMs...")
            self.run_async_task(auto_reply_dms(self.page, reply_text))

    def scrape_bookmarks_action(self):
        self.status_var.set("Scraping bookmarks...")
        self.run_async_task(self._show_bookmarks())

    async def _show_bookmarks(self):
        bookmarks = await scrape_bookmarks(self.page)
        messagebox.showinfo("Bookmarks", "\n\n".join(bookmarks) if bookmarks else "No bookmarks found.")

    def delete_bookmarks_action(self):
        self.status_var.set("Deleting bookmarks...")
        self.run_async_task(delete_bookmarks(self.page))

    def auto_quote_action(self):
    
        hashtag = simpledialog.askstring("Hashtag", "Enter hashtag (without #):", parent=self.root)
        quote_text = simpledialog.askstring("Quote Text", "Enter quote text:", parent=self.root)
        if hashtag and quote_text:
            self.status_var.set(f"Auto-quoting tweets with #{hashtag}...")
            self.run_async_task(auto_quote_tweets_by_hashtag(self.page, hashtag, quote_text))
    

    def scrape_poll_action(self):
        tweet_url = simpledialog.askstring("Tweet URL", "Enter tweet URL with poll:", parent=self.root)
        if tweet_url:
            self.status_var.set("Scraping poll results...")
            self.run_async_task(self._show_poll_results(tweet_url))

    async def _show_poll_results(self, tweet_url):
        results = await scrape_poll_results(self.page, tweet_url)
        messagebox.showinfo("Poll Results", "\n".join(results) if results else "No poll found.")

    def bookmark_keyword_action(self):
        keyword = simpledialog.askstring("Keyword", "Enter keyword:", parent=self.root)
        if keyword:
            self.status_var.set(f"Bookmarking tweets with keyword '{keyword}'...")
            self.run_async_task(bookmark_tweets_by_keyword(self.page, keyword))

    def scrape_media_tweets_action(self):
        username = simpledialog.askstring("Username", "Enter username to scrape media tweets:", parent=self.root)
        if username:
            self.status_var.set(f"Scraping media tweets for {username}...")
            self.run_async_task(self._show_media_tweets(username))

    async def _show_media_tweets(self, username):
        tweets = await scrape_media_tweets(self.page, username)
        messagebox.showinfo("Media Tweets", "\n\n".join(tweets) if tweets else "No media tweets found.")

    def auto_report_action(self):
        keyword = simpledialog.askstring("Keyword", "Enter keyword to report tweets:", parent=self.root)
        if keyword:
            self.status_var.set(f"Auto-reporting tweets with keyword '{keyword}'...")
            self.run_async_task(auto_report_tweets_by_keyword(self.page, keyword))

    def on_close(self):
        self.run_async_task(self._close_playwright())
        self.root.destroy()

    async def _close_playwright(self):
        if hasattr(self, "browser") and self.browser:
            await self.browser.close()
        if hasattr(self, "playwright") and self.playwright:
            await self.playwright.stop()

    def setup_gui(self):
        self.root.title("X Automation Suite")
        self.root.geometry("900x1200")
        style = ttk.Style(self.root)
        style.theme_use('clam')

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        status_bar.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(main_frame, text="DM Message:").pack(anchor="w")
        self.msg_text = scrolledtext.ScrolledText(main_frame, width=60, height=4)
        self.msg_text.pack()

        self.dry_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Dry Run", variable=self.dry_var).pack(anchor="w")

        ttk.Label(main_frame, text="Schedule (YYYY-MM-DD HH:MM):").pack(anchor="w")
        self.sched_entry = ttk.Entry(main_frame, width=25)
        self.sched_entry.pack()

        ttk.Label(main_frame, text="Tweet:").pack(anchor="w")
        self.tweet_text = scrolledtext.ScrolledText(main_frame, width=60, height=2)
        self.tweet_text.pack()

        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons for all features
        self.send_dm_btn = ttk.Button(main_frame, text="Send DMs", command=self.send_dm_action)
        self.send_dm_media_btn = ttk.Button(main_frame, text="Send DM with Media", command=self.send_dm_media_action)
        self.schedule_dm_btn = ttk.Button(main_frame, text="Schedule DMs", command=self.schedule_dm_action)
        self.post_tweet_btn = ttk.Button(main_frame, text="Post Tweet", command=self.post_tweet_action)
        self.schedule_post_btn = ttk.Button(main_frame, text="Schedule Post", command=self.schedule_post_action)
        self.delete_retweets_btn = ttk.Button(main_frame, text="Delete Retweets", command=self.delete_retweets_action)
        self.like_hashtag_btn = ttk.Button(main_frame, text="Like Tweets by Hashtag", command=self.like_hashtag_action)
        self.retweet_hashtag_btn = ttk.Button(main_frame, text="Retweet by Hashtag", command=self.retweet_hashtag_action)
        self.auto_follow_btn = ttk.Button(main_frame, text="Auto-Follow from List", command=self.auto_follow_action)
        self.unfollow_btn = ttk.Button(main_frame, text="Unfollow Non-Followers", command=self.unfollow_action)
        self.export_followers_btn = ttk.Button(main_frame, text="Export Followers", command=self.export_followers_action)
        self.update_profile_btn = ttk.Button(main_frame, text="Update Profile", command=self.update_profile_action)
        self.pin_tweet_btn = ttk.Button(main_frame, text="Pin/Unpin Tweet", command=self.pin_tweet_action)
        self.block_users_btn = ttk.Button(main_frame, text="Block Users from List", command=self.block_users_action)
        self.mute_users_btn = ttk.Button(main_frame, text="Mute Users from List", command=self.mute_users_action)
        self.analytics_btn = ttk.Button(main_frame, text="Export Analytics", command=self.analytics_action)
        self.reply_mentions_btn = ttk.Button(main_frame, text="Auto-Reply to Mentions", command=self.reply_mentions_action)
        self.bookmark_hashtag_btn = ttk.Button(main_frame, text="Bookmark Tweets by Hashtag", command=self.bookmark_hashtag_action)
        self.auto_delete_tweets_btn = ttk.Button(main_frame, text="Auto-Delete Recent Tweets", command=self.auto_delete_tweets_action)
        self.like_followers_btn = ttk.Button(main_frame, text="Auto-Like Followers' Tweets", command=self.like_followers_action)
        self.trending_topics_btn = ttk.Button(main_frame, text="Scrape Trending Topics", command=self.trending_topics_action)
        self.scrape_tweets_btn = ttk.Button(main_frame, text="Scrape User's Tweets", command=self.scrape_tweets_action)
        self.follow_back_btn = ttk.Button(main_frame, text="Auto-Follow Back", command=self.follow_back_action)
        self.export_following_btn = ttk.Button(main_frame, text="Export Following", command=self.export_following_action)
        self.auto_mute_followers_btn = ttk.Button(main_frame, text="Auto-Mute Followers", command=self.auto_mute_followers_action)
        self.scrape_notifications_btn = ttk.Button(main_frame, text="Scrape Notifications", command=self.scrape_notifications_action)
        self.auto_reply_dm_btn = ttk.Button(main_frame, text="Auto-Reply to DMs", command=self.auto_reply_dm_action)
        self.scrape_bookmarks_btn = ttk.Button(main_frame, text="Scrape Bookmarks", command=self.scrape_bookmarks_action)
        self.delete_bookmarks_btn = ttk.Button(main_frame, text="Delete Bookmarks", command=self.delete_bookmarks_action)
        self.auto_quote_btn = ttk.Button(main_frame, text="Auto-Quote Tweets by Hashtag", command=self.auto_quote_action)
        self.scrape_poll_btn = ttk.Button(main_frame, text="Scrape Poll Results", command=self.scrape_poll_action)
        self.bookmark_keyword_btn = ttk.Button(main_frame, text="Bookmark Tweets by Keyword", command=self.bookmark_keyword_action)
        self.scrape_media_tweets_btn = ttk.Button(main_frame, text="Scrape Media Tweets", command=self.scrape_media_tweets_action)
        self.auto_report_btn = ttk.Button(main_frame, text="Auto-Report Tweets by Keyword", command=self.auto_report_action)
        self.stop_btn = ttk.Button(main_frame, text="Stop Operation", command=self.stop_operations)
        self.switch_account_btn = ttk.Button(main_frame, text="Switch Account", command=self.switch_account_action)

        self.all_buttons = [
            self.send_dm_btn, self.send_dm_media_btn, self.schedule_dm_btn, self.post_tweet_btn, self.schedule_post_btn,
            self.delete_retweets_btn, self.like_hashtag_btn, self.retweet_hashtag_btn, self.auto_follow_btn,
            self.unfollow_btn, self.export_followers_btn, self.update_profile_btn, self.pin_tweet_btn,
            self.block_users_btn, self.mute_users_btn, self.analytics_btn, self.reply_mentions_btn,
            self.bookmark_hashtag_btn, self.auto_delete_tweets_btn, self.like_followers_btn, self.trending_topics_btn,
            self.scrape_tweets_btn, self.follow_back_btn, self.export_following_btn, self.auto_mute_followers_btn,
            self.scrape_notifications_btn, self.auto_reply_dm_btn, self.scrape_bookmarks_btn, self.delete_bookmarks_btn,
            self.auto_quote_btn, self.scrape_poll_btn, self.bookmark_keyword_btn, self.scrape_media_tweets_btn,
            self.auto_report_btn, self.stop_btn
        ]

        for btn in self.all_buttons:
            btn.pack(pady=2, fill=tk.X, in_=scrollable_frame)

    def set_theme(self, theme_name):
        style = ttk.Style(self.root)
        style.theme_use(theme_name)

def run_gui():
    root = tk.Tk()
    app = XAutomationGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()