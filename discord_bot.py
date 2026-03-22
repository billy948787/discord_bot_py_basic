import os

import discord
import discord.app_commands
import dotenv

dotenv.load_dotenv()


class DiscordBot:
    def __init__(self, session_manager) -> None:
        self._session_manager = session_manager
        intent = discord.Intents.default()
        intent.message_content = True
        self._client = discord.Client(intents=intent)
        self._tree = discord.app_commands.CommandTree(self._client)
        self._register_handlers()

    def _register_handlers(self):
        @self._tree.command(name="turtle_start", description="Start a turtle soup game")
        async def turtle_start(interaction: discord.Interaction):
            await interaction.response.defer()
            surface = await self._session_manager.start_session(interaction.channel_id)
            await interaction.followup.send(f"遊戲開始！\n湯面：{surface}")

        @self._client.event
        async def on_ready():
            await self._tree.sync()
            print(f"We have logged in as {self._client.user}")

        @self._client.event
        async def on_message(message):
            if message.author == self._client.user:
                return

            response = await self._session_manager.handle_question(
                message.channel.id, message.content
            )
            if response:
                await message.channel.send(response)

    def run(self):
        DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
        if DISCORD_BOT_TOKEN is None:
            raise ValueError("DISCORD_BOT_TOKEN environment variable not set")
        self._client.run(DISCORD_BOT_TOKEN)
