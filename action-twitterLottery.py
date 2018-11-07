#!/usr/bin/env python2
from hermes_python.hermes import Hermes
import random
import tweepy
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
participants = []

def user_start_game(hermes, intent_message):
    session_id = intent_message.session_id
    tts = "Starting game."
    hermes.publish_end_session(session_id, tts)


def user_stop_game(hermes, intent_message):
    session_id = intent_message.session_id

    # get people who retweeted
    results = api.retweets(tweet_id, count=100)
    screen_names = [r.user.screen_name for r in results]

    # check which ones are followers
    _part = []
    for sn in screen_names:
        fship = api.show_friendship(source_screen_name=twitter_handle,
                                    target_screen_name=sn)
        if fship[0].followed_by:
            _part.append(str(sn))

    try:
        participants = _part
        tts = "Stopping game. I've collected {} participants.".format(len(_part))
    except:
        tts = "Please ask to start the game first!"

    hermes.publish_end_session(session_id, tts)


def get_winner(hermes, intent_message):
    session_id = intent_message.session_id
    tts = "The winner is {}.".format(random.choice(participants))
    hermes.publish_end_session(session_id, tts)


with Hermes(MQTT_ADDR) as h:
    h.subscribe_intent(INTENT_START, user_start_game) \
     .subscribe_intent(INTENT_STOP, user_stop_game) \
     .subscribe_intent(INTENT_WINNER, get_winner).start()
