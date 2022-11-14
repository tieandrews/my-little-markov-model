import os
import sys

import random

cur_dir = os.getcwd()
SRC_PATH = cur_dir[
    : cur_dir.index("my-little-markov-model") + len("my-little-markov-model")
]

# SRC_PATH = os.path.abspath(os.path.join(".."))
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

from src.models.markov_model import MarkovModel
from src.twitter.twitter_bot import TwitterBot


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

    print(introduction + tweet + hashtags)

    markov_bot = TwitterBot()
    markov_bot.create_authenticate_api()

    markov_bot.send_tweet(introduction + tweet)


if __name__ == "__main__":
    main()
