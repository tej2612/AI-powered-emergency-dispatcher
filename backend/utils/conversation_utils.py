"""Conversation management utilities"""

import re


class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self, history_turns=6):
        self.history = []
        self.history_turns = history_turns
    
    def add_turn(self, role, content):
        """Add a conversation turn"""
        self.history.append((role, content))
    
    def get_recent_history(self):
        """Get recent conversation history as formatted string"""
        hist_snippet = []
        for role, text in self.history[-self.history_turns:]:
            prefix = "User:" if role == "user" else "Assistant:"
            hist_snippet.append(f"{prefix} {text}")
        return "\n".join(hist_snippet) if hist_snippet else "[no earlier turns]"
    
    def clear_history(self):
        """Clear all conversation history"""
        self.history = []
    
    def get_full_history(self):
        """Get full conversation history"""
        return self.history


def extract_location_from_conversation(conversation_history):
    """
    Extract location from conversation history using regex patterns
    
    Args:
        conversation_history: List of (role, text) tuples
        
    Returns:
        Extracted location string or None
    """
    conversation_text = " ".join([turn[1] for turn in conversation_history if turn[0] == "user"])
    
    # Common location patterns
    location_patterns = [
        r"in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        r"at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        r"near\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        r"([A-Z][a-z]+\s+[A-Z][a-z]+),\s*(?:CA|California)"
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, conversation_text)
        if matches:
            location = matches[-1].lower()  # Get the most recent mention
            return location
    
    return None


def extract_disaster_type_from_conversation(conversation_history):
    """
    Extract disaster type from conversation history using keyword matching
    
    Args:
        conversation_history: List of (role, text) tuples
        
    Returns:
        List of detected disaster types
    """
    conversation_text = " ".join([turn[1].lower() for turn in conversation_history if turn[0] == "user"])
    
    disaster_keywords = {
        "fire": [
            "fire", "wildfire", "burning", "flames", "smoke", "blaze",
            "bushfire", "forest fire", "house fire", "structure fire"
        ],
        "medical": [
            "injured", "hurt", "medical", "ambulance", "unconscious",
            "bleeding", "heart attack", "stroke", "breathing", "collapsed",
            "overdose", "seizure", "faint", "burn", "cut"
        ],
        "police": [
            "threat", "violence", "crime", "robbery", "assault", "shooting",
            "theft", "burglary", "fight", "attack", "suspect", "gun", "knife",
            "hostage", "terrorist", "kidnap", "riot", "vandalism"
        ],
        "rescue": [
            "trapped", "stuck", "stranded", "rescue", "collapsed building",
            "pinned", "buried", "cave", "mine", "confined space"
        ],
        "earthquake": [
            "earthquake", "tremor", "aftershock", "seismic", "ground shaking",
            "collapsed building", "quake", "rubble", "fault line"
        ],
        "flood": [
            "flood", "flooding", "overflow", "inundation", "submerged",
            "water rising", "washed away", "dam break", "levee breach", "flash flood"
        ],
        "hurricane": [
            "hurricane", "cyclone", "typhoon", "storm surge", "tropical storm",
            "high winds", "gale", "category 5", "landfall", "eye of the storm"
        ],
        "tornado": [
            "tornado", "twister", "funnel cloud", "windstorm", "touchdown",
            "debris", "rotation", "supercell"
        ],
        "tsunami": [
            "tsunami", "tidal wave", "giant wave", "seawater surge", "undersea quake"
        ],
        "landslide": [
            "landslide", "mudslide", "rockslide", "debris flow", "slope failure",
            "earth slip", "hill collapse"
        ],
        "snowstorm": [
            "snowstorm", "blizzard", "whiteout", "heavy snow", "avalanche",
            "snowed in", "frozen", "ice storm"
        ],
        "drought": [
            "drought", "dry spell", "no rain", "water shortage", "famine", "crop failure"
        ],
        "explosion": [
            "explosion", "blast", "bomb", "detonation", "blast wave", "explosive", "gas leak"
        ],
        "chemical": [
            "chemical spill", "toxic", "hazmat", "hazardous", "gas leak",
            "radiation", "contamination", "biohazard"
        ],
        "transport_accident": [
            "plane crash", "train derailment", "car accident", "bus crash",
            "vehicle collision", "shipwreck", "boat accident", "helicopter crash"
        ],
        "building_collapse": [
            "building collapse", "structure collapse", "roof fell", "bridge collapse"
        ],
        "power_outage": [
            "power outage", "blackout", "no electricity", "power failure"
        ]
    }
    
    detected_types = []
    for disaster_type, keywords in disaster_keywords.items():
        if any(keyword in conversation_text for keyword in keywords):
            detected_types.append(disaster_type)
    
    return detected_types if detected_types else ["emergency"]



def infer_image_damage_and_info(entry):
    """
    Infer damage level and information quality from metadata entry
    
    Args:
        entry: Metadata dictionary
        
    Returns:
        Tuple of (damage_level, info_quality)
    """
    if "image_damage" in entry and entry["image_damage"] is not None:
        damage = entry["image_damage"]
    else:
        text = " ".join([str(entry.get("tweet_text","") or ""), 
                        str(entry.get("image_caption","") or "")]).lower()
        
        high_kw = [
                    "trapped", "on fire", "engulfed", "destroyed", "collapse", "evacuate",
                    "urgent", "immediate", "fatal", "dead", "massive destruction",
                    "completely ruined", "severe damage", "multiple casualties", "devastated",
                    "widespread damage", "catastrophic", "total loss", "building down",
                    "major explosion", "severely injured", "life threatening", "critical condition",
                    "missing persons", "under rubble", "burning intensely", "structure failure",
                    "blocked exits", "panic", "chaos", "major incident", "emergency declared",
                    "disaster", "crumbling", "collapsed structure", "entire area destroyed",
                    "fatalities reported", "serious casualties", "fire out of control",
                    "complete destruction", "total devastation", "significant structural failure",
                    "building leveled", "road washed away", "bridge collapsed"
        ]

        med_kw = [
                    "burn", "burned", "smoke", "injured", "damage", "collapsed",
                    "heavy smoke", "partially destroyed", "serious", "severe", "moderate damage",
                    "some injuries", "partially collapsed", "significant damage",
                    "building cracked", "fire spreading", "visible flames", "strong winds",
                    "minor casualties", "loss of power", "roof damaged", "wall down",
                    "street flooded", "partial evacuation", "hazardous", "unstable structure",
                    "property damage", "broken windows", "fallen debris", "injuries reported",
                    "medium intensity", "some people hurt", "moderate flooding",
                    "sections destroyed", "structural damage", "roads blocked", "trees down"
        ]

        low_kw = [
                    "small", "minor", "contained", "controlled", "smouldering", "smoldering",
                    "under control", "limited", "localized", "light damage", "no injuries",
                    "contained fire", "low intensity", "minor flooding", "slight damage",
                    "no casualties", "safe", "situation stable", "partly controlled",
                    "handled", "manageable", "contained incident", "non-critical",
                    "minor issue", "resolved", "contained quickly", "smoke subsiding",
                    "power restored", "roads cleared", "clean-up ongoing"
        ]

        
        if any(k in text for k in high_kw):
            damage = "HIGH"
        elif any(k in text for k in med_kw):
            damage = "MEDIUM"
        elif any(k in text for k in low_kw):
            damage = "LOW"
        else:
            damage = ""
    
    if "image_info" in entry and entry["image_info"] is not None:
        info = entry["image_info"]
    else:
        cap = (entry.get("image_caption","") or "").strip()
        info = "NOT INFORMATIVE" if len(cap) == 0 else "INFORMATIVE"
    
    return damage, info