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
INTENT_COLLECT = "bezzam:collect_names"
INTENT_WINNER = "bezzam:winner"
INTENT_DELETE = "bezzam:delete_collection"
INTENT_KEEP = "bezzam:keep_collection"
INTENT_HOW_MANY = "bezzam:how_many_names"

# target handle and tweet
twitter_handle = "realDonaldTrump"
tweet_id = 1060194964351660033  # Trump tweet to test large number of RT
rt_count = 10

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


def delete_names(hermes, intent_message):
    session_id = intent_message.session_id
    try:
        del tweet_lottery[tweet_id]
        tts = "Deleting gathered usernames."
    except:
        tts = "No usernames to delete."
        pass
    hermes.publish_end_session(session_id, tts)


def keep_names(hermes, intent_message):
    session_id = intent_message.session_id
    try:
        participants = tweet_lottery[tweet_id].participants
        tts = "Sure thing."
    except:
        tts = "I have not gathered any participants."
    hermes.publish_end_session(session_id, tts)


def collect_names(hermes, intent_message):
    session_id = intent_message.session_id

    tweet_lottery[tweet_id] = ExtractRetweetThread(twitter_handle, tweet_id, rt_count)
    tweet_lottery[tweet_id].start()
    tts = "I've started collecting the usernames. This may take a couple minutes."
    hermes.publish_end_session(session_id, tts)


def how_many(hermes, intent_message):
    session_id = intent_message.session_id

    try:
        if tweet_lottery[tweet_id].done:
            participants = tweet_lottery[tweet_id].participants
            n_participants = len(participants)
            tts = "I've collected {} participants.".format(n_participants)
        else:
            tts = "I haven't finished collecting the participants."
    except:
        tts = "I have not gathered any participants."
    hermes.publish_end_session(session_id, tts)


def get_winner(hermes, intent_message):
    session_id = intent_message.session_id

    try:
        if tweet_lottery[tweet_id].done:
            participants = tweet_lottery[tweet_id].participants
            n_participants = len(participants)
            if n_participants > 0:
                tts = "The winner is {}.".format(random.choice(participants))
                hermes.publish_continue_session(session_id, tts, [INTENT_KEEP, INTENT_DELETE])
            else:
                tts = "There are no participants! Looks like no one wants a maker kit."
                hermes.publish_end_session(session_id, tts)
        else:
            tts = "Sorry I am still collecting the participants."
            hermes.publish_end_session(session_id, tts)
    except:
        tts = "I do not have any gathered names."
        hermes.publish_end_session(session_id, tts)


with Hermes(MQTT_ADDR) as h:
    h.subscribe_intent(INTENT_DELETE, delete_names) \
     .subscribe_intent(INTENT_KEEP, keep_names) \
     .subscribe_intent(INTENT_HOW_MANY, how_many) \
     .subscribe_intent(INTENT_COLLECT, collect_names) \
     .subscribe_intent(INTENT_WINNER, get_winner).start()

