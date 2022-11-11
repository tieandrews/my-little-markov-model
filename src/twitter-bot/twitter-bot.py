# text
import tweepy
import os 
from dotenv import load_dotenv
import logging


# searches for .env file path
load_dotenv(os.path.join(os.pardir, ".env"))


# creates a logger
logger = logging.getLogger()

class TwitterBot:
    """A twitter bot that will post tweets generated from a Markov model of languages based on character frequencies in text."""

    def __init__(self):

        return None


    def create_authenticate_api(): 

        """creates and authenticates an twiter api . Access token/Cosumer keys 
        must be available 

        Returns:
            twitter_api: An authenticated twitter api that can be used to interact 
            with the twitter environment
        """
        # pulls keys/secrets from env
        consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
        consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        
        # sets up authentication
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        
        # creates twitter api object
        twitter_api = tweepy.API(auth, wait_on_rate_limit=True, 
                                 wait_on_rate_limit_notify=True)

        # tests if authentication is successful
        try:
            twitter_api.verify_credentials()
        except Exception as e:
            logger.error("Error creating API", exc_info=True)
            raise e
        logger.info("API created")

        return twitter_api 


        
    def send_tweet(twitter_api, tweet_text):

        # pseduo flag
        success = False
        
        # tries to send tweet
        try:
            twitter_api.update_status(tweet_text)
            success = True
        except Exception as e:
            logger.error("Error tweeting tweet", exc_info=False) 
            raise e

        logger.info("Tweet sent")    

        return success

