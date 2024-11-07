# Gamefinder discord bot

This bot scrapes Roblox game pages for specific keywords, collects information about games and posts relevant data (e.g, game link, owner, visit count and discord link) to a Discord server.

## Installation
1. Go to the [Discord for Dev](discord.com/developers) website and register application via `New Application` button. Then go to the `OAuth2` and scroll down to the `OAuth2 URL Generator`, then click on `bot` checkbox, scroll down to the `Bot Permissions` and click on `Administrator` checkbox. Scroll down to the `Generated URL` and copy&paste link in your browser. This will open separate tab and ask about bot server adding (select preffered).
2. Install Python 3.10.1 (make sure that [this](https://www.python.org/downloads/release/python-3101/) version was installed).
3. Open console and locate your project with `cd` command (for instance: `cd yourproject/folder`) and paste this command there: `pip3 install -r requirements.txt`.
4. Open `app -> constants -> config.ini` and configure settings (change command prefix, required admin role, delay).
5. Now you need to set TOKEN for your bot. To do so, go to the [Discord for Dev](discord.com/developers) and go to the `your_bot_name -> Bot -> Find Token section and reset the current token -> Copy new token -> Paste it in TOKEN variable`.
6. Open `app -> constants -> keywords.txt` and configure your game keywords.
7. In the console type: `python main.py` and hit Enter. You're all set!

## Commands Overview
('!' will be used as default command prefix)

- `!games` - starts scraping process.
- `!stop` - stops current scraping process.

## Config File Overview
- In the `Roblox` section config file stores username and password in case if you want to login in scraping account.
- In the `Bot` section of the config file, other important bot variables are stored (token, prefix, admin role, delay. For the delay I'd recommend to leave 5 sec as minimum value).

## Other Files Overview
- `cookie.json` - stores scraper account cookie.
- `processed_games.json` - stores scraped game IDs.
- `keywords.txt` - contains keywords that used for the scraping process.
- `utils` - folder contains all the necessary utilities for scraping and keyword reading.
- `main.py` - the main file that contains all discord bot commands, functions (in other words, it's a heart of the bot).

## Usage Notes
- As I mentioned before, it's recommended to leave at least 5 second delay, because discord may raise a warning that could cause the bot to reconnect in the future.
- I would also recommend waiting some time before the next game scraping, because at the end of the scraping process the bot will close all open Chrome tabs that were used in the scraping process. It was implemented to reduce CPU load.
- I would also recommend (but it's optional) to clear processed games from time to time when you're done with the specific keyword.