import asyncio
from autogen_agentchat.agents import AssistantAgent
from dotenv import load_dotenv
import os
from autogen_ext.models.openai import OpenAIChatCompletionClient

class webagent:

    @classmethod
    def DesiredConfigs(cls):
        load_dotenv()
        api_key = os.getenv("GEMINI_KEY")
        model="gemini-1.5-flash-8b"
        return api_key,model
           

    #here iam defining the web search agent
    async def main(self) -> None:
        # get the model and apikey from above function
        api_key, model = self.DesiredConfigs()
        print(f"Model in use: {model}")

        assert isinstance(model, str), "model must be string" 

        model_client = OpenAIChatCompletionClient(
            model=model, # this should pass as a string 
            api_key = api_key
            )
        agent = AssistantAgent(
            "assistant",
            model_client=model_client
            )
        # passing multiple queries here 
        task = [
            "What is Quantum computers?",
            "What are Agentic ai,how are they used?",
            "tell me something about sunitha williams",
            "What is illuminati in your perspective?"

        ]

        for query in task:
            print("=====================================================================================================")
            print(f"Query: {query}")
            response = await agent.run(task=query)
            print(f"response: {response}") 

        await model_client.close()  # close the model client

if __name__ == "__main__":
    agent = webagent()
    asyncio.run(agent.main())

