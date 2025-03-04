import praw
import time
import cred
from datetime import datetime, timedelta, UTC

# Subreddit to monitor
SUBREDDIT_NAME = "reply_timer_test"
# SUBREDDIT_NAME = "whereintheworld"

# Time threshold
CHECK_MINS = 1

def authenticate():
    """Authenticate with Reddit API."""
    return praw.Reddit(
        client_id=cred.REDDIT_CLIENT_ID,
        client_secret=cred.REDDIT_CLIENT_SECRET,
        username=cred.REDDIT_USERNAME,
        password=cred.REDDIT_PASSWORD,
        user_agent=cred.USER_AGENT
    )

def check_posts_for_op_reply(reddit):
    """Check if OP has replied to their own post within the time threshold."""
    subreddit = reddit.subreddit(SUBREDDIT_NAME)
    current_time = datetime.now(UTC)

    for post in subreddit.new(limit=50):  # Adjust limit as needed
        post_created_time = datetime.fromtimestamp(post.created_utc, UTC)
        if (current_time - post_created_time) > timedelta(minutes=CHECK_MINS):
            op_replied = any(comment.author == post.author for comment in post.comments.list())
            if post.comments.list() and not op_replied:
                print(f"OP did not reply in time: {post.title}. url: {post.url}")
                post.report(reason="")

def main():
    reddit = authenticate()
    print("Authentication successful. Scanning posts")
    check_posts_for_op_reply(reddit)
    print("Scanning done")

if __name__ == "__main__":
    main()
