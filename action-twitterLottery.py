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
INTENT_NOT_YET = "bezzam:not_yet"

# target handle and tweet
twitter_handle = "snips"
tweet_id = 1060462680597848064  # Trump tweet to test large number of RT
rt_count = 100

tts_not_gathered = ["Sorry I haven't gathered any participant names.",
                    "I don't have any names.",
                    "Sorry I don't have any usernames.",
                    "Sorry I don't have any gathered names."]

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
        tts = "Sure thing, I'm deleting the gathered usernames."
    except:
        tts = "There are no usernames to delete."
        pass
    hermes.publish_end_session(session_id, tts)


def keep_names(hermes, intent_message):
    session_id = intent_message.session_id
    try:
        participants = tweet_lottery[tweet_id].participants
        tts = "Sure thing."
    except:
        tts = random.choice(tts_not_gathered)
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
            tts = "I've got {} participants. Would you like to know the winner?".format(n_participants)
            hermes.publish_continue_session(session_id, tts, [INTENT_WINNER, INTENT_NOT_YET])
        else:
            tts = "Sorry, I haven't finished collecting the participants."
            hermes.publish_end_session(session_id, tts)
    except:
        tts = random.choice(tts_not_gathered)
        hermes.publish_end_session(session_id, tts)


def not_yet(hermes, intent_message):
    session_id = intent_message.session_id
    tts = "Alright, just let me know when you would like to know."
    hermes.publish_end_session(session_id, tts)


def get_winner(hermes, intent_message):
    session_id = intent_message.session_id

    try:
        if tweet_lottery[tweet_id].done:
            participants = tweet_lottery[tweet_id].participants
            n_participants = len(participants)
            if n_participants > 0:
                winner = random.choice(participants)
                tts = "The winner is {}.".format(winner)
                tweet_lottery[tweet_id].participants.remove(winner)
                hermes.publish_end_session(session_id, tts)

                # tts = "The winner is {}. Would you like to delete the names?".format(random.choice(participants))
                # hermes.publish_continue_session(session_id, tts, [INTENT_KEEP, INTENT_DELETE])

            else:
                tts = "There are no participants! Looks like no one wants a maker kit."
                hermes.publish_end_session(session_id, tts)
        else:
            tts = "Sorry I'm still collecting the participants."
            hermes.publish_end_session(session_id, tts)
    except:
        tts = random.choice(tts_not_gathered)
        hermes.publish_end_session(session_id, tts)


with Hermes(MQTT_ADDR) as h:
    h.subscribe_intent(INTENT_DELETE, delete_names) \
     .subscribe_intent(INTENT_KEEP, keep_names) \
     .subscribe_intent(INTENT_NOT_YET, not_yet) \
     .subscribe_intent(INTENT_HOW_MANY, how_many) \
     .subscribe_intent(INTENT_COLLECT, collect_names) \
     .subscribe_intent(INTENT_WINNER, get_winner).start()

