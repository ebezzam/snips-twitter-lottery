#!/usr/bin/env python2
from hermes_python.hermes import Hermes
import random
import tweepy
import threading
import api_keys


MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

# intents
INTENT_START = "bezzam:start_game"
INTENT_WINNER = "bezzam:winner"
INTENT_STOP = "bezzam:stop_game"

# target handle and tweet
twitter_handle = "realDonaldTrump"
tweet_id = 1060194964351660033  # Trump tweet to test large number of RT
rt_count = 100

# variables that contains the user credentials to access Twitter API
access_token = api_keys.access_token
access_token_secret = api_keys.access_token_secret
consumer_key = api_keys.consumer_key
consumer_secret = api_keys.consumer_secret

# authenticate and connect
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# store participants
tweet_lottery = dict()


class ExtractRetweetThread(threading.Thread):

    def __init__(self, handle, tweet, rt_count):
        super(ExtractRetweetThread, self).__init__()
        self.handle = handle
        self.tweet = tweet
        self.rt_count = rt_count
        self.rt_screen_names = None
        self.participants = []
        self.done = False

    def run(self):

        # get people who retweeted
        results = api.retweets(self.tweet, count=self.rt_count)
        self.rt_screen_names = [r.user.screen_name for r in results]

        # check which ones are followers
        for sn in self.rt_screen_names:
            fship = api.show_friendship(source_screen_name=self.handle,
                                        target_screen_name=sn)
            if fship[0].followed_by:
                self.participants.append(str(sn))

        self.done = True


def user_start_game(hermes, intent_message):
    session_id = intent_message.session_id
    tts = "Starting game."
    hermes.publish_end_session(session_id, tts)


def user_collect(hermes, intent_message):
    session_id = intent_message.session_id

    tweet_lottery[tweet_id] = ExtractRetweetThread(twitter_handle, tweet_id, rt_count)
    tweet_lottery[tweet_id].start()
    tts = "I've started collecting the usernames. This will take a couple minutes."
    hermes.publish_end_session(session_id, tts)

    # # get people who retweeted
    # results = api.retweets(tweet_id, count=100)
    # screen_names = [r.user.screen_name for r in results]
    #
    # # check which ones are followers
    # _part = []
    # for sn in screen_names:
    #     fship = api.show_friendship(source_screen_name=twitter_handle,
    #                                 target_screen_name=sn)
    #     if fship[0].followed_by:
    #         _part.append(str(sn))
    #
    # try:
    #     participants = _part
    #     tts = "Stopping game. I've collected {} participants.".format(len(_part))
    # except:
    #     tts = "Please ask to start the game first!"

    # hermes.publish_end_session(session_id, tts)


def get_winner(hermes, intent_message):
    session_id = intent_message.session_id

    if tweet_lottery[tweet_id].done:
        participants = tweet_lottery[tweet_id].participants
        tts = "I've collected {} participants. The winner is {}.".format(len(participants),
                                                                         random.choice(participants))
        del tweet_lottery[tweet_id]
    else:
        tts = "Sorry I am still collecting the participants."
    hermes.publish_end_session(session_id, tts)


with Hermes(MQTT_ADDR) as h:
    h.subscribe_intent(INTENT_START, user_start_game) \
     .subscribe_intent(INTENT_STOP, user_collect) \
     .subscribe_intent(INTENT_WINNER, get_winner).start()

