import praw
import time
import cred
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta, UTC

LOG_FILE = "reply-timer.log"
MAX_LOG_BYTES = 1 * 1024 * 1024  # 1 MB
BACKUP_COUNT = 1

logger = logging.getLogger("reply-timer")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_BYTES, backupCount=BACKUP_COUNT)
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(file_handler)

# Subreddit to monitor
# SUBREDDIT_NAME = "reply_timer_test"
SUBREDDIT_NAME = "whereintheworld"

# Time threshold
CHECK_MINS = 60 * 10

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
        has_comment = False
        has_op_reply = False
        for comment in post.comments:
            comment_created_time = datetime.fromtimestamp(comment.created_utc, UTC)
            if comment.author != post.author and comment.author != 'AutoModerator':
                if (current_time - comment_created_time) > timedelta(minutes=CHECK_MINS):
                    has_comment = True
                has_op_reply = has_op_reply or any(reply.author == post.author for reply in comment.replies.list())

        if has_comment and not has_op_reply:
            logger.info("OP did not reply in time: %s. url: %s", post.title, post.url)
            post.report(reason="")

def main():
    reddit = authenticate()
    logger.info("Authentication successful. Scanning posts")
    check_posts_for_op_reply(reddit)
    logger.info("Scanning done")

if __name__ == "__main__":
    main()
