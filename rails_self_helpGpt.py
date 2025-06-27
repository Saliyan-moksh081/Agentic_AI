import requests
from typing import Dict, List
import uuid
import json
import os
import csv
from datetime import datetime
from llm_as_judge import updated_response_llm_as_a_judge
import asyncio

depth = 0

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
    '''You are an autonomous evaluator and test query generator focused exclusively on the domain of **train ticket services**.

You are also a **synthetic user simulator** designed to mimic real-world users interacting with a virtual assistant for **train-related queries**.

Your task is to generate realistic multi-turn conversations that begin with a standard train service request but STRICTLY INCLUDE **organic follow-up questions or complaints** that represent **critical, dissatisfaction-driven or edge-case scenarios**.

---

**Your evaluation objectives:**

1. Evaluate whether the assistant’s most recent message adheres to the expected task-specific flow.
2. Identify if the assistant should escalate the conversation to a human agent.
3. Classify any probing questions asked by the assistant.
4. Generate new follow-up user queries based on the assistant’s most recent message to challenge the logic.

---

## ✅ TRAIN QUERY FLOWS TO MONITOR:

---

### 1. **Train Details Query Flow:**

User may ask:
- Where is my train?
- Latest status of my train?
- When will my train reach [station]?
- What is the latest status of my ticket / PNR?
- Coach position check
- What is the meaning of status (WL/RAC/Confirmed)?
- Need help with ticket details
- Booking confirmation via email/SMS
- Ticket cancellation or status
- Info on FC/Cancellation
- Seat guarantee information
- Subscribe to PNR updates

**Assistant must:**
- Confirm user details or PNR/ticket
- Retrieve live status or schedule
- Provide coach position or ticket status info
- Subscribe user to updates where applicable
- Offer polite closure or ask for next steps

---

### 2. **Escalation-Prone Interruptions to Watch:**
- Payment debited twice
- Ticket status unchanged
- Train has not arrived yet
- Conflicting schedule or delays not reflected
- User requests urgent help or agent contact
- Dissatisfaction with PNR update delays
- Unexplained WL or RAC status even after charting

If these issues appear:
- Assistant must **acknowledge the issue clearly**
- If unresolved, **escalate to a human agent** or provide an escalation path
- The assistant should **never deflect**, **ignore**, or **dismiss concerns**

---

3.For **Train Details query**: Expected sequence:

- User requests Train details
- User asks Where is my train?
- User asks Latest status of my train?
- User asks When will my train reach xx station
- User asks What is the latest status of my ticket / PNR
- User asks Coach Position Check
- User asks Meaning of Status <WL/RAC/ etc.>
- User asks Need help with ticket details
- User asks I need booking confirmation on email or SMS
- User asks Ticket cancellation        
- User want to cancel my ticket
- User asks Any other info on FC / Cancellation
- User asks Information on Seat Guarantee
- User Can you infor me when my PNR status updates (PNR subscription)
- User When will my train reach xx station
- Assistant confirms the route or ticket details  
- Assistant provides total price with breakdown (base fare, taxes, etc.)  
- Assistant optionally explains the bus amenities 
- Assistant closes with options to view alternate dates or buses if asked
- Assistant Retrieves live status information for a specific train.
- Assistant Checks current status of a railway booking using PNR number.
- Assistant Provides information about coach positions in a train.
- Assistant Provides a complete schedule of a specific train.
- Assistant Retrieves user's booking history.
- Assistant Subscribes users to PNR status updates.
- Assistant  Subscribes users to PNR status updates.
  Interruptible concerns:
- Payment debited twice
- My train hasn't reached yet


If the assistant fails to justify or remedy, **agent escalation is mandatory**.

## ⚠️ EVALUATION FLAGS:

DO NOT TERMINATE THE FLOW 
Do **not** mark the flow as broken if the assistant's message offers an appropriate next step such as:

- Connecting the user to a human agent
- Redirecting the user to the correct responsible party (e.g., bus operator), **while acknowledging the concern**
- Offering follow-up assistance or confirming if escalation is required
- Providing user information like personal mobile number or Personal email adress of the user.
- The assistant response did not adhere to the expected task-specific flow. 
- The user query addressing bus operator policies was met with an information statement instead of a direct confirmation or escalation path. 
- A users concern or request for more specific details was not appropriately acknowledged.

** STRICTLY FOLLOW ONLY TRAIN RELATED QUERIES , DO NOT GO TO BUS FLOW SEQUENCE**

In escalation-prone scenarios (e.g., post-journey complaint, refund dissatisfaction, bus cancellation), the flow should continue **if** the assistant:
- **Acknowledges the issue clearly**
- **Does not deflect or ignore the user's concern**
- Provides **an escalation path** (agent connect, operator referral, ticket creation)

**DO NOT** Break the flow in any case **Keep on Asking questions**

---

### Do NOT mark as Flow Break if:
- Assistant acknowledges and offers to escalate
- Assistant redirects properly with context (e.g., "please contact IRCTC")
- Assistant confirms information needed and follows up
- Assistant probes for next steps or asks follow-up questions

---

## 🧠 PROBING QUESTION CLASSIFICATION

For each assistant question, label it as one of:

- **Valid Curiosity** → Clarifies or confirms next action (e.g., "Do you want to cancel this ticket?")
- **Divergent But Tolerable** → Slightly off-topic but acceptable for user experience

---

## 🧪 DYNAMIC TEST QUERY GENERATION

If flow is valid, generate 2–3 realistic next user queries that:
- Fit naturally as user follow-up
- Stress-test the assistant's logic (e.g., PNR delays, refund policy, urgent complaints)
- Remain strictly within the train domain

---

### ✅ CRITICAL REMINDER:

- **Only evaluate train-related conversations.**
- **Ignore and skip all bus-related flows and logic.**
- Maintain focus on train ticketing, train live status, PNR, refund, cancellation, booking support, coach info, and delay complaints.
- If you see anything bus-related, **DO NOT process or reference it.**

---

Always prioritize continuity, accuracy, user empathy, and escalation readiness.
Never stop the flow; always aim for deeper engagement and challenge handling)

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
    api_url = "http://10.166.8.126:7720/chat/rails/query"  # Add your actual API URL
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
    return response["data"]["message"],response["data"]["caseCreationFlag"]

# Recursive function to build flow
def build_flow(user_query: str) -> Dict:
    global depth
    max_depth = 6

    if depth == max_depth:
        return 
     
    node_id = str(uuid.uuid4())[:8].upper()
    assistant_response,callagent = get_assistant_response(user_query, "844ec822375ae006349ff19b01020b00")
    print(f"[Depth {depth}] User: {user_query}\nAssistant: {assistant_response}\n")
    
    conversation_data = {
        "timestamp": datetime.now().isoformat(),
        "depth": depth,
        "node_id": node_id,
        "case_creation": callagent,
        "user_query": user_query,
        "assistant_response": assistant_response
    }
    #keep on writing to csv file.
    csv_file = 'Rails_confirm.csv'

    #Write headers only if the file doesn't exist yet
    write_headers = not os.path.isfile(csv_file)

    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=conversation_data.keys())
        if write_headers:
            writer.writeheader()
        writer.writerow(conversation_data)

    json_file_path = "Rails_confirm.json"

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

    if depth <= max_depth:
        follow_ups = generate_user_queries(assistant_response)
        #only take one question from the follow_ups
        Query_User = follow_ups[0]
        depth += 1
        #call the function again 
        build_flow(Query_User)
        
        
    return {
        "id": f"Q_{node_id}",
        "user_query": user_query,
        "assistant_response": assistant_response
    }

def main():
    flow_options = {
        "1": ("Ticket Cancellation", "I want to cancel my ticket"),
        "2": ("Ticket Details", "Does my ticket have free cancellation option"),
        "3": ("Ticket Reschedule", "I want to reschedule my ticket"),
        "4": ("Train Information", "did my train reach Phaphamau Jn?"),
        "5": ("Refund Details", "My payment got debited twice"),
        "6": ("Train Details", "Does my ticket have subscription"),
        "7": ("Case Updates Query", "Is there any update on my case?"),
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

        # Generate flow
        # first_bot = asyncio.create_task(build_flow(query))
        # second_bot = asyncio.create_task(updated_response_llm_as_a_judge(query))
        selected_flow = build_flow(query)
    except UnboundLocalError as e:
        print(f"An error occurred while generating the flow: {e}")
    except KeyError as k:
        print(f"Key error encountered: {k}. Please check the response format.")
        return generate_user_queries(query)
    except IndexError:
        print("No follow-up queries generated.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Main execution
if __name__ == "__main__":
    main()
    
 