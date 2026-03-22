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
            if self._session_manager.check_session(interaction.channel_id):
                await interaction.response.send_message("目前已經有正在進行的遊戲了！")
                surface = self._session_manager.get_session_surface(
                    interaction.channel_id
                )
                if surface:
                    await interaction.followup.send(f"目前的湯面是：{surface}")

                return

            await interaction.response.defer()
            surface = await self._session_manager.start_session(interaction.channel_id)
            await interaction.followup.send(f"遊戲開始！\n湯面：{surface}")

        @self._tree.command(name="turtle_end", description="End the turtle soup game")
        async def turtle_end(interaction: discord.Interaction):
            self._session_manager.end_session(interaction.channel_id)
            await interaction.response.send_message("遊戲結束！")

        @self._tree.command(
            name="turtle_status",
            description="Check if there's an ongoing turtle soup game",
        )
        async def turtle_status(interaction: discord.Interaction):
            if self._session_manager.check_session(interaction.channel_id):
                await interaction.response.send_message("目前有正在進行的遊戲！")
            else:
                await interaction.response.send_message("目前沒有正在進行的遊戲！")

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
