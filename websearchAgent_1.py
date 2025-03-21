import autogen
from autogen_agentchat.agents import AssistantAgent
from duckduckgo_search import DDGS
from dotenv import load_dotenv
from autogen.agentchat import register_function
import os
from huggingface_hub import InferenceApi
from autogen_ext.models.openai import OpenAIChatCompletionClient


load_dotenv()
api_key = os.getenv("GEMINI_KEY")

#define the model to use
config_list =[
    {
        "model": "gemini-1.5-flash-8b",
        "api_key": os.getenv("GEMINI_KEY")
    }
]
#define the llm config
llm_config ={
    "timeout": 10,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0   
    } 

# model_client = OpenAIChatCompletionClient(
#         model="gemini-1.5-flash-8b",
#         api_key = api_key
#           )

# api_key = os.getenv("HUGGING_FACE_API_KEY")
# inference_api = InferenceApi(repo_id="meta-llama/Llama-3.2-1B", token=api_key)

def web_search(query: str) -> str:
    """Find information on the web"""
    return "A websearch agent which searches the web for Internet"
    

#here iam defining the web search agent
web_agent = autogen.AssistantAgent(
    name="Webagent",
    description = "a web agent which searches the web for information",
    llm_config=llm_config
)

#Define the user proxy agent - this is used to give the users chat 
user = autogen.UserProxyAgent(
    name="User_proxy",
    human_input_mode="TERMINATE", #user decides whether to continue or not 
    max_consecutive_auto_reply=5,
    is_termination_msg=lambda x: x.get("content","").rstrip().endswith("TERMINATE"),
    code_execution_config={
            "use_docker": False
        }
           # set use docker to true only if running using docker ,else false if running locally 
)

#register the function to be called by the agent 
# websearch_registered = register_function(
#     web_search,
#     caller = web_agent,
#     executor= user,
#     name="websearch",
#     description="a web tool that searches the web for information"
# )

task="""
search the web for the name elon musk
"""
#start the interaction chat 
user.initiate_chat(
    web_agent, 
    message=task
    )
