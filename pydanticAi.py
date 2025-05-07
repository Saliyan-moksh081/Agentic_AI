import nest_asyncio
from pydantic_ai import Agent
from pydantic import BaseModel as AIBaseModel  # Use the correct import
import httpx

nest_asyncio.apply()

# Create a custom model class that inherits from the correct base class
class CustomLLM(AIBaseModel):
    def __init__(self, model_name="mistral:latest", api_url="http://10.120.17.147:11434/api/chat"):
        super().__init__()  # Important to call parent's __init__
        self.model_name = model_name
        self.api_url = api_url
    
    async def generate(self, messages, **kwargs):
        """Send request to custom API endpoint"""
        headers = {"Content-Type": "application/json"}
        
        payload = {
            "stream": False,
            "messages": messages,
            "model": self.model_name
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract content from API response
            if "choices" in result:
                return result["choices"][0]["message"]["content"]
            else:
                # If API has different response format, extract content appropriately
                return result.get("content", "No content returned from API")

# Create an instance of your custom model
model = CustomLLM(model_name="mistral:latest")

# Use the model instance directly with the Agent
basic_agent = Agent(
    model=model,  # Pass the model instance directly
    system_prompt="You are a Doctor with 20 years of experience in the field of cardiology. You need to provide medicine and treatment for the patients",
)

response = basic_agent.run_sync("I am having severe headache after taking hot bath, what is the issue?")
print(response.data)
print(response.all_messages())