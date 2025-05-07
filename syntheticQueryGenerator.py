import requests
from typing import Dict, List
import uuid
import json

def generate_user_queries(query: str) -> List[str]:
    url = "http://gir.redbus.com/openai4/chat/completions"  # Add your actual URL
    payload = json.dumps({
        "username": "",
        "password": "",
        "api": 40,
        "request": {
            "messages": [
                {
                    "role": "system",
                    "content": '''You are a Smart assistant whose task is to generate 5 user responses that are likely to follow for the given query. Ensure that 5 generated queries are strictly related to **bus travel**. 
Use **natural, commonly spoken words** for each language instead of overly formal or bookish language.

user_queries: {user_queries_with_response}

### **Output Format:**  
Output should be in json format. Don't add any other field to the output.
'''.format(user_queries_with_response=query)
                }
            ]
        }
    })

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    
    try:
        response_json = json.loads(response.text)
        response_content = response_json["response"]["openAIResponse"]["choices"][0]["message"]["content"]

        # Clean possible code-block markdown
        if "json" in response_content:
            response_content = response_content.replace("```json", "").replace("", "").strip()

        # Try to parse the response content as JSON
        parsed_response = json.loads(response_content)

        # Debug print
        print("Parsed response:", parsed_response)
        print("Type:", type(parsed_response))

        # Return based on whether it's a list or dict
        if isinstance(parsed_response, list):
            return parsed_response
        elif isinstance(parsed_response, dict):
            return parsed_response.get("possible_user_responses", [])
        else:
            return []
    
    except json.JSONDecodeError as e:
        print("Failed to parse response content as JSON:", response.text)
        return []

# Function to generate follow-up queries using the assistant's message
def get_assistant_response(question, orderuuid):
    api_url = "http://selfhelp-gpt.redbus.com:17714/chat/query"  # Add your actual API URL
    payload = json.dumps({
        "message": question,
        "orderItemUUID": orderuuid
    })

    headers = {
        "X-CLIENT": "SELF_HELP",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", api_url, headers=headers, data=payload, verify=False)
    response = response.json()
    return response["data"]["message"]

# Recursive function to build flow
def build_flow(user_query: str, depth: int = 0, max_depth: int = 3) -> Dict:
    node_id = str(uuid.uuid4())[:8].upper()
    assistant_response = get_assistant_response(user_query, "448de5ff300cf006de86aae303020100")

    # Stop if assistant says it's time to connect to an agent
    
    if "apologized" in assistant_response:
        return {
            "id": f"Q_{node_id}",
            "user_query": user_query,
            "assistant_response": assistant_response,
            "children": [],
            "stop_reason": "agent_connection"
        }

    children = []

    if depth < max_depth:
        follow_ups = generate_user_queries(assistant_response)

        # Clean up JSON code blocks if needed
        if follow_ups:
            follow_ups = [follow_up.strip("json").strip("") if isinstance(follow_up, str) else follow_up for follow_up in follow_ups]

        # Recursively build flow for each follow-up query
        for follow_up in follow_ups:
            child_node = build_flow(follow_up, depth + 1, max_depth)
            children.append(child_node)

    return {
        "id": f"Q_{node_id}",
        "user_query": user_query,
        "assistant_response": assistant_response,
        "children": children
    }

# Main execution
if __name__ == "__main__":
    flow = {
        "flow_name": "bus_quality_complaint",
        "root": build_flow("my bus was not clean")
    }

    with open("generated_flow.json", "w", encoding="utf-8") as f:
        json.dump(flow, f, indent=2, ensure_ascii=False)

    print("Flow saved to generated_flow.json")


def user_cancellation_flow(query):
    url = "http://gir.redbus.com/openai4/chat/completions"  # Add your actual URL
    payload = json.dumps({
        "username": "",
        "password": "",
        "api": 40,
        "request": {
            "messages": [
                {
                    "role": "system",
                    "content": ''' probing questions after response: This should be sequential

                                   1. User wants to cancel ticket(here user should get an option to cancel ticket partially or fully)
                                   2. Now user can select the option provided or 
'''.format(user_queries_with_response=query)
                }
            ]
        }
    })

    headers = {
        'Content-Type': 'application/json'
    } 
    response = requests.request("POST", url, headers=headers, data=payload)