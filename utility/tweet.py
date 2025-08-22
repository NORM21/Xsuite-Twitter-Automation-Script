import logging
import asyncio

async def post_tweet(page, text):
    try:
        await page.goto("https://x.com/compose/post")
        await page.wait_for_selector('div[data-testid="tweetTextarea_0"][role="textbox"]', timeout=15000)
        tweet_box = await page.query_selector('div[data-testid="tweetTextarea_0"][role="textbox"]')
        if not tweet_box:
            logging.warning("Tweet box not found.")
            return False
        await tweet_box.click()
        await tweet_box.type(text)
        await page.wait_for_selector('button[data-testid="tweetButton"]:not([aria-disabled="true"])', timeout=10000)
        tweet_btn = await page.query_selector('button[data-testid="tweetButton"]:not([aria-disabled="true"])')
        if not tweet_btn:
            logging.warning("Tweet button not found or not enabled.")
            return False
        await tweet_btn.click()
        await asyncio.sleep(2)
        logging.info("Tweet posted successfully.")
        return True
    except Exception as e:
        logging.error(f"Error while posting tweet: {e}")
