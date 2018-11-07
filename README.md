# snips-twitter-lottery
Randomly chose a winner based on Twitter activity.

Setup
1. http://adilmoujahid.com/posts/2014/07/twitter-analytics/
    - make Twitter account, create app, get credentials
    
    
Manually adding action code (inspired from https://snips.gitbook.io/documentation/console/deploying-your-skills#code-snippets-and-github-repository)
1. Clone this repo on the board to: /var/lib/snips/skills
2. cd snips-twitter-lottery/
3. Make action and setup file executable: chmod +x <file>
4. Create virtual environment for action
5. Restart skills server: $ sudo systemctl restart snips-skill-server

