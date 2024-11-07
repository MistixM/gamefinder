# Get keyword reader module from the utils folder
from .get_keywords import read_keyword_file

# Import drissionpage modules for scraping
from DrissionPage import ChromiumPage
from DrissionPage import ChromiumOptions
from DrissionPage.common import Settings

# Import other important libraries
import os
import json
# import requests
import aiohttp
import asyncio


scraping = False

Settings.raise_when_ele_not_found = True
Settings.raise_when_click_failed = True

async def find_games(ctx, delay) -> None:

    # Get all games with specified keyword
    url = f"https://www.roblox.com/discover/?Keyword={read_keyword_file()}"

    # In case if we want to hide Chrome

    options = ChromiumOptions()
    # options.set_argument("--headless")  # Hide browser
    options.set_argument("--disable-blink-features=AutomationControlled")
    options.set_argument("--disable-gpu")
    options.set_argument("--disable-dev-shm-usage")
    options.set_argument("--disable-infobars")
    options.set_argument("--window-size=1920,1080")
    options.set_argument("--disable-features=IsolateOrigins,site-per-process")
    options.set_argument("--disable-extensions")
    options.set_argument("--remote-debugging-port=9223")

    # options.headless(True)

    # Correct way to set user-agent
    options.set_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36')

    # Initialize the browser
    driver = ChromiumPage(options)

    driver.get(url)

    # Get current directory
    current_dir = os.path.dirname(__file__)

    # Get cookie file for roblox account registration
    path = os.path.join(current_dir, '..', 'constans', 'cookie.json')
    with open(path, 'r') as file:
        cookies = json.load(file)
        
        # DO NOT DELETE OR CHANGE THIS BLOCK OF CODE
        # Otherwise cookies won't work properly
        for cookie in cookies:
            if cookie.get('sameSite') not in ['None', 'Lax', 'Strict']:
                cookie['sameSite'] = 'Lax'

            driver.set.cookies(cookie)

    # When cookies set wait some time and refresh the page
    await asyncio.sleep(1)

    driver.refresh()
    
    await asyncio.sleep(2)

    driver.run_js("window.scrollBy(0, 2000);")

    # Get the file with the processed games
    processed_games_file = os.path.join(current_dir, '..', 'constans', 'processed_games.json')

    # Then check if it's exists
    if os.path.exists(processed_games_file):
        
        # And try to open json file and write down the ids
        try:
            with open(processed_games_file, 'r') as file:
                processed_games = json.load(file)

                # Handle the case where the file is empty
                if not isinstance(processed_games, list):
                    processed_games = []
        
        # Catch an error if the file is empty
        except json.JSONDecodeError:
            processed_games = []
    
    # If it's not exists, just create an empty list
    else:
        processed_games = []
    
    async with aiohttp.ClientSession() as session:
        while get_scraper_flag():
            global scraping
        
            driver.run_js("window.scrollBy(0, 1000)")
            await asyncio.sleep(3)
            
            # Get all game cards
            game_containers = driver.eles(".grid-item-container game-card-container")
            
            # Initialise the list with the new games
            new_games = []


            # Start get each game in the container
            for game in game_containers:   
                print("Scanning game")
                # driver.run_js("window.scrollBy(0, 600);")

                if not get_scraper_flag():
                    driver.close()
                    print("Driver closed")
                    return
            
                # Required to get link and its ID first
                game_link = game.ele(".game-card-link").attr('href')
                game_id = game_link.split('/games/')[1].split('/')[0]

                # If game ID already exist in JSON file, move on the next iteration
                if game_id in processed_games:
                    print('Game ID already exists')
                    continue
                
                # Cookie for the request
                cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}

                # Player count, owner's name, visit count, discord link and other important statistic goes here
                try:
                    playing_count = game.ele(".info-label playing-counts-label").text
                    game_info_tab = driver.new_tab(game_link)
                    game_universe_id = await get_async_response(session, f"https://games.roblox.com/v1/games/multiget-place-details?placeIds={game_id}", cookie_dict)
                    
                    game_owner_request = await get_async_response(session, f"https://games.roblox.com/v1/games?universeIds={game_universe_id[0]['universeId']}", cookie_dict)
                    game_owner_info = game_owner_request['data'][0]['creator']
                    
                    if game_owner_info['type'] == "Group":
                        game_owner_id_request = await get_async_response(session, f"https://groups.roblox.com/v1/groups/{game_owner_info['id']}", cookie_dict)
                        game_owner = game_owner_id_request['owner']['username']
                    else:
                        game_owner = game_owner_info['name']

                    # game_owner = game_info_tab.ele(".text-name text-overflow").text
                    game_visits = game_info_tab.eles(".text-lead font-caption-body")[2].text
                except Exception as e:
                    print(f"Error while getting game info: {e}")
                    continue


                # Send API request to the roblox servers with the user's cookie
                game_universe_visits = await get_async_response(session, f"https://games.roblox.com/v1/games?universeIds={game_universe_id[0]['universeId']}", cookie_dict)

                # Get visits index and check if it's greater than N number
                if game_universe_visits['data'][0]['visits'] > 100_000_000:
                    print('Game has more than 100,000,000 visits')
                    # if it's not, just append the game ID to the processed list
                    new_games.append(game_id)
                    game_info_tab.close()
                    continue
                    
                discord_link = None

                # Check if social exist
                try:   
                    # Get all possible socials
                    socials = game_info_tab.ele('.game-social-links').children()

                    # Check every social and open it in the new tab (cuz link probably hidden)
                    for social in socials:
                        social.click()
                        tab = driver.get_tab()

                        # If discord link found, break the loop and save the link
                        if "discord" in tab.url:
                            discord_link = tab.url
                            tab.close()
                            break
                        else:
                            tab.close()

                # If don't found any socials there, just close the game tab and move on the next iteration (also move this ID to json, so it won't load bot)
                except Exception:
                    print("No socials found")
                    new_games.append(game_id)
                    game_info_tab.close()
                    continue
                
                # If found discord link, let's pack it into the discord message with all the previous informations
                if discord_link:
                    await ctx.send(
                        f"> **Game Link**: {game_link[:100]}\n"
                        f"> **Owner**: {game_owner}\n"
                        f"> **Players**: {playing_count}\n"
                        f"> **Visits**: {game_visits}\n"
                        f"> **Discord Link**: {discord_link}\n"
                    )

                    # And append the new ID to the list
                    new_games.append(game_id)

                # in case if discord link was not found
                else:
                    # If discord link doesn't exist, just put ID to the black list
                    new_games.append(game_id)

                # Create a variable with the processed games
                processed_games = list(set(processed_games + new_games))

                # Open a JSON file and write a new ID there to prevent duplicating next time
                with open(processed_games_file, "w") as file:
                    json.dump(processed_games, file, indent=4)

                # Close the game tab
                game_info_tab.close()

                # Wait some time before the next iteration to prevent overwhelming the server
                await asyncio.sleep(int(delay))

            print("Scraping finished")
            set_scraper_flag(False)
            driver.close()

async def get_async_response(session, url, cookies):
    async with session.get(url, cookies=cookies) as response:
        return await response.json()


def set_scraper_flag(state):
    global scraping
    scraping = state

def get_scraper_flag():
    global scraping
    return scraping