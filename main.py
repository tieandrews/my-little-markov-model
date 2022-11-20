import os
import sys

import random

# cur_dir = os.getcwd()
# SRC_PATH = cur_dir[
#     : cur_dir.index("my-little-markov-model") + len("my-little-markov-model")
# ]

# # SRC_PATH = os.path.abspath(os.path.join(".."))
# if SRC_PATH not in sys.path:
#     sys.path.append(SRC_PATH)

from src.models.markov_model import MarkovModel
from src.twitter.twitter_bot import TwitterBot

import logging
import sys
from logging.handlers import TimedRotatingFileHandler

FORMATTER = logging.Formatter(
    "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"
)
LOG_FILE = "my_app.log"


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight")
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    # with this pattern, it's rarely necessary to propagate the error up to parent
    logger.propagate = False
    return logger


def main():

    models = ["taylor-swift", "arthur-conan-doyle", "trump-tweets"]
    tweet_formatting = {
        "taylor-swift": {
            "seq_len": 180,
            "introduction": "Taylor Swifts new lyrics:\n",
            "hashtags": " #TaylorSwift",
        },
        "arthur-conan-doyle": {
            "seq_len": 240,
            "introduction": "From Arthur Conan Doyle: ",
            "hashtags": " #SherlockHolmes",
        },
        "trump-tweets": {
            "seq_len": 180,
            "introduction": "Trump Tweeting - ",
            "hashtags": " #Trump",
        },
    }

    random_model = random.choice(models)
    seq_len = tweet_formatting[random_model]["seq_len"]
    introduction = tweet_formatting[random_model]["introduction"]
    hashtags = tweet_formatting[random_model]["hashtags"]

    markov_model = MarkovModel()

    markov_model.load_production_model(model_name=random_model)

    tweet = markov_model.generate_tweet(seq_len=seq_len)

    logger.info(introduction + tweet + hashtags)

    markov_bot = TwitterBot()
    markov_bot.create_authenticate_api()

    markov_bot.send_tweet(introduction + tweet)


if __name__ == "__main__":
    logger = get_logger("markov-model")
    logger.info("Starting to generate tweet..")
    os.chdir("/code/my-little-markov-model")
    main()
    logger.info("Tweet Successfully Sent, shutting down...")
