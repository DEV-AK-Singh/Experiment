import re
import random
from datetime import datetime

class SimpleChatbot:
    def __init__(self):
        self.name = "ChatBot"
        self.responses = {
            'greeting': [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Hey! Nice to meet you. How can I assist?"
            ],
            'farewell': [
                "Goodbye! Have a great day!",
                "See you later!",
                "Bye! Come back anytime!"
            ],
            'thanks': [
                "You're welcome!",
                "Happy to help!",
                "Anytime!"
            ],
            'name': [
                f"I'm {self.name}, your friendly assistant!",
                f"My name is {self.name}. Nice to meet you!",
                f"Call me {self.name}. How can I help?"
            ],
            'weather': [
                "I don't have access to weather data, but I hope it's nice where you are!",
                "You should check a weather app for accurate forecasts.",
                "I'm just a chatbot, but I hope the weather is pleasant for you!"
            ],
            'joke': [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Why did the scarecrow win an award? He was outstanding in his field!",
                "What do you call a fake noodle? An impasta!"
            ],
            'help': [
                "I can chat with you, tell jokes, answer simple questions, or just keep you company!",
                "Try asking me about my name, tell me a joke, or just say hello!",
                "I'm here to chat! You can ask me anything and I'll do my best to respond."
            ]
        }
    
    def find_pattern(self, message):
        """Match user input to response patterns"""
        message_lower = message.lower()
        
        # Greeting patterns
        if re.search(r'\b(hi|hello|hey|greetings|good morning|good afternoon)\b', message_lower):
            return 'greeting'
        
        # Farewell patterns
        elif re.search(r'\b(bye|goodbye|see you|farewell|quit|exit)\b', message_lower):
            return 'farewell'
        
        # Thanks patterns
        elif re.search(r'\b(thanks|thank you|appreciate it)\b', message_lower):
            return 'thanks'
        
        # Name patterns
        elif re.search(r'\b(what.*your name|who are you|your name)\b', message_lower):
            return 'name'
        
        # Weather patterns
        elif re.search(r'\b(weather|rain|sunny|temperature|forecast)\b', message_lower):
            return 'weather'
        
        # Joke patterns
        elif re.search(r'\b(joke|funny|make me laugh)\b', message_lower):
            return 'joke'
        
        # Help patterns
        elif re.search(r'\b(help|what can you do|how does this work)\b', message_lower):
            return 'help'
        
        # Default response
        else:
            return 'default'
    
    def get_response(self, message):
        """Generate response based on pattern"""
        pattern = self.find_pattern(message)
        
        if pattern in self.responses:
            return random.choice(self.responses[pattern])
        else:
            # Default responses for unmatched patterns
            default_responses = [
                "That's interesting! Tell me more.",
                "I see. What else would you like to know?",
                "Thanks for sharing! Is there anything specific you'd like to talk about?",
                "I'm still learning. Could you rephrase that?",
                "That's cool! What's on your mind?"
            ]
            return random.choice(default_responses)
    
    def chat(self, message):
        """Main chat method"""
        response = self.get_response(message)
        return {
            "user_message": message,
            "bot_response": response,
            "timestamp": datetime.now().isoformat(),
            "pattern": self.find_pattern(message)
        }