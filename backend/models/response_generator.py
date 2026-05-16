"""Response generation - supports both LoRA and Gemini"""

import torch
from utils.conversation_utils import infer_image_damage_and_info


class ResponseGenerator:
    """Generates dispatcher responses using LoRA model"""
    
    def __init__(self, model, tokenizer, config):
        self.model = model
        self.tokenizer = tokenizer
        self.config = config
    
    def generate_response(self, user_input, retrieved_results, conversation_history, 
                         web_search_summary=None):
        """
        Generate dispatcher response
        
        Args:
            user_input: Current user message
            retrieved_results: List of retrieved crisis data
            conversation_history: Recent conversation history
            web_search_summary: Optional web search summary
            
        Returns:
            Generated response string
        """
        if self.model is None or self.tokenizer is None:
            return self._generate_fallback_response(user_input, conversation_history)
        
        # Format context
        context_block = self._format_retrieved_context(retrieved_results)
        hist_text = self._format_conversation_history(conversation_history)
        
        # Build prompt
        prompt = self._build_prompt(user_input, context_block, hist_text, web_search_summary)
        
        # Generate
        try:
            inputs = self.tokenizer([prompt], return_tensors="pt").to(self.config.DEVICE)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=256,
                    use_cache=True,
                    do_sample=True,
                    temperature=0.7,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            raw = self.tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
            
            if "### response:" in raw:
                return raw.split("### response:")[1].strip()
            return raw.strip()
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return self._generate_fallback_response(user_input, conversation_history)
    
    def _format_retrieved_context(self, retrieved_results):
        """Format retrieved results for prompt"""
        context_blocks = []
        for i, r in enumerate(retrieved_results, start=1):
            tweet = (r.get("tweet_text","") or "").strip()
            cap = (r.get("image_caption","") or "").strip()
            
            tweet_short = (tweet[:self.config.MAX_ITEM_CHARS] + 
                          ("…" if len(tweet) > self.config.MAX_ITEM_CHARS else ""))
            cap_short = (cap[:self.config.MAX_ITEM_CHARS] + 
                        ("…" if len(cap) > self.config.MAX_ITEM_CHARS else ""))
            
            damage, info = infer_image_damage_and_info(r)
            
            block = (
                f"Item {i}:\n"
                f" tweet_id: {r.get('tweet_id','')}\n"
                f" image_id: {r.get('image_id','')}\n"
                f" image_damage: {damage}\n"
                f" image_info: {info}\n"
                f" tweet_text: {tweet_short}\n"
                f" image_caption: {cap_short}\n"
                f" retrieval_score: {r.get('score', 0):.4f}\n"
            )
            context_blocks.append(block)
        
        return "\n".join(context_blocks) if context_blocks else "No retrieved items."
    
    def _format_conversation_history(self, conversation_history):
        """Format conversation history for prompt"""
        hist_snippet = []
        for role, text in conversation_history[-self.config.HISTORY_TURNS:]:
            prefix = "User:" if role == "user" else "Assistant:"
            hist_snippet.append(f"{prefix} {text}")
        return "\n".join(hist_snippet) if hist_snippet else "[no earlier turns]"
    
    def _build_prompt(self, user_input, context_block, hist_text, web_search_summary):
        """Build complete prompt for model"""
        instruction = (
            "You are a professional 911 dispatcher. You have access to historical crisis data and conversation history. "
            "IMPORTANT: Read and use the retrieved context and conversation history to provide relevant, progressive responses. "
            "Do NOT repeat the same questions. Build on what the caller has already told you. "
            "If the caller has provided location information, acknowledge it and ask for the next most critical details "
            "(exact address/landmarks, number of people involved, injuries, immediate dangers, escape routes). "
            "Be efficient, calm, and move the conversation forward to dispatch appropriate help."
        )
        
        conversation_input_parts = [
            f"CONVERSATION HISTORY - READ THIS CAREFULLY:\n{hist_text}\n\n",
            "RETRIEVED CRISIS CONTEXT:\n",
            f"{context_block}\n\n"
        ]
        
        if web_search_summary:
            conversation_input_parts.append(
                f"REAL-TIME WEB SEARCH INFORMATION:\n{web_search_summary}\n\n"
            )
        
        conversation_input_parts.extend([
            "CURRENT USER MESSAGE:\n",
            f"{user_input}\n\n",
            "CRITICAL INSTRUCTIONS: This is a continuing conversation. The user has already provided information above. ",
            "Do NOT ask questions they've already answered. Progress the conversation by asking for the next most important details needed for dispatch."
        ])
        
        conversation_input = "".join(conversation_input_parts)
        
        return (
            "Below is an instruction that describes a task, paired with an input that provides further context. "
            "Write a response that appropriately completes the request.\n\n"
            f"### instruction:\n{instruction}\n\n"
            f"### input:\n{conversation_input}\n\n"
            "### response:\n"
        )
    
    def _generate_fallback_response(self, user_input, conversation_history):
        """Generate rule-based response when model isn't available"""
        user_lower = user_input.lower()
        
        location_keywords = ["in", "at", "near", "on", "street", "road", "avenue", "boulevard"]
        has_location = any(keyword in user_lower for keyword in location_keywords)
        
        location_provided = any(
            "location" in turn[1].lower() or 
            any(loc in turn[1].lower() for loc in ["california", "street", "road", "avenue"])
            for turn in conversation_history if turn[0] == "user"
        )
        
        if not location_provided and not has_location:
            return "911, I need to know your exact location. What's your address or the nearest cross streets?"
        
        if "fire" in user_lower:
            return "I'm dispatching fire and rescue to your location. Are you in immediate danger? Do you have a safe evacuation route?"
        
        return "I'm getting help to you right away. Stay on the line and provide any additional information about your situation."