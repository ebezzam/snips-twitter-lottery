# Twitter Lottery with a Voice Assistant!

Select a winner randomly from RT'ers (of a specified tweet) that are also followers (or a specified account).
When deploying the assistant with SAM, you will be asked to specify the following "end-user" parameters:
- Twitter handle, which participants in the lottery should follow.
- Tweet ID, which participants should RT. This can be obtained by clicking on the desired tweet from Twitter and taking the integer sequence at the end of the url, e.g. `1060462680597848064` for [this tweet](https://twitter.com/snips/status/1060462680597848064).
- Access token.
- Access token secret.
- Consumer key.
- Consumer secret.

The last four parameters are unique for each Twitter developer/user. 
You can obtain your own by creating a Twitter developer [here](https://developer.twitter.com) and then making an App.
After making an App, you should find a tab called "Keys and tokens" where you can obtain your unique tokens and keys.
Under "Step 1" of [this article](http://adilmoujahid.com/posts/2014/07/twitter-analytics/), you can see more info about getting Twitter API keys.

You can find this Twitter Lottery App on the Console riiiight over [here](https://console.snips.ai/store/en/skill_g7pX7N2oM87). It was used to give away two free [Maker Kits](https://makers.snips.ai/kit/) at [this event](https://www.hardwarepioneers.com/2018-events/l-the-impact-of-ai-and-ml-on-iot).
