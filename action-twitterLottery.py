#!/usr/bin/env python2
import ConfigParser
from hermes_python.hermes import Hermes
import random
import tweepy
import threading
import io
import sys

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

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

RT_COUNT = 100      # max is 100

# remove some participants from contention
pre_event = []

# store participants
tweet_lottery = dict()

tts_not_gathered = ["Sorry I haven't gathered any participant names.",
                    "I don't have any names.",
                    "Sorry I don't have any usernames.",
                    "Sorry I don't have any gathered names."]


class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section: {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()


class ExtractRetweetThread(threading.Thread):

    def __init__(self, api, handle, tweet, rt_count):
        super(ExtractRetweetThread, self).__init__()
        self.api = api
        self.handle = handle
        self.tweet = tweet
        self.rt_count = rt_count
        self.rt_screen_names = None
        self.participants = []
        self.done = False

    def run(self):

        # get people who retweeted
        results = self.api.retweets(self.tweet, count=self.rt_count)
        self.rt_screen_names = [r.user.screen_name for r in results]
        
        # check which ones are followers
        for sn in self.rt_screen_names:
            if sn not in pre_event:
                fship = self.api.show_friendship(source_screen_name=self.handle,
                                                 target_screen_name=sn)
                if fship[0].followed_by:
                    self.participants.append(str(sn))
        self.done = True


def delete_names(hermes, intent_message):
    session_id = intent_message.session_id
    try:
        del tweet_lottery[hermes.tweet_id]
        tts = "Sure thing, I'm deleting the gathered usernames."
    except:
        tts = "There are no usernames to delete."
        pass
    hermes.publish_end_session(session_id, tts)


def keep_names(hermes, intent_message):
    session_id = intent_message.session_id
    try:
        participants = tweet_lottery[hermes.tweet_id].participants
        tts = "Sure thing."
    except:
        tts = random.choice(tts_not_gathered)
    hermes.publish_end_session(session_id, tts)


def collect_names(hermes, intent_message):
    session_id = intent_message.session_id
    
    tweet_lottery[hermes.tweet_id] = ExtractRetweetThread(hermes.api, hermes.twitter_handle, hermes.tweet_id, RT_COUNT)
    tweet_lottery[hermes.tweet_id].start()
    tts = "I've started collecting the usernames. This may take a couple minutes."
    hermes.publish_end_session(session_id, tts)


def how_many(hermes, intent_message):
    session_id = intent_message.session_id

    try:
        if tweet_lottery[hermes.tweet_id].done:
            participants = tweet_lottery[hermes.tweet_id].participants
            n_participants = len(participants)
            if n_participants > 1:
                tts = "I've got {} participants. Would you like to know the winner?".format(n_participants)
                hermes.publish_continue_session(session_id, tts, [INTENT_WINNER, INTENT_NOT_YET])
            elif n_participants == 1:
                tts = "I've only got 1 participant. The winner is {}.".format(participants[0])
                hermes.publish_end_session(session_id, tts)
            else:
                tts = "There are no participants! Looks like no one wants to win."
                hermes.publish_end_session(session_id, tts)
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
        if tweet_lottery[hermes.tweet_id].done:
            participants = tweet_lottery[hermes.tweet_id].participants
            n_participants = len(participants)
            if n_participants > 0:
                winner = random.choice(participants)
                tts = "The winner is {}.".format(winner)
                tweet_lottery[hermes.tweet_id].participants.remove(winner)
                hermes.publish_end_session(session_id, tts)

            else:
                tts = "There are no participants! Looks like no one wants a maker kit."
                hermes.publish_end_session(session_id, tts)
        else:
            tts = "Sorry I'm still collecting the participants."
            hermes.publish_end_session(session_id, tts)
    except:
        tts = random.choice(tts_not_gathered)
        hermes.publish_end_session(session_id, tts)


if __name__ == "__main__":

    config = read_configuration_file(CONFIG_INI)

    # authenticate and connect
    auth = tweepy.OAuthHandler(config["secret"]["consumer_key"], config["secret"]["consumer_secret"])
    auth.set_access_token(config["secret"]["access_token"], config["secret"]["access_token_secret"])
    api = tweepy.API(auth)

    with Hermes(MQTT_ADDR) as h:
        h.api = api
        h.twitter_handle = config["secret"]["twitter_handle"]
        h.tweet_id = config["secret"]["tweet_id"]
        h.subscribe_intent(INTENT_DELETE, delete_names) \
         .subscribe_intent(INTENT_KEEP, keep_names) \
         .subscribe_intent(INTENT_NOT_YET, not_yet) \
         .subscribe_intent(INTENT_HOW_MANY, how_many) \
         .subscribe_intent(INTENT_COLLECT, collect_names) \
         .subscribe_intent(INTENT_WINNER, get_winner).start()

