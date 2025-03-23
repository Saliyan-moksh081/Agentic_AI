"""
 AutoGen agent that calls an API based on your prompt using the 
 requests library. 
 This agent can handle both GET and POST requests.
"""
import requests
from dotenv import load_dotenv
import os
from autogen.agentchat import AssistantAgent, UserProxyAgent, register_function

# load_dotenv()
# api_key = os.getenv("GEMINI_KEY")

#define the model to use
config_list =[
    {
        "model": "gpt-4o",
        "api_key": ""
    }
]
#define the llm config
llm_config ={
    "timeout": 10,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0   
    } 
#Function to Get requets 

def get_request(url: str) -> str:
    try:
        response = requests.get(url)
        print(response.status_code)
        return response.json()
    except requests.exceptions.RequestException as e:
        return f"error {e}"

#function for post requests

def post_request(url: str, data: dict=None, headers: dict=None) -> str:
    try:
        response = requests.post(url,json=data,headers=headers)
        print("post response")
        status = response.status_code
        return status,response.json()
    except requests.exceptions.RequestException as e:
        return f"error: {e}"

#define the autogen agents 
assistant = AssistantAgent(
    name="Api_assistant",
    llm_config=llm_config,
)

user = UserProxyAgent(
    name="User",
    human_input_mode="TERMINATE",
    code_execution_config={
            "use_docker": False,
            "work_dir": "Apilogs"
        }
)
# defining the register functions to make above functions to e detected ny agent 
#get request
register_function(
    get_request,
    caller=assistant,
    executor=user,  # this is an proxy agent 
    name = "get_call",
    description="this makes a get call to the api"
)
# post request
register_function(
    post_request,
    caller=assistant,
    executor=user,  # this is an proxy agent 
    name = "post_call",
    description="this makes a post call to the api"
)
prompts = [
    """
    make a POST request to {}  with the  folowing json payload:
    {
    "city": "std:044",
    "endingStation": "SGE|0109",
    "startingStation": "SGM|0115",
    "txnId": ""
} 
and with this headers:
    {
    "AuthToken": "",
    "Channel_Name": "MOBILE_APP",
    "BusinessUnit": "",
    "Content-Type": "application/json"
    }
    """,
    "Make an Get request call to {} "
]
# iam combining the above list into a single string with mutiple queries
task_string = "\n".join([f"{i+1}. {task}" for i, task in enumerate(prompts)])

# initiate the chat 
user.initiate_chat(
    assistant,
    message=task_string
)



