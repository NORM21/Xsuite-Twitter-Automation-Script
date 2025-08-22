import asyncio

async def auto_quote_tweets_by_hashtag(page, hashtag, quote_text, max_quotes=5):
    await page.goto(f"https://x.com/search?q=%23{hashtag}&src=typed_query")
    await asyncio.sleep(2)
    quoted = 0
    articles = await page.locator('article').all()
    for article in articles:
        try:
            retweet_btn = await article.get_by_test_id("retweet")
            if retweet_btn:
                await retweet_btn.click()
                await asyncio.sleep(1)
                quote_btn = await page.get_by_role("menuitem", name="Quote")
                if quote_btn:
                    await quote_btn.click()
                    await asyncio.sleep(1)
                    await page.get_by_test_id("tweetTextarea_0").fill(quote_text)
                    await asyncio.sleep(1)
                    tweet_btn = await page.get_by_test_id("tweetButton")
                    if tweet_btn:
                        await tweet_btn.click()
                        quoted += 1
                        await asyncio.sleep(2)
                        if quoted >= max_quotes:
                            break
        except Exception:
            continue