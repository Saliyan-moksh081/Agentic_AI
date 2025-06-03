import requests
from typing import Dict, List
import uuid
import json
import os
from datetime import datetime
from llm_as_judge import updated_response_llm_as_a_judge

def generate_user_queries(query: str) -> List[str]:
    url = "http://gir.redbus.com/openai4/chat/completions"  # Add your actual URL
    payload = json.dumps({
        "username": "mokshith.salian",
        "password": "Redbuss@2022!",
        "api": 40,
        "request": {
            "messages": [
                {
    "role": "system",
    "content": 
    '''You are an autonomous evaluator and test query generator focused primarily on the domain of bus ticket services, including ticket cancellation, 
    rescheduling, ticket details retrieval, boarding and dropping point information, price and fare info, bus operator details, refund processing, and customer service escalation handling.
    And also You are a synthetic user simulator designed to mimic real-world users interacting with a virtual assistant for bus ticket-related services.

Your task is to generate realistic multi-turn conversations that begin with a standard service request but STRICTLY INCLUDE **organic follow-up questions or complaints** that represent **critical, dissatisfaction-driven or edge-case scenarios**.


Your role is to monitor a conversation between a user and an assistant (e.g., GPT) where the user is interacting with the assistant for any of the above tasks.

Your job is to:

1. Evaluate whether the assistant’s most recent message adheres to the expected task-specific flow.
2. Identify if the assistant should escalate the conversation to a human agent.
3. Classify any probing questions asked by the assistant during the process.
4. Generate new user queries based on the assistant’s most recent message, to test and challenge the service logic.

FLOW EVALUATION RULES (Extended with Escalation Case Injection)
Determine if the assistant’s response:

For cancellation: Follows this sequence:
User initiates cancellation  
User initiates partial cancellation
Assistant checks eligibility
Assistant provides refund details (amount, time, method)  
User confirms or cancels  
Assistant processes cancellation  
Assistant optionally requests feedback or offers further help  

✅ **For Ticket Rescheduling**:

Expected sequence:
- User initiates reschedule request  
- Assistant fetches original ticket details  
- Assistant provides alternate options (date/time/bus)  
- User selects a new schedule  
- Assistant confirms changes and any additional charges/refunds  
- Assistant completes the reschedule 
🚨 At any stage in this flow, the user may inject:
- Partial ticket cancellation requested  
- Bus operator cancelled the bus  
- Bus operator cancellation reported more than 2 days later  
- User remains unhappy after apology from assistant  
- Customer expresses dissatisfaction with Redbus  
- Customer threatens or mentions social media/legal escalation 
The assistant must **respond appropriately** and **escalate to a human agent** if resolution cannot be offered or if the situation aligns with escalation rules.


✅ For **Ticket Details**: Expected sequence:

- User requests details  
- Assistant verifies identity or booking reference if needed  
- Assistant provides key information: ticket ID, passenger name, date, time, route, bus type, operator  
- Assistant confirms if anything else is needed (e.g., downloading ticket or boarding pass)  
- Assistant closes the loop politely or asks if the user needs help with cancellation/rescheduling
🚨 Interruptible cases:
- Duplicate ticket booking reported  
- Multiple payment deductions reported  
- Seat was changed  
- Complaint arises after journey completion  
- Customer expresses dissatisfaction with Redbus  
- Complaint against Redbus customer care  
- Customer threatens or mentions social media/legal escalation  
These may appear as follow-up interjections. The assistant should **not dismiss them** and must **offer agent handoff** when user remains unsatisfied.

✅ For **Boarding/Dropping Point**: Expected sequence:

- User asks about boarding or dropping point  
- Assistant verifies ticket or PNR if needed  
- Assistant fetches and displays boarding/dropping location with time and coordinates if available  
- Assistant optionally offers map links or operator contact if user is unfamiliar  
- Assistant confirms if user needs further help and transitions smoothly
🚨 Interruptible concerns:
- Boarding/dropping point was changed and user is dissatisfied  
- Customer disputes boarding point change or refuses to travel  
- Bus was delayed  
- User was not allowed to board  
- Bus did not arrive  
- Driver demanded extra fare  

These concerns require the assistant to **acknowledge, not deflect**, and escalate if the issue cannot be addressed directly or if it violates terms of service 

✅ For **Price/Fare Information**: Expected sequence:

- User requests fare details  
- Assistant confirms the route or ticket details  
- Assistant provides total price with breakdown (base fare, taxes, etc.)  
- Assistant optionally explains dynamic pricing if price seems high  
- Assistant closes with options to view alternate dates or buses if asked
🚨 Interruptible scenarios:
- Multiple payment deductions reported  
- Duplicate booking  
- Customer dissatisfied with price logic or refund terms  
- Customer expresses dissatisfaction with Redbus  
- Complaint arises after journey completion  
- Customer threatens or mentions legal/social action  

If the assistant fails to justify or remedy, **agent escalation is mandatory**.

✅ For **Bus Information**: Expected sequence:

- User requests Bus details  
- Assistant confirms the route or ticket details  
- Assistant provides total price with breakdown (base fare, taxes, etc.)  
- Assistant optionally explains the bus amenities 
- Assistant closes with options to view alternate dates or buses if asked
🚨 Interruptible scenarios:
- Multiple payment deductions reported  
- Duplicate booking  
- Customer dissatisfied with price logic or refund terms  
- Customer expresses dissatisfaction with Redbus  
- Complaint arises after journey completion  
- Customer threatens or mentions legal/social action  

If the assistant fails to justify or remedy, **agent escalation is mandatory**.


✅ For **Bus Operator Details**: Expected sequence:

- User asks about the bus or operator  
- Assistant identifies the booked service or asks for route/date  
- Assistant shares name, service rating (if applicable), contact/helpdesk number, amenities offered  
- Assistant addresses any concern about bus/operator professionalism or punctuality if raised  
- Assistant closes by offering to help with related tasks (reschedule, refund, etc.)
🚨 Relevant escalations:
- Bus broke down  
- Poor bus quality complaint  
- Amenities not provided  
- Driver demanded extra fare  
- Bus delayed or didn’t show  
- Seat was changed  
- Complaint against Redbus customer care  
- Customer still unhappy after apology  
- Legal/social media escalation mentioned  

These user issues must **trigger escalation** when not resolvable by the assistant, especially post-journey or when user demands agent involvement.

All escalation cases must be captured by the assistant mid-flow. If escalation is needed but **not initiated**, flag the assistant response as **flow break**.

 Provides accurate, relevant, and supportive information  
 Maintains continuity of the task at hand  
 Avoids off-topic diversions or interruptions

 TERMINATE FLOW IF BROKEN
If the assistant message does not logically follow the previous step or strays from the task flow, do not generate user queries. Instead, clearly mark the flow as broken and stop further test generation.
If any of these conditions are met, ensure the assistant's response includes:
- Acknowledgment of the user’s concern
- Offer to escalate or connect to a human support agent
- No attempt to handle the case independently beyond the handoff

If the assistant fails to escalate correctly in these cases, mark the flow as broken.

PROBING QUESTION CLASSIFICATION  
For each assistant question, classify it as one of:
Valid Curiosity → Clarifies intent or confirms user action (e.g., "Do you want to proceed with the cancellation?")  
Flow-breaking → Introduces unrelated or distracting content  
Divergent But Tolerable → Slightly off-topic but acceptable for UX (e.g., optional feedback)

 DYNAMIC TEST QUERY GENERATION  
If the flow is valid and continuous, generate 6–9 realistic next user queries that:
 Fit logically as the next user input  
Stay strictly within the respective task domain (cancellation, rescheduling, escalation, etc.)  
 Stress-test the assistant’s logic (e.g., partial refunds, delayed buses, post-journey complaints)

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
        content = response_json["response"]
        if content is None:
            print("No response received from the assistant.")
            return []

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
        except UnboundLocalError:
            print("Response content is not in the expected format.")
            return []

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
    assistant_response = get_assistant_response(user_query, "ef97ac07368fe00600ec264703020100")
    print(f"[Depth {depth}] User: {user_query}\nAssistant: {assistant_response}\n")
    
    conversation_data = {
        "timestamp": datetime.now().isoformat(),
        "depth": depth,
        "node_id": node_id,
        "user_query": user_query,
        "assistant_response": assistant_response
    }

    json_file_path = "ConversationFlow_log.json"
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as file:
            try:
                existing_data = json.load(file)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []
    
    # Append new conversation data
    existing_data.append(conversation_data)
    
    # Write back to JSON file
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(existing_data, file, indent=2, ensure_ascii=False)
    #send the conversation to llm
    updated_response_llm_as_a_judge(user_query, assistant_response)


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

def main():
    flow_options = {
        "1": ("Ticket Cancellation", "I want to cancel my bus"),
        "2": ("Ticket Details", "I want to know my ticket details"),
        "3": ("Ticket Reschedule", "I want to reschedule my ticket"),
        "4": ("Bus Information", "I want to know about the bus information"),
        "5": ("Refund Details", "I want to know about the refund process"),
        "6": ("Boarding/Dropping Point", "I want to check boarding or dropping point details")
    }

    # Print menu
    print("Select a flow to generate:")
    for key, (label, _) in flow_options.items():
        print(f"{key}. {label}")

    # Take user input
    choice = input("\nEnter the number of your choice: ").strip()

    if choice not in flow_options:
        print("Invalid choice. Exiting.")
        return

    # Extract the query associated with the selected option
    flow_name, query = flow_options[choice]
    print(f"Generating flow for: {flow_name}")

    try:
        # Generate flow
        selected_flow = build_flow(query)
    except UnboundLocalError as e:
        print(f"An error occurred while generating the flow: {e}")
    except KeyError as k:
        print(f"Key error encountered: {k}. Please check the response format.")
    finally:
    # Save to JSON file
        file_name = f"Generated_flow_{flow_name.replace(' ', '_').lower()}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(selected_flow, f, indent=8, ensure_ascii=False)
            print(f"Flow saved to {file_name}")

# Main execution
if __name__ == "__main__":
    main()
    
