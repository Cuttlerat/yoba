# PyBot

This is my first telegram bot written in Python

## Commands

```
/bug                - Link to create issue on github
/db <SQL query>     - Manage your database (Only for admins)
/info               - Information about this bot
/ping               - Show usage of pinger command wich allow to
                    + add ping phrases for user who call this command
/w <City>           - Short form of /w
/weather <City>     - Weather in a city for now, today and tommorow
/wset <City>        - Set default city for /weather
/crypt              - Crypto-currency exchange rate
```

## Starting

```bash
git clone https://github.com/Cuttlerat/pybot.git
cd pybot
```

Add your telegram username, tokens, and database path into `./bot/config.yaml` file
```yaml
tokens:
  tg_token: YOUR_TOKEN
  weather_token: YOUR_TOKEN
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
docker-compose up --build pybot
```

You can get a weather token here: http://openweathermap.org/ <br>
Register your bot here: https://t.me/BotFather

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

And is it! Enjoy your bot!

### Ping

This section still in progress