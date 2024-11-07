# Import dependencies
import discord
import configparser
import asyncio

# Get discord commands module
from discord.ext import commands

# Get scraper
from app.utils.scraper import (find_games, 
                               set_scraper_flag, 
                               get_scraper_flag)

def main():
    # Read the config file
    config = configparser.ConfigParser()
    config.read("app/constans/config.ini")

    # Bot setup
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=config['BOT']['PREFIX'], intents=intents)

    @bot.command(name="stop")
    @commands.has_role(config['BOT']['ADMIN_ROLE']) # Check if user has required role for it
    async def stop_cmd(ctx):
        await ctx.message.delete()

        if get_scraper_flag():
            set_scraper_flag(False)
            msg = await ctx.send(f"{ctx.author.mention} Scraper stopped!")
            await asyncio.sleep(3)
            await msg.delete()
        else:
            msg = await ctx.send(f"{ctx.author.mention} Scraper is not running!")
            await asyncio.sleep(3)
            await msg.delete()

    # !games command setting
    @bot.command(name='games') 
    @commands.has_role(config['BOT']['ADMIN_ROLE']) # Check if user has required role for it
    async def fing_games_cmd(ctx):

        # Delete called command
        await ctx.message.delete()

        if not get_scraper_flag():
            set_scraper_flag(True)

            msg = await ctx.send(f"{ctx.author.mention} Scraper started")
            await asyncio.sleep(3)
            await msg.delete()
            
            # Start scraper
            await find_games(ctx, config['BOT']['DELAY'])

        else:
            await ctx.send("Scraper is already running!")
            await asyncio.sleep(3)
            await ctx.message.delete()

    # On ready event (check all necessary info here before bot start)
    @bot.event
    async def on_ready():
        print(f"Bot started as {bot.user.name}")

    # Command error handler
    @bot.event
    async def on_command_error(ctx, err):
        # Delete the message immediately
        try:
            await ctx.message.delete()
        
        # If bot catch unknown error (such us 404) just print and pass it
        except Exception as e:
            print(f"An unknown error occurred: {e}")
            pass
        
        # If bot catch missing role error, show error message and delete the message
        if isinstance(err, commands.MissingRole):
            msg = await ctx.send(f"{ctx.author.mention} You don't have the required permissions..", ephemeral=True)
            await asyncio.sleep(3)
            await msg.delete()

        # If bot catch command error in the server, show an error message and delete message as well
        elif isinstance(err, commands.CommandError):
            print(err)

            msg = await ctx.send(f"{ctx.author.mention} Can't find such command..", ephemeral=True)
            await asyncio.sleep(3)
            await msg.delete()

        # Otherwise it's unexpected error for the bot and will be shown in the console
        else:
            print(f"An unexpected error occurred: {err}. Please try again")
    
    # Finally run the bot with TOKEN from the config file
    bot.run(config['BOT']['TOKEN'], reconnect=True)

if __name__ == '__main__':
    main()
