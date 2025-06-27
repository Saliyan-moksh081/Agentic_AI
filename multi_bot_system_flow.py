import requests
from typing import Dict, List
import uuid
import json
import os
import csv
from datetime import datetime
import asyncio

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
User initiates question for refund details 
User initiates question about Free cancellation opted or not 
Assistant checks eligibility
Assistant provides refund details (amount, time, method)  
User confirms or cancels
Assistant processes cancellation  
Assistant optionally requests feedback or offers further help  

**For Ticket Refunding**: Follow this sequence:
User initiates a query regarding refund
Assistant validates ticket or booking reference
Assistant confirms refund status (amount, method, timeline)
Assistant explains refund policy (e.g., deductions, refund window, non-refundable rules)
Assistant offers to assist with any related next steps (e.g., cancellation confirmation, escalation, or delay clarification)
Assistant asks if the user needs anything else and politely concludes if resolved
At any stage in this flow, the user may inject:
Dissatisfaction with the refund amount or deductions
User already received a refund communication but is not satisfied
Multiple payment deductions and refund not processed correctly
Refund delayed beyond promised time
Partial ticket cancellation refund issues
Bus operator cancelled the bus, and user is demanding full refund
User remains unhappy after apology or policy explanation
User claims redBus support did not help or delayed resolution
Legal threat or social media escalation is mentioned
The assistant must **respond appropriately** and **escalate to a human agent** if resolution cannot be offered or if the situation aligns with escalation rules.

 **For Ticket Rescheduling**:

Expected sequence:
- User initiates reschedule request  
- Assistant fetches original ticket details  
- Assistant provides alternate options (date/time/bus)  
- User selects a new schedule  
- Assistant confirms changes and any additional charges/refunds  
- Assistant completes the reschedule 
 At any stage in this flow, the user may inject:
- Partial ticket cancellation requested  
- Bus operator cancelled the bus  
- Bus operator cancellation reported more than 2 days later  
- User remains unhappy after apology from assistant  
- Customer expresses dissatisfaction with Redbus  
- Customer threatens or mentions social media/legal escalation 
The assistant must **respond appropriately** and **escalate to a human agent** if resolution cannot be offered or if the situation aligns with escalation rules.


 For **Ticket Details**: Expected sequence:

- User requests details for the ticket details
- Assistant verifies identity or booking reference if needed  
- Assistant provides key information: ticket ID, passenger name, date, time, route, bus type, operator  
- Assistant confirms if anything else is needed (e.g., downloading ticket or boarding pass)  
- Assistant closes the loop politely or asks if the user needs help with cancellation/rescheduling
 Interruptible cases:
- Duplicate ticket booking reported  
- Multiple payment deductions reported  
- Seat was changed  
- Complaint arises after journey completion  
- Customer expresses dissatisfaction with Redbus  
- Complaint against Redbus customer care  
- Customer threatens or mentions social media/legal escalation  
These may appear as follow-up interjections. The assistant should **not dismiss them** and must **offer agent handoff** when user remains unsatisfied.

 For **Boarding/Dropping Point**: Expected sequence:

- User asks about boarding or dropping point  
- Assistant verifies ticket or PNR if needed  
- Assistant fetches and displays boarding/dropping location with time and coordinates if available  
- Assistant optionally offers map links or operator contact if user is unfamiliar  
- Assistant confirms if user needs further help and transitions smoothly
 Interruptible concerns:
- Boarding/dropping point was changed and user is dissatisfied  
- Customer disputes boarding point change or refuses to travel  
- Bus was delayed  
- User was not allowed to board  
- Bus did not arrive  
- Driver demanded extra fare  

For **CASE UPDATE QUERIES** :Expected sequence:

- User asks for case updates or complaint status
- User asks for case number and comments
- Assistant verifies user identity or case reference
- Assistant fetches and provides current status of the case or complaint
- Assistant explains next steps or expected resolution time
- Assistant confirms if user needs further assistance or has additional questions
- Assistant closes the loop politely or asks if the user needs help with cancellation/rescheduling
Interruptible concerns:
- User expresses dissatisfaction with case handling or resolution
- User demands immediate resolution or threatens escalation
- User claims case was mishandled or not addressed properly
- User threatens or mentions social media/legal escalation
- User demands to speak with a human agent immediately
**strictly follow this sequence**      

These concerns require the assistant to **acknowledge, not deflect**, and escalate if the issue cannot be addressed directly or if it violates terms of service 

 For **Price/Fare Information**: Expected sequence:

- User requests fare details  
- Assistant confirms the route or ticket details  
- Assistant provides total price with breakdown (base fare, taxes, etc.)  
- Assistant optionally explains dynamic pricing if price seems high  
- Assistant closes with options to view alternate dates or buses if asked
 Interruptible scenarios:
- Multiple payment deductions reported  
- Duplicate booking  
- Customer dissatisfied with price logic or refund terms  
- Customer expresses dissatisfaction with Redbus  
- Complaint arises after journey completion  
- Customer threatens or mentions legal/social action  

If the assistant fails to justify or remedy, **agent escalation is mandatory**.

 For **Bus Information**: Expected sequence:

- User requests Bus details  
- Assistant confirms the route or ticket details  
- Assistant provides total price with breakdown (base fare, taxes, etc.)  
- Assistant optionally explains the bus amenities 
- Assistant closes with options to view alternate dates or buses if asked
Interruptible scenarios:
- Multiple payment deductions reported  
- Duplicate booking  
- Customer dissatisfied with price logic or refund terms  
- Customer expresses dissatisfaction with Redbus  
- Complaint arises after journey completion  
- Customer threatens or mentions legal/social action  

If the assistant fails to justify or remedy, **agent escalation is mandatory**.

For **Bus Operator Details**: Expected sequence:

- User asks about the bus or operator  
- Assistant identifies the booked service or asks for route/date  
- Assistant shares name, service rating (if applicable), contact/helpdesk number, amenities offered  
- Assistant addresses any concern about bus/operator professionalism or punctuality if raised  
- Assistant closes by offering to help with related tasks (reschedule, refund, etc.)
 Relevant escalations:
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

DO NOT TERMINATE THE FLOW 
Do **not** mark the flow as broken if the assistant's message offers an appropriate next step such as:

- Connecting the user to a human agent
- Redirecting the user to the correct responsible party (e.g., bus operator), **while acknowledging the concern**
- Offering follow-up assistance or confirming if escalation is required
- Providing user information like personal mobile number or Personal email adress of the user.
- The assistant response did not adhere to the expected task-specific flow. 
- The user query addressing bus operator policies was met with an information statement instead of a direct confirmation or escalation path. 
- A users concern or request for more specific details was not appropriately acknowledged.

In escalation-prone scenarios (e.g., post-journey complaint, refund dissatisfaction, bus cancellation), the flow should continue **if** the assistant:
- **Acknowledges the issue clearly**
- **Does not deflect or ignore the user's concern**
- Provides **an escalation path** (agent connect, operator referral, ticket creation)

**DO NOT** Break the flow in any case **Keep on Asking questions**

PROBING QUESTION CLASSIFICATION  
For each assistant question, classify it as one of:
Valid Curiosity → Clarifies intent or confirms user action (e.g., "Do you want to proceed with the cancellation?")  
Flow-breaking → Introduces unrelated or distracting content  
Divergent But Tolerable → Slightly off-topic but acceptable for UX (e.g., optional feedback)

DYNAMIC TEST QUERY GENERATION  
If the flow is valid and continuous, generate 2-3 realistic next user queries that:
Fit logically as the next user input.
Stay strictly within the respective task domain (cancellation, rescheduling, escalation, etc.).  
Stress-test the assistant’s logic (e.g., partial refunds, delayed buses, post-journey complaints)

Return these in the following Json format like:
{{
  "possible_user_responses": [
    "query1"
  ]
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
            #print("Failed to parse response content as JSON:")
            return []
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
        "Content-Type": "application/json",
        "Country_Name": "PER",
        "BusinessUnit": "BUS"
    }

    response = requests.request("POST", api_url, headers=headers, data=payload, verify=False)
    response = response.json()
    return response["data"]["message"],response["data"]["callAgent"]

def get_orchestrator_response(question, orderuuid):
    api_url = "http://10.166.8.126:8099/agentic_chat/COL/BUS/SELFHELP/query"  # Add your actual API URL
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
    return response["data"]["message"],response["data"]["callAgent"]

def save_to_csv(conversation_data, csv_file):
    write_headers = not os.path.isfile(csv_file)
    
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=conversation_data.keys())
        if write_headers:
            writer.writeheader()
        writer.writerow(conversation_data)

# Helper function to save to JSON
def save_to_json(conversation_data):
    json_file_path = "latam_log.json"
    
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

async def run_parallel(query):
    global depth, iter
    max_depth = 6
    
    # Start with the initial query
    current_query = query
    
    # Create storage for conversation history
    bot1_history = []
    bot2_history = []
    
    # Run the conversation for up to max_depth turns
    for turn in range(max_depth + 1):
        # Reset depth and iter for this turn
        depth = turn
        iter = turn
        
        # Get responses from both bots to the same query
        node_id1 = str(uuid.uuid4())[:8].upper()
        node_id2 = str(uuid.uuid4())[:8].upper()
        
        # Get responses from both systems
        assistant_response1, callagent1 = get_assistant_response(current_query, "250d2da737aee006d3b2c8ba02020800")
        assistant_response2, callagent2 = get_orchestrator_response(current_query, "250d2da737aee006d3b2c8ba02020800")
        
        # Print responses
        print(f"[Turn {turn}] User: {current_query}")
        print(f"Bot 1: {assistant_response1}")
        print(f"Bot 2: {assistant_response2}\n")
        
        # Create conversation data for bot 1
        conversation_data1 = {
            "timestamp": datetime.now().isoformat(),
            "depth": turn,
            "node_id": node_id1,
            "call_agent": callagent1,
            "user_query": current_query,
            "assistant_response": assistant_response1,
            "bot": "standard"
        }
        
        # Create conversation data for bot 2
        conversation_data2 = {
            "timestamp": datetime.now().isoformat(),
            "depth": turn,
            "node_id": node_id2,
            "call_agent": callagent2,
            "user_query": current_query,
            "assistant_response": assistant_response2,
            "bot": "orchestrator"
        }
        
        # Save to CSV files
        save_to_csv(conversation_data1, '/Users/mokshith.salian/Documents/Agentic_AI/Agentic_AI/templatam.csv')
        save_to_csv(conversation_data2, '/Users/mokshith.salian/Documents/Agentic_AI/Agentic_AI/temporchestrator.csv')
        
        # Save to JSON
        save_to_json(conversation_data1)
        save_to_json(conversation_data2)
        
        # Store in history
        bot1_history.append(conversation_data1)
        bot2_history.append(conversation_data2)
        
        # Break if we've reached max depth
        if turn == max_depth:
            break
            
        # Generate the next question using only the first bot's response
        # You could also use both responses to generate the next query
        follow_ups = generate_user_queries(assistant_response1)
        
        # Check if we got any follow-ups
        if not follow_ups:
            print("No follow-up questions generated. Ending conversation.")
            break
            
        # Set the next query
        current_query = follow_ups[0]
    
    return bot1_history, bot2_history
   

async def main():
    flow_options = {
        "1": ("Ticket Cancellation", "I want to cancel my ticket"),
        "2": ("Ticket Details", "I want to know my ticket details"),
        "3": ("Ticket Reschedule", "I want to reschedule my ticket"),
        "4": ("Bus Information", "I want to know about the bus information"),
        "5": ("Refund Details", "I want to know about the refund amount"),
        "6": ("Boarding/Dropping Point", "I want to check boarding or dropping point details"),
        "7": ("Case Updates Query", "what is the status of my cpomplaint"),
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
    global selected_flow
    try:
        #  loop = asyncio.get_event_loop()
        # # Generate flow in parallel
        #  loop.run_until_complete(run_parallel(query))
        await run_parallel(query)
         
        #selected_flow = build_flow(query)
    except UnboundLocalError as e:
        print(f"An error occurred while generating the flow: {e}")
    except KeyError as k:
        print(f"Key error encountered: {k}. Please check the response format.")
    except IndexError:
        print("bot ended as connected to agent")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Main execution
if __name__ == "__main__":
    asyncio.run(main())
    
 