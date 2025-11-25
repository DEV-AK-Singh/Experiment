from asyncio import wait
from time import sleep
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Dict, Any

from chatbot import SimpleChatbot

# Create FastAPI app
app = FastAPI(
    title="Simple Chatbot API",
    version="1.0.0",
    description="A rule-based chatbot that responds to patterns"
)

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize chatbot
chatbot = SimpleChatbot()

# Request model
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    user_message: str
    bot_response: str
    timestamp: str
    pattern: str

class ChatHistory(BaseModel):
    conversations: List[Dict[str, Any]]

# Store chat history (in production, use database)
chat_history = []

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health_check():
    return {"status": "healthy", "bot_name": chatbot.name}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat with the bot"""
    try:
        if not request.message.strip():
            return ChatResponse(
                user_message="",
                bot_response="Please type a message!",
                timestamp="",
                pattern="error"
            )
        
        # Get bot response
        response = chatbot.chat(request.message)
        
        # Store in history (simple in-memory storage)
        chat_history.append(response)
        
        # Keep only last 50 messages
        if len(chat_history) > 50:
            chat_history.pop(0)

        # wait for 2 seconds before returning the response
        sleep(2)
        
        return ChatResponse(**response)
        
    except Exception as e:
        return ChatResponse(
            user_message=request.message,
            bot_response="Sorry, I encountered an error. Please try again.",
            timestamp="",
            pattern="error"
        )

@app.get("/history", response_model=ChatHistory)
async def get_chat_history():
    """Get chat history"""
    return {"conversations": chat_history}

@app.delete("/history")
async def clear_chat_history():
    """Clear chat history"""
    global chat_history
    chat_history = []
    return {"message": "Chat history cleared"}

@app.get("/patterns")
async def get_supported_patterns():
    """Get supported conversation patterns"""
    return {
        "supported_patterns": list(chatbot.responses.keys()),
        "examples": {
            "greeting": ["hello", "hi", "good morning"],
            "farewell": ["bye", "goodbye", "see you"],
            "thanks": ["thank you", "thanks"],
            "name": ["what's your name", "who are you"],
            "weather": ["what's the weather", "is it raining"],
            "joke": ["tell me a joke", "make me laugh"],
            "help": ["help", "what can you do"]
        }
    }