import json
import os
import requests
import csv
from typing import Dict, List
import time

def generate_user_queries(query,answer):
    url = "http://gir.redbus.com/openai4/chat/completions"
      # Add your actual URL
    prompt ="""You are an evaluation AI designed to assess chatbot interactions in the domain of **bus ticket services**. Your task is to read each row containing two fields:

- "user_query": the customer’s message.
- "assistant_response": the chatbot’s reply

You will score the assistant’s response from 0% to "100%" based on predefined metrics. If any field is missing or invalid, handle gracefully and note it in the explanation.

---

**✅ INPUT VALIDATION:**

1. If `user_query` is empty or null, return:
   - final_score: 0%
   - explanation: "Missing user query. Evaluation skipped."

2. If `assistant_response` is empty or null:
   - contextual_accuracy = 0%
   - resolution_value = 0%
   - sentiment_handling = "N/A"
   - completion_and_coherence = 0%
   - final_score = 0%
   - explanation: "Assistant provided no response."

---

**✅ DOMAIN RELEVANCE:**

The query is only valid if it relates to:
- Ticket cancellation or rescheduling
- Ticket details lookup
- Boarding/dropping point info
- Fare/pricing details
- Bus operator details
- Refund processing
- Dissatisfaction or complaint resolution
- Routing to a human agent when needed

---

**📊 EVALUATION METRICS (out of 100%):**

- **Contextual Accuracy (40%)**:
  - Is the reply relevant to the domain and question?
  - Is the answer accurate and stays on topic?

- **Resolution Value (30%)**:
  - Was the query answered or redirected to an agent appropriately?

- **Sentiment Handling (20%)**:
  - If user is upset or rude, does the assistant stay composed and supportive?
  - Mark "N/A" if sentiment not expressed.

- **Completion & Coherence (10%)**:
  - Is the reply grammatically correct, complete, and easy to understand?

---

**🧾 OUTPUT FORMAT:**

Always return results in **this exact JSON format**:
{{
  "final_score": "TOTAL_PERCENTAGE%",
  "explanation": "Brief explanation in plain language (2-3 sentences max)"
}}


---

**📎 NOTES:**

- Round all percentages to the nearest multiple of 5 (e.g., 85%, 70%, 0%).
- If `user_query` is unrelated to bus ticket services (e.g., “what’s the weather”), assign "0%" contextual_accuracy.
- If the assistant escalates unresolved issues to a human agent and the query is valid, resolution_value can be 100%.
- If sentiment is not present in `user_query`, set `sentiment_handling` = "N/A".

---

**📌 EXAMPLES:**

1. **Good Resolution**
"{query}": "Can I reschedule my 9pm bus to 10pm?",
"{answer}": "Yes, please open your app, go to 'My Bookings' and choose 'Reschedule'.",

OUTPUT:
{{ 
"final_score": "100%",
"explanation": "The assistant responded directly, accurately, and resolved the query clearly."
}}
 

2. **Escalation to Agent**
"{query}": "Why haven't I received my refund after 3 days? This is ridiculous!",
"{answer}": "I apologize for the delay. I’m connecting you to our human support team to resolve this quickly.",
{{
  "final_score": "98%",
  "explanation": "The assistant acknowledged the frustration and routed the issue appropriately."
}}


3. **Empty Response**
"{query}": "Where is my bus?",
"{answer}": "",
{{
  "final_score": "0%",
  "explanation": "The assistant failed to respond, so evaluation scores are zero."
}}

user_query : "{query}"
assistant_response : "{answer}"

Take Your Time. Check Your Work. Always Prioritize Accuracy.""".format(query=query, answer=answer)


    payload = json.dumps({
        "username": "mokshith.salian",
        "password": "Redbuss@2022!",
        "api": 40,
        "request": {
            "messages": [
                {
    "role": "system",
    "content": prompt

                }
            ]
        }
    })

    headers = {
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    response_text = json.loads(response.text)
    response_text = response_text["response"]["openAIResponse"]["choices"][0]["message"]["content"]

    return response_text
 

if __name__ == "__main__":
    
    csv_file_path = "/Users/mokshith.salian/Documents/Agentic_AI/Agentic_AI/Self Help Conversation Test Metrics  - Sheet1.csv"
    # Read all rows into memory
    with open(csv_file_path, mode='r') as file:
        csv_reader = csv.DictReader(file)
        fieldnames = csv_reader.fieldnames
        rows = list(csv_reader)

    # Update each row by appending to Accuracy_score
    for row in rows:
        user = row['text']
        response = row['transcript/response from Bot']
        if user:
            percentage = generate_user_queries(user, response)
            print(percentage)
            try:
                percentage = json.loads(percentage)
                new_score = percentage["final_score"]
                row['Accuracy_score'] = new_score
            except json.JSONDecodeError:
                if percentage.strip().startswith("```json") and percentage.strip().endswith("```"):
                    percentage = percentage.strip().replace("```json", "").replace("```", "").strip()
                    percentage = json.loads(percentage)
                    new_score = percentage["final_score"]
                    row['Accuracy_score'] = new_score
    # Write all updated rows back to the file
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    

                  
                    
                

   



  

