import asyncio
import random

from google import genai
from google.api_core import exceptions as google_exceptions
from google.genai import types

import bot_config
import soup_data

accepted_responses = ["是", "否", "不相關", "問題無效"]


async def send_async_with_retry(client: genai.Client, **kwargs):
    while True:
        try:
            return await client.aio.models.generate_content(**kwargs)
        except google_exceptions.ResourceExhausted:
            print("Rate limit exceeded, retrying in 1 seconds...")
            await asyncio.sleep(1)


class TurtleSessionManager:
    def __init__(self, genai_client: genai.Client) -> None:
        self._genai_client = genai_client
        self._sessions: dict[int, TurtleGame] = {}

    async def start_session(self, channel_id: int) -> str:
        soup = random.choice(soup_data.soups)

        print(f"Selected soup surface: {soup.surface}")
        print(f"Selected soup bottom: {soup.bottom}")

        self._sessions[channel_id] = TurtleGame(
            soup.surface, soup.bottom, self._genai_client
        )

        return soup.surface

    def end_session(self, channel_id: int) -> None:
        if channel_id in self._sessions:
            del self._sessions[channel_id]

    async def handle_question(self, channel_id: int, question: str) -> str | None:
        game = self._sessions.get(channel_id)
        if game is None:
            return None
        return await game.get_response_to_question(question)


class TurtleGame:
    def __init__(self, surface: str, bottom: str, genai_client: genai.Client) -> None:
        self._surface = surface
        self._bottom = bottom
        self._genai_client = genai_client

    async def get_response_to_question(self, question: str) -> str | None:
        system_prompt = gen_system_prompt(self._surface, self._bottom)

        response = await send_async_with_retry(
            self._genai_client,
            model=bot_config.model,
            contents=question,
            config=types.GenerateContentConfig(system_instruction=system_prompt),
        )
        result = response.text

        if result not in accepted_responses:
            print(f"Invalid response from Gemini: {result}")
            return "問題無效"

        # ask another ai to check if the response is actually answer

        return result


def gen_system_prompt(surface: str, bottom: str) -> str:
    return f"""你是海龜湯遊戲的主持人。
    湯面：{surface}
    湯底：{bottom}

    玩家會提問，你只能回答以下其中一種，不能有其他文字：
    是
    否
    不相關
    問題無效"""
