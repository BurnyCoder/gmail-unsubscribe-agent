# /// script
# dependencies = [
#   "python-dotenv",
#   "langchain-openai",
#   "langchain-anthropic",
#   "browser-use",
#   "sqlite3",
# ]
# ///

import asyncio
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Tuple

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from browser_use import ActionResult, Agent, Browser, BrowserConfig, Controller

load_dotenv()

BROWSER_CONFIG = BrowserConfig(
    # To launch real browser:
    # chrome_instance_path='/Applications/Google Chrome Dev.app/Contents/MacOS/Google Chrome Dev',
    # extra_chromium_args=['--profile-directory=Profile 12'], # ✏️ EDIT THIS TO YOUR PROFILE
    # To reuse running browser:
    cdp_url="http://localhost:9222",
)

# - Also extract who I'm following and who's following me
task = """
Extract tweets from:
- My X/Twitter "For you" feed
- My X/Twitter "Following" feed

Stop at 20 tweets.
List tweets about Claude.

(Be sure to call extract_tweets to get the tweets)
"""

controller = Controller(exclude_actions=["google_search"])


def store_tweets_to_db(tweets: List[Dict]) -> Tuple[int, int]:
    """Store tweets to SQLite DB. Returns (stored_count, updated_count)."""
    conn = sqlite3.connect("tweets.db")
    cursor = conn.cursor()

    with open("schema.sql", "r") as f:
        cursor.executescript(f.read())

    stored = 0
    duplicates = 0
    for tweet in tweets:
        try:
            cursor.execute(
                """
                INSERT INTO tweets (id, content, author, timestamp, likes, retweets, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    str(tweet.get("id")),
                    tweet.get("text"),
                    tweet.get("author"),
                    tweet.get("timestamp"),
                    tweet.get("likes", 0),
                    tweet.get("retweets", 0),
                    json.dumps(tweet),
                ),
            )
            stored += 1
        except sqlite3.IntegrityError:
            duplicates += 1
            cursor.execute(
                """
                UPDATE tweets 
                SET content=?, author=?, timestamp=?, likes=?, retweets=?, raw_data=?
                WHERE id=?
            """,
                (
                    tweet.get("text"),
                    tweet.get("author"),
                    tweet.get("timestamp"),
                    tweet.get("likes", 0),
                    tweet.get("retweets", 0),
                    json.dumps(tweet),
                    str(tweet.get("id")),
                ),
            )

    conn.commit()
    conn.close()
    return stored, duplicates


@controller.action("Ask user for information")
def ask_human(question: str) -> str:
    answer = input(f"\n{question}\nInput: ")
    return ActionResult(extracted_content=answer)  # type: ignore


@controller.action("Extract tweets")
async def extract_tweets(amount: int, browser: Browser):
    page = await browser.get_current_page()  # type: ignore

    # Set the target amount in the browser context
    await page.evaluate(f"window.targetTweetAmount = {amount};")

    with open("jk_scrape_tweets.js", "r") as f:
        script = f.read()
    await page.evaluate(script)  # actually don't await
    print("🕷️ Scraping script evaluated...")

    # Using polling instead of page.wait_for_function because Twitter's Content Security Policy (CSP)
    # blocks evaluation of dynamic JavaScript. This approach only uses simple property access which is allowed by CSP.
    try:
        print("🕷️ Waiting for target amount of tweets...")
        start_time = datetime.now()
        timeout = 120  # seconds

        while True:
            tweets = await page.evaluate("window.scrapedTweets || []")
            if len(tweets) >= amount:
                print(f"🕷️ Got {len(tweets)} tweets")
                break

            if (datetime.now() - start_time).seconds > timeout:
                print(f"🕷️ Timeout reached before getting {amount} tweets")
                break

            await asyncio.sleep(2)  # Poll every 2 seconds
    except Exception as e:
        print(f"🕷️ Error while waiting for tweets: {e}")

    try:
        # Get whatever tweets we have
        tweets = await page.evaluate("window.scrapedTweets || []")
        print(f"🕷️ Scraped {len(tweets)} tweets")

        if not tweets:
            return ActionResult(error="No tweets were scraped")

        # Store tweets in SQLite
        stored, duplicates = store_tweets_to_db(tweets)
        print(f"🕷️ Stored {stored} new tweets, updated {duplicates} existing tweets")

        # Return structured tweet data
        return ActionResult(extracted_content=str(tweets))

    except Exception as e:
        print(f"Error processing tweets: {e}")
        return ActionResult(error=f"Failed to process tweets: {str(e)}")


browser = Browser(config=BROWSER_CONFIG)


agent = Agent(
    task=task,
    llm=ChatAnthropic(model="claude-3-5-sonnet-20240620"),
    controller=controller,
    browser=browser,
    initial_actions=[
        # {'open_tab': {'url': 'https://x.com/home'}},
        # {'extract_tweets': {'amount': 20}},
    ],
    save_conversation_path="logs/conversation",
)


async def main():
    history = await agent.run()
    print("=" * 80)
    print(history.final_result())
    print("=" * 80)
    input("Press Enter to close the browser...")
    await browser.close()


if __name__ == "__main__":
    asyncio.run(main()) 