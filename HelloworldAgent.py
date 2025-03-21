import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from dotenv import load_dotenv
import os

load_dotenv()
# get api key from env 
api_key = os.getenv("GEMINI_KEY")

# this is a small sample program to understand the basic function of autogen 
async def main() -> None:
    model_client = OpenAIChatCompletionClient(
        model="gemini-1.5-flash-8b",
        api_key = api_key
          )
    agent = AssistantAgent("assistant", model_client=model_client)
    print(await agent.run(task="what is an ant-eater!'"))
    await model_client.close()

asyncio.run(main()) 