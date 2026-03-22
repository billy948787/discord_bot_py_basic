import os

import dotenv
from google import genai

import discord_bot
import turtle_soup

if __name__ == "__main__":
    dotenv.load_dotenv()

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    genai_client = genai.Client(api_key=GOOGLE_API_KEY)
    turtle_session_manager = turtle_soup.TurtleSessionManager(genai_client)

    discod_bot = discord_bot.DiscordBot(turtle_session_manager)

    discod_bot.run()
