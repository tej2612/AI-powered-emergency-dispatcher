"""Gemini-based dispatcher response generator"""

import google.generativeai as genai
from typing import List, Tuple, Dict, Optional


class GeminiDispatcher:
    """Generate dispatcher responses using Gemini API"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini dispatcher
        
        Args:
            api_key: Google API key
            model_name: Gemini model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        print(f"✅ Gemini Dispatcher initialized with {model_name}")
    
    def generate_response(self, user_input: str, retrieved_results: List[Dict], 
                         conversation_history: List[Tuple], 
                         web_search_summary: Optional[str] = None) -> str:
        """
        Generate dispatcher response using Gemini
        
        Args:
            user_input: Current user message
            retrieved_results: List of retrieved crisis data
            conversation_history: Recent conversation history
            web_search_summary: Optional summary from web search
            
        Returns:
            Generated dispatcher response
        """
        # Format retrieved context
        context_block = self._format_retrieved_context(retrieved_results)
        
        # Format conversation history
        hist_text = self._format_conversation_history(conversation_history)
        
        # Build prompt
        prompt = self._build_prompt(user_input, context_block, hist_text, web_search_summary)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating Gemini response: {e}")
            return self._generate_fallback_response(user_input, conversation_history)
    
    def _format_retrieved_context(self, retrieved_results: List[Dict], max_chars: int = 400) -> str:
        """Format retrieved crisis data for prompt"""
        if not retrieved_results:
            return "No retrieved crisis data available."
        
        context_blocks = []
        for i, r in enumerate(retrieved_results[:3], start=1):  # Limit to top 3
            tweet = (r.get("tweet_text", "") or "").strip()
            disaster_type = r.get("disaster_type", "Unknown")
            location = r.get("extracted_location", "Unknown")
            
            tweet_short = tweet[:max_chars] + ("..." if len(tweet) > max_chars else "")
            
            block = (
                f"Crisis Report {i}:\n"
                f"  Type: {disaster_type}\n"
                f"  Location: {location}\n"
                f"  Report: {tweet_short}\n"
            )
            context_blocks.append(block)
        
        return "\n".join(context_blocks)
    
    def _format_conversation_history(self, conversation_history: List[Tuple], 
                                     history_turns: int = 6) -> str:
        """Format conversation history for prompt"""
        if not conversation_history:
            return "[No previous conversation]"
        
        hist_snippet = []
        for role, text in conversation_history[-history_turns:]:
            prefix = "Caller:" if role == "user" else "Dispatcher:"
            hist_snippet.append(f"{prefix} {text}")
        
        return "\n".join(hist_snippet)
    
    def _build_prompt(self, user_input: str, context_block: str, 
                     hist_text: str, web_search_summary: Optional[str]) -> str:
        """Build complete prompt for Gemini"""
        
        # Base instruction
        instruction = """You are a professional 911 dispatcher handling an emergency call. Your goals are to:
1. Stay calm, clear, and reassuring
2. Gather critical information (location, injuries, immediate dangers)
3. Provide actionable guidance based on the situation
4. Do NOT repeat questions already answered in the conversation history
5. Progress the conversation efficiently toward dispatching help

Important: Build on what the caller has already told you. If they've provided their location, acknowledge it and ask for the next most critical details."""
        
        # Build the full prompt
        prompt_parts = [
            instruction,
            "\n--- CONVERSATION HISTORY ---",
            hist_text,
            "\n--- SIMILAR CRISIS REPORTS (Historical Data) ---",
            context_block
        ]
        
        # Add web search summary if available
        if web_search_summary:
            prompt_parts.extend([
                "\n--- REAL-TIME WEB SEARCH INFORMATION ---",
                web_search_summary,
                "\nUse this real-time information to provide current, accurate guidance."
            ])
        
        prompt_parts.extend([
            "\n--- CURRENT CALLER MESSAGE ---",
            user_input,
            "\n--- YOUR RESPONSE ---",
            "Respond as the 911 dispatcher. Be concise, professional, and action-oriented."
        ])
        
        return "\n".join(prompt_parts)
    
    def _generate_fallback_response(self, user_input: str, 
                                    conversation_history: List[Tuple]) -> str:
        """Generate rule-based response if API fails"""
        user_lower = user_input.lower()
        
        # Check if location was provided in history
        location_provided = any(
            "location" in turn[1].lower() or 
            any(loc in turn[1].lower() for loc in ["street", "road", "avenue", "address"])
            for turn in conversation_history if turn[0] == "user"
        )
        
        if not location_provided:
            return "911, what is your exact location? Please provide your address or nearest cross streets."
        
        if "fire" in user_lower:
            return "Help is on the way. Are you in immediate danger? Do you have a safe evacuation route?"
        
        if "injured" in user_lower or "hurt" in user_lower:
            return "Medical assistance is being dispatched. Is the person conscious and breathing?"
        
        return "Stay on the line. Help is being dispatched to your location. Can you provide more details about your situation?"