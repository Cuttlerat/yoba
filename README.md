# YOBA

Yet One Bot Assistant - just a funny telegeram bot.

## Commands

```
/bug                    - Link to create issue on github
/db <SQL query>         - Manage your database (Only for admins)
/info                   - Information about this bot
/ping_add [matches]     - Add casts for user, for admins allows to use 
                        + /ping_add @username1 @username2 match1 match2
/ping_add_me            - Add casts for user which can be randomly chosen in /me
/ping_show              - Show all casts for user
/ping_show_all          - Show all casts in DB for this chat (only for admins)
/ping_delete [matches]  - Delete matches for user, for admins the same usage as in /ping_add
/ping_delete_me         - Delete matches for user which can be used in /me
/ping_drop <Username>   - Delete all matches for user (only for admins)
/me [message]           - Deletes source message and send message like this
                        + <Random cast for user which was added by /ping_add_me> [message]
/w <City>               - Short form of /w
/weather <City>         - Weather in a city for now, today and tommorow
/wset <City>            - Set default city for /weather
/crypto                 - Crypto-currency exchange rate
/mute_on                - Turn on auto ban (readonly) for all messages for 5 minutes (except admins)
/mute_off               - Turn off auto ban
/clash                  - Create CoC competition (https://condingame.com)
/clash_start            - Start CoC competition
/clash_enable           - Enable CoC notifications
/clash_disable          - Disable CoC notifications
```

## Starting

```bash
git clone https://github.com/Cuttlerat/pybot.git
cd pybot
```

Add your telegram username, tokens, and database path into `./bot/config/config.yaml` file
```yaml
tokens:
  tg_token: YOUR_TOKEN       # Register your bot here: https://t.me/BotFather
  weather_token: YOUR_TOKEN  # You can get a weather token here: http://openweathermap.org/
  clash_remcg: COOKIE        # You can take it from https://codingame.com cookies
  clash_remember_me: COOKIE  # You can take it from https://codingame.com cookies
  clash_cg_session: COOKIE   # You can take it from https://codingame.com cookies
  clash_secret: SECRET       # You can take it from https://codingame.com requests
telegram:
  mode: Polling # or Webhook
  webhook_port: 30222
  webhook_url: https://example.com/{}
  # Use this if you want to run with webhook not in docker
  listen_ip: 0.0.0.0 # Your IP
database:
  host: data/pybot.db
admins:
  - Username1
  - Username2
```

Then just launch the bot

```bash
./bot/main.py
```

### Starting into a docker container

In order to build and create a docker container, `docker-compose` must be installed in your system

```bash
docker-compose up --build
```


## How to manage database

If you want that your bot triggers on a some type of messages, there some options here.

### Simple trigger

If you want a simple trigger on a message responding with your specified string

```sql
/db INSERT INTO answers(match,string) VALUES("hello!", "Hi!")
Cuttlerat: Hello!
Cutltebot: Hi!
```

### Ping
#### Add it into database

You also can use the `/ping` command for this, and so all the others (besides the administrator) can use this to add trigers but not more than 10

If you want to summon someone with just mentioning of his name or nickname

```sql
/db INSERT INTO pingers(username,match) VALUES("Cuttlerat", "rat")
Cuttlerat: rat!
*nothing*
```

Why? Because we didn't set a ping phrase yet

```sql
/db INSERT INTO ping_phrases(phrase) VALUES("ping")
Cuttlerat: ping rat
Cuttlebot: @Cuttlerat
```

There is a little trick to summon all persons from the pingers table

```sql
/db INSERT INTO pingers(username,match) VALUES("hotkosc", "kosc")
/db INSERT INTO pingers(username,match) VALUES("EVERYONE GET IN HERE", "all")
Cuttlerat: ping all
Cuttlebot: @Cuttlerat @hotkosc
```

But what if you want to call everyone except one guy?

You will need to add a ping exclude phrase

```sql
/db INSERT INTO ping_exclude(match) VALUES("except")
Cuttlerat: ping all except kosc
Cuttlebot: @Cuttlerat
```

#### Add with /ping_* commands

`/ping` command is deprecated!  
Use `/ping_add`, `/ping_show`, `/ping_show_all` and `/ping_delete` instead  

This commands setting notifications for users.  
When you will send a message with a match which in `ping_phrases` table and with match of user, bot will reply on your message with `@username` in his reply and that user will get a notification even if he disabled them

Example:
```
> Ping CuttleRat
< @CuttleRat
```

Ping command is different for admins and common users


##### Admin

```
Usage: 
/ping_add [@username] [match] - Add a ping for @username with match
/ping_show [@username] - Show all matches of this user in this chat
/ping_show_all - Show all mathces for all users in this chat
/ping_delete [@username] [match] - Delete a match for this user if it exists
/ping_drop [@username]` - Delete all matches for this user if it exists
```

For add and delete commands you also can use multiple usernames at once, example:  
```
/ping_add @user_1 @user_2 @user_3 match
/ping_delete @user_1 @user_2 @user_3 match
/ping_drop @user_1 @user_2 @user_3
```

##### Common user

```
Usage: 
/ping_add [match] - Add a match for you. You can have only 10 matches, or more if an administrator will add it for you  
/ping_show [@username] - Show all matches for @user_1  
/ping_delete [match] - Delete a match  
```

## Clash of code

These commands will help you to create a new Clash of Code game and not miss any games created by someone else.

### Create a new game

```
/clash

Cuttlebot:

Clash of Code!

https://www.codingame.com/clashofcode/clash/GAME_ID

@User1 @User2 @User3

Please send /clash_disable if you don't want to receive these notifications
```

### Disable and enable notifications

```
/clash_disable

Cutlebot:

Now you won't receive any notifications about Clash of Code games
```

```
/clash_enable

Cutlebot:

You will be notified when a new game is created!
```

### Manually start the last game

```
/clash_start

Cuttlebot:

The game is about to start, hurry up!

@User1 @User2 @User3
```

**Enjoy your bot!**

