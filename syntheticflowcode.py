import requests
from typing import Dict, List
import uuid
import json

def generate_user_queries(query: str) -> List[str]:
    url = "http://gir.redbus.com/openai4/chat/completions"  # Add your actual URL
    payload = json.dumps({
        "username": "mokshith.salian",
        "password": "Redbus@2022!",
        "api": 40,
        "request": {
            "messages": [
                {
                    "role": "system",
                    "content": '''You are an autonomous evaluator and test query generator focused exclusively on the task of ticket cancellation.

Your role is to monitor a conversation between a user and an assistant (e.g., GPT) where the user is attempting to cancel a ticket. Your job is to:

Evaluate whether the assistant’s most recent message adheres to the expected cancellation flow.

Classify any probing questions asked by the assistant during the process.

Generate new user queries based on the assistant’s most recent message, to test and challenge the cancellation logic.

🔹 FLOW EVALUATION RULES
Determine if the assistant’s response:

✅ Follows the expected ticket cancellation sequence:
User initiates cancellation
Assistant checks eligibility
Assistant provides refund details (amount, time, method)
User confirms or cancels
Assistant processes cancellation
Assistant optionally requests feedback or offers further help

✅ Provides accurate, relevant, and supportive information
✅ Maintains continuity of the cancellation task

❌ Avoids off-topic diversions or interruptions

⚠️ TERMINATE FLOW IF BROKEN
If the assistant message does not logically follow the previous step or strays from the cancellation flow, do not generate user queries. Instead, clearly mark the flow as broken and stop further test generation.
🔹 PROBING QUESTION CLASSIFICATION
For each assistant question, classify it as one of:
Valid Curiosity → Clarifies intent or confirms user action (e.g., "Do you want to proceed with the cancellation?")
Flow-breaking → Introduces unrelated or distracting content
Divergent But Tolerable → Slightly off-topic but acceptable for UX (e.g., optional feedback)

🔹 DYNAMIC TEST QUERY GENERATION
If the flow is valid and continuous, generate 2–3 realistic next user queries that:
✅ Fit logically as the next user input
✅ Stay strictly within the cancellation domain
✅ Stress-test the assistant’s logic (e.g., partial refunds, late cancellations, method-specific issues)
Return these in the following JSON format:

{{
  "possible_user_responses": [
    "query1",
    "query2",
    "query3"
  ]
}}
If flow is broken:
{{
  "flow_status": "broken",
  "reason": "Explanation of how the flow was interrupted or violated"
}}

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
        # Parse the response from the assistant
        response_json = json.loads(response.text)
        response_content = response_json["response"]["openAIResponse"]["choices"][0]["message"]["content"]

        # Try to parse the response content as JSON
        try:
            if "json" in response_content:
                response_content = response_content.strip("json").strip("")
            parsed_response = json.loads(response_content)
            print()
            return parsed_response.get("possible_user_responses", [])
        except json.JSONDecodeError:
            print("Failed to parse response content as JSON:", response_content)
            return [parsed_response]

    except json.JSONDecodeError as e:
        print(f"Failed to parse the response JSON: {e}")
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
def build_flow(user_query: str, depth: int = 0, max_depth: int = 20) -> Dict:
    node_id = str(uuid.uuid4())[:8].upper()
    assistant_response = get_assistant_response(user_query, "a07b85a13577e00600ec264701020100")
    print(f"[Depth {depth}] User: {user_query}\nAssistant: {assistant_response}\n")

    children = []

    if depth < max_depth:
        follow_ups = generate_user_queries(assistant_response)

        # Clean follow-ups if they are wrapped in code blocks
        if follow_ups:
            follow_ups = [follow_up.strip("json").strip(" ").strip() for follow_up in follow_ups]

        # If we received follow-ups, recursively build the flow
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
    
    selected_flow = build_flow("I want to cancel my ticket")

    with open("Generated_flow.json", "w", encoding="utf-8") as f:
        json.dump(selected_flow, f, indent=10, ensure_ascii=False)
        print(f"Flow saved to {f}")