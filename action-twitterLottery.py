#!/usr/bin/env python2
from hermes_python.hermes import Hermes

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

# intents
INTENT_START = "bezzam:start_game"
INTENT_WINNER = "bezzam:winner"
INTENT_STOP = "bezzam:stop_game"

# dict to store participants
participants = dict()


def user_start_game(hermes, intent_message):
    session_id = intent_message.session_id
    tts = "Starting game."
    hermes.publish_end_session(session_id, tts)


def user_stop_game(hermes, intent_message):
    session_id = intent_message.session_id
    tts = "Stopping game."
    hermes.publish_end_session(session_id, tts)


def get_winner(hermes, intent_message):
    session_id = intent_message.session_id
    tts = "The winner is Eric."
    hermes.publish_end_session(session_id, tts)


with Hermes(MQTT_ADDR) as h:
    h.subscribe_intent(INTENT_START, user_start_game) \
     .subscribe_intent(INTENT_STOP, user_stop_game) \
     .subscribe_intent(INTENT_WINNER, get_winner).start()
