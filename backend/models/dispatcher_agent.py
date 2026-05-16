"""AI Dispatcher Agent for emergency coordination"""

from transformers import pipeline
from database.responder_db import find_available_responders
from utils.conversation_utils import (
    extract_location_from_conversation,
    extract_disaster_type_from_conversation
)


class DispatcherAgent:
    """AI agent for dispatcher coordination"""
    
    def __init__(self, config):
        self.config = config
        self.agent = None
        self.state = {
            "location": None,
            "disaster_type": None,
            "dispatched_units": []
        }
        self.initialize_agent()
    
    def initialize_agent(self):
        """Initialize the AI agent model"""
        try:
            print("🤖 Initializing Dispatcher AI Agent...")
            self.agent = pipeline(
                "text2text-generation",
                model=self.config.DISPATCHER_MODEL_NAME,
                device=0 if self.config.DEVICE == "cuda" else -1
            )
            print("✅ Dispatcher AI Agent initialized!")
            return True
        except Exception as e:
            print(f"⚠️ Failed to initialize dispatcher agent: {e}")
            print("📝 System will use fallback dispatcher logic")
            return False
    
    def analyze_conversation(self, conversation_history):
        """
        Analyze conversation and generate dispatch summary
        
        Args:
            conversation_history: List of (role, text) tuples
            
        Returns:
            Dictionary with location, disaster_type, units, and analysis
        """
        # Extract information
        location = extract_location_from_conversation(conversation_history)
        disaster_types = extract_disaster_type_from_conversation(conversation_history)
        
        # Update state
        self.state["location"] = location
        self.state["disaster_type"] = disaster_types
        
        # Find responders
        available_responders = find_available_responders(location, disaster_types)
        self.state["dispatched_units"] = available_responders
        
        # Generate analysis
        if self.agent:
            analysis = self._generate_ai_analysis(conversation_history, location, 
                                                  disaster_types, available_responders)
        else:
            analysis = self._generate_fallback_analysis(location, disaster_types, 
                                                        available_responders)
        
        return {
            "location": location,
            "disaster_type": disaster_types,
            "dispatched_units": available_responders,
            "analysis": analysis
        }
    
    def _generate_ai_analysis(self, conversation_history, location, 
                             disaster_types, available_responders):
        """Generate analysis using AI model"""
        conversation_summary = "\n".join([
            f"{'User' if role == 'user' else 'Dispatcher'}: {text}"
            for role, text in conversation_history[-4:]
        ])
        
        prompt = f"""Analyze this emergency call and provide a brief dispatch summary:

Conversation:
{conversation_summary}

Location identified: {location if location else "Not yet identified"}
Emergency type: {', '.join(disaster_types) if disaster_types else "Unknown"}
Available responders: {len(available_responders)} units

Provide a brief professional dispatch message (2-3 sentences)."""
        
        try:
            response = self.agent(prompt, max_length=150, do_sample=True, temperature=0.7)
            return response[0]['generated_text']
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return self._generate_fallback_analysis(location, disaster_types, 
                                                    available_responders)
    
    def _generate_fallback_analysis(self, location, disaster_types, available_responders):
        """Generate analysis without AI model"""
        if location and available_responders:
            responder_names = [r["name"] for r in available_responders[:2]]
            return (f"Location confirmed: {location.title()}. "
                   f"Emergency type: {', '.join(disaster_types)}. "
                   f"Dispatching {len(available_responders)} units including "
                   f"{', '.join(responder_names)}. ETA: {available_responders[0]['eta']}.")
        elif location:
            return (f"Location identified: {location.title()}. "
                   f"Emergency type: {', '.join(disaster_types)}. "
                   f"Searching for available responders in the area.")
        else:
            return ("Analyzing conversation. Waiting for location confirmation "
                   "to dispatch appropriate emergency responders.")
    
    def reset_state(self):
        """Reset dispatcher state"""
        self.state = {
            "location": None,
            "disaster_type": None,
            "dispatched_units": []
        }