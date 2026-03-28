"""Remplacement natif de emergentintegrations.llm.chat"""
import os
from openai import AsyncOpenAI
from dataclasses import dataclass


@dataclass
class UserMessage:
    text: str


class LlmChat:
    def __init__(self, api_key: str = None, session_id: str = "", system_message: str = ""):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.session_id = session_id
        self.system_message = system_message
        self.model = "gpt-4o-mini"
        self.provider = "openai"

    def with_model(self, provider: str, model: str):
        self.provider = provider
        self.model = model
        return self

    async def send_message(self, message: UserMessage) -> str:
        client = AsyncOpenAI(api_key=self.api_key)
        messages = []
        if self.system_message:
            messages.append({"role": "system", "content": self.system_message})
        messages.append({"role": "user", "content": message.text})
        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
