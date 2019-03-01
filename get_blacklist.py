import ConfigParser
import tweepy
import io

BLACKLIST = []

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

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

if __name__ == "__main__":

	config = read_configuration_file(CONFIG_INI)

	# authenticate and connect
	auth = tweepy.OAuthHandler(config["secret"]["consumer_key"], config["secret"]["consumer_secret"])
	auth.set_access_token(config["secret"]["access_token"], config["secret"]["access_token_secret"])
	api = tweepy.API(auth)

	twitter_handle = config["secret"]["twitter_handle"]
	tweet_id = config["secret"]["tweet_id"]

	# get people who retweeted
	results = api.retweets(tweet_id, count=100)
	rt_screen_names = [r.user.screen_name for r in results]

	# check which ones are followers
	for sn in rt_screen_names:
		fship = api.show_friendship(
			source_screen_name=twitter_handle,
			target_screen_name=sn
		)
		if fship[0].followed_by:
		    BLACKLIST.append(str(sn))

	print(len(BLACKLIST))
	print(BLACKLIST)
