"""Web search functionality using Tavily and Gemini"""

import os
import json
from tavily import TavilyClient
import google.generativeai as genai
from typing import List, Dict


class WebSearchAgent:
    """Agent for searching disaster-related information"""
    
    def __init__(self, tavily_api_key: str, gemini_api_key: str):
        self.tavily = TavilyClient(api_key=tavily_api_key)
        genai.configure(api_key=gemini_api_key)
        print(f"🔑 Configuring Gemini with API key: {gemini_api_key[:10]}...")
        self.gemini_model = genai.GenerativeModel("gemini-2.5-flash")
        
        print("🧪 Testing Gemini connection...")
        try:
            test_response = self.gemini_model.generate_content("Say 'Hello'")
            print(f"✅ Gemini test successful: {test_response.text}")
        except Exception as e:
            print(f"❌ Gemini test failed: {e}")
    
    def extract_search_query(self, conversation_history: List[tuple]) -> Dict:
        """
        Use Gemini to extract key information from conversation
        and generate optimized search queries.
        
        Args:
            conversation_history: List of (role, content) tuples
            
        Returns:
            Dictionary with primary and secondary queries
        """
        print(f"🔍 DEBUG: Conversation history length: {len(conversation_history)}")
        
        if not conversation_history:
            print("⚠️ WARNING: Empty conversation history")
            return {"primary": "", "secondary": [], "error": "No conversation history"}
        
        # Format conversation for Gemini
        conversation_text = "\n".join(
            f"{role.upper()}: {content}" for role, content in conversation_history
        )
        
        print(f"🔍 DEBUG: Formatted conversation:\n{conversation_text}\n")
        
        # Ask Gemini for strict JSON output to make parsing robust
        prompt = f"""
You are an assistant helping to construct web search queries for emergency or disaster situations.

Analyze the following conversation between a caller and a dispatcher and extract:
- A single PRIMARY query (5–10 words) summarizing the main information need.
- 2–3 SECONDARY queries with related, more specific information needs.

Conversation:
{conversation_text}

Respond **ONLY** with a single JSON object with this exact structure, no extra text:
{{
  "primary": "single primary search query here",
  "secondary": [
    "secondary query 1",
    "secondary query 2"
  ]
}}
"""
        
        try:
            print(f"🔍 DEBUG: Sending request to Gemini model: {self.gemini_model._model_name}")
            
            response = self.gemini_model.generate_content(prompt)
            response_text = response.text.strip()
            
            print(f"🔍 DEBUG: Raw Gemini response:\n{response_text}\n")

            # Clean up optional markdown code fences that Gemini may add
            cleaned = response_text
            if cleaned.startswith("```"):
                # Drop leading ``` or ```json
                first_newline = cleaned.find("\n")
                if first_newline != -1:
                    cleaned = cleaned[first_newline + 1 :]
                # Drop trailing ```
                if "```" in cleaned:
                    cleaned = cleaned.rsplit("```", 1)[0]
                cleaned = cleaned.strip()
                print(f"🔍 DEBUG: Cleaned Gemini response (code fences removed):\n{cleaned}\n")
            else:
                cleaned = cleaned.strip()

            queries = {"primary": "", "secondary": []}

            try:
                parsed = json.loads(cleaned)
                print(f"🔍 DEBUG: Parsed JSON from Gemini: {parsed}")

                primary = (
                    parsed.get("primary")
                    or parsed.get("PRIMARY")
                    or parsed.get("PRIMARY_QUERY")
                    or parsed.get("primary_query")
                )
                secondary = (
                    parsed.get("secondary")
                    or parsed.get("SECONDARY")
                    or parsed.get("SECONDARY_QUERIES")
                    or parsed.get("secondary_queries")
                )

                if isinstance(primary, str):
                    queries["primary"] = primary.strip()
                if isinstance(secondary, str):
                    secondary = [secondary]
                if isinstance(secondary, list):
                    # Filter out empty / whitespace-only entries
                    queries["secondary"] = [s.strip() for s in secondary if isinstance(s, str) and s.strip()]

            except json.JSONDecodeError as je:
                print(f"⚠️ WARNING: Failed to parse Gemini response as JSON: {je}")
                # Fallback to previous line-based parsing to avoid total failure
                lines = cleaned.splitlines()
                for line in lines:
                    line = line.strip()
                    if line.lower().startswith("primary_query:") or line.lower().startswith("primary:"):
                        queries["primary"] = line.split(":", 1)[1].strip()
                        print(f"✅ Fallback extracted primary query: {queries['primary']}")
                    elif line.startswith("- "):
                        secondary_query = line.replace("- ", "").strip()
                        if secondary_query:
                            queries["secondary"].append(secondary_query)
                            print(f"✅ Fallback extracted secondary query: {secondary_query}")

                if not queries["primary"] and lines:
                    # Last-resort heuristic: take the first non-empty line as primary
                    for line in lines:
                        if line.strip():
                            queries["primary"] = line.strip()
                            print(f"✅ Heuristic primary query: {queries['primary']}")
                            break

            if not queries["primary"]:
                print("⚠️ WARNING: No primary query extracted from Gemini response after all parsing attempts")

            return queries
        
        except Exception as e:
            print(f"❌ ERROR in extract_search_query: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"primary": "", "secondary": [], "error": str(e)}
    
    def search_disaster_query(self, query: str, max_results: int = 5) -> Dict:
        """
        Search for disaster-related information using Tavily.
        
        Args:
            query: The search query
            max_results: Maximum number of results to return
        
        Returns:
            Search results with relevant information
        """
        try:
            response = self.tavily.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=True,
                include_raw_content=False,
                include_images=False
            )

            # DEBUG: log raw Tavily response structure
            try:
                print(f"🔎 DEBUG: Tavily response for '{query}': {response}")
            except Exception:
                pass

            # Normalize shape so frontend always has a predictable structure
            if isinstance(response, dict):
                # Some Tavily variants may use different keys; ensure "answer" exists
                if not response.get("answer"):
                    # Try common alternative keys
                    alt_answer = (
                        response.get("summary")
                        or response.get("overview")
                        or response.get("response")
                    )
                    if alt_answer:
                        response["answer"] = alt_answer
                    elif response.get("results"):
                        # Fallback: synthesize a brief summary from top result titles
                        titles = [
                            r.get("title")
                            for r in response.get("results", [])
                            if isinstance(r, dict) and r.get("title")
                        ]
                        if titles:
                            response["answer"] = "Top sources:\n" + "\n".join(
                                f"- {t}" for t in titles[:3]
                            )
                        else:
                            response.setdefault("answer", "")
                # Ensure "results" key exists for frontend
                response.setdefault("results", [])

            return response
        
        except Exception as e:
            print(f"Search error: {e}")
            return {"error": str(e), "results": [], "answer": ""}
    
    def process_conversation(self, conversation_history: List[tuple], 
                           search_all: bool = True) -> Dict:
        """
        Complete pipeline: Extract queries and perform searches.
        
        Args:
            conversation_history: List of (role, content) tuples
            search_all: If True, search all queries; if False, only primary
        
        Returns:
            All queries and search results
        """
        # Extract queries
        queries = self.extract_search_query(conversation_history)
        
        if not queries.get("primary"):
            return {
                "queries": queries,
                "primary_results": {"results": [], "answer": ""},
                "secondary_results": [],
                "error": "Could not extract search queries"
            }
        
        # Search primary query
        primary_results = self.search_disaster_query(queries["primary"])
        # print(primary_results)
        results = {
            "queries": queries,
            "primary_results": primary_results,
            "secondary_results": []
        }
        
        # Optionally search secondary queries
        if search_all and queries.get("secondary"):
            for query in queries["secondary"]:
                secondary_result = self.search_disaster_query(query, max_results=3)
                # print(secondary_result,"\n")
                results["secondary_results"].append({
                    "query": query,
                    "results": secondary_result
                })
        
        return results