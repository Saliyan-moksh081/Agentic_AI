from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
import uvicorn
from pydantic import BaseModel
from typing import List, Dict, Optional, Any, Union
import asyncio
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Free LLM API")

# Load a free LLM model - using a smaller model that can run on CPU
# You can replace this with any model of your choice from Hugging Face
model_name = "facebook/opt-350m"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name, 
    torch_dtype=torch.float32,  # Using float32 for CPU compatibility
    device_map="auto"
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    stream: bool = False
    messages: List[Message]
    model: Optional[str] = None

def format_messages(messages):
    """Format messages into a prompt that the model can understand"""
    formatted_prompt = ""
    
    for message in messages:
        if message.role == "system":
            if message.content:
                formatted_prompt += f"<|system|>\n{message.content}\n"
        elif message.role == "user":
            formatted_prompt += f"<|user|>\n{message.content}\n"
        elif message.role == "assistant":
            formatted_prompt += f"<|assistant|>\n{message.content}\n"
    
    # Add the final assistant tag to indicate it's the model's turn to respond
    formatted_prompt += "<|assistant|>\n"
    
    return formatted_prompt


async def generate_response(prompt, stream=False):
    """Generate response from the model"""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    # Explicitly create the attention mask if not present
    if "attention_mask" not in inputs:
        inputs["attention_mask"] = torch.ones_like(inputs["input_ids"])
    
    
    if stream:
        # Stream the response token by token
        generated_ids = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,  # Add this line
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            streamer=None,  # No built-in streamer for this example
        )
        generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        
        # Remove the prompt from the generated text to get only the response
        response_text = generated_text[len(tokenizer.decode(inputs.input_ids[0], skip_special_tokens=True)):]
        logger.info(f"Generated response: {response_text}")

        
        # Simulate streaming by yielding chunks of text
        words = response_text.split()
        for i in range(0, len(words), 3):  # Send 3 words at a time
            chunk = " ".join(words[i:i+3])
            yield f"data: {chunk}\n\n"
            await asyncio.sleep(1)  # Add small delay to simulate streaming
        
        yield f"data: [DONE]\n\n"
    else:
        # Generate the full response at once
        generated_ids = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )
        generated_text = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        
        # Remove the prompt from the generated text to get only the response
        response_text = generated_text[len(tokenizer.decode(inputs.input_ids[0], skip_special_tokens=True)):]
        logger.info(f"Generated response: {response_text}")

        yield response_text

#if api is hit without any endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to the Free LLM API!"}

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    """Endpoint for chat completions with optional streaming"""
    formatted_prompt = format_messages(request.messages)
    
    if request.stream:
        # Return a streaming response
        return StreamingResponse(
            generate_response(formatted_prompt, stream=True),
            media_type="text/event-stream"
        )
    else:
        generator = generate_response(formatted_prompt, stream=False)
        # Return a regular JSON response
        response_text = await generator.__anext__()
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "stop",
                    "index": 0
                }
            ],
            "model": request.model or model_name,
            "object": "chat.completion"
        }

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=4546, reload=True)
