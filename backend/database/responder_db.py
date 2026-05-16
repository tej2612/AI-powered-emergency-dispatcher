"""Responder database and query functions"""

RESPONDER_DATABASE = {
    "california": {
        "santa rosa": {
            "fire": [
                {"id": "FR-001", "name": "Santa Rosa Fire Station 1", "units": 3, "eta": "5 mins"},
                {"id": "FR-002", "name": "Santa Rosa Fire Station 2", "units": 2, "eta": "8 mins"}
            ],
            "medical": [
                {"id": "MD-001", "name": "Santa Rosa Medical Unit 1", "units": 2, "eta": "6 mins"}
            ],
            "police": [
                {"id": "PD-001", "name": "Santa Rosa Police Unit 1", "units": 4, "eta": "4 mins"}
            ]
        },
        "sacramento": {
            "fire": [
                {"id": "FR-101", "name": "Sacramento Fire Dept", "units": 5, "eta": "7 mins"}
            ],
            "medical": [
                {"id": "MD-101", "name": "Sacramento EMS", "units": 3, "eta": "5 mins"}
            ],
            "rescue": [
                {"id": "RS-101", "name": "Sacramento Urban Search & Rescue", "units": 2, "eta": "9 mins"}
            ]
        },
        "los angeles": {
            "fire": [
                {"id": "FR-201", "name": "LA Fire Station 5", "units": 4, "eta": "10 mins"},
                {"id": "FR-202", "name": "LA Wildfire Response Unit", "units": 3, "eta": "12 mins"}
            ],
            "medical": [
                {"id": "MD-201", "name": "LA Paramedics", "units": 5, "eta": "8 mins"}
            ],
            "rescue": [
                {"id": "RS-201", "name": "LA County Disaster Rescue", "units": 2, "eta": "11 mins"}
            ]
        },
        "san francisco": {
            "fire": [
                {"id": "FR-301", "name": "SF Fire Department", "units": 6, "eta": "6 mins"}
            ],
            "medical": [
                {"id": "MD-301", "name": "SF Emergency Medical", "units": 4, "eta": "7 mins"}
            ],
            "police": [
                {"id": "PD-301", "name": "SF Police Department", "units": 5, "eta": "5 mins"}
            ]
        }
    },

    "sri lanka": {
        "colombo": {
            "flood": [
                {"id": "FD-001", "name": "Colombo Flood Rescue Unit", "units": 3, "eta": "10 mins"},
                {"id": "FD-002", "name": "Navy Flood Response Team", "units": 2, "eta": "15 mins"}
            ],
            "medical": [
                {"id": "MD-401", "name": "Colombo General Hospital EMS", "units": 3, "eta": "8 mins"}
            ],
            "rescue": [
                {"id": "RS-401", "name": "Sri Lanka Disaster Management Unit", "units": 4, "eta": "12 mins"}
            ]
        },
        "kandy": {
            "flood": [
                {"id": "FD-101", "name": "Kandy Flood Relief Unit", "units": 2, "eta": "9 mins"}
            ],
            "rescue": [
                {"id": "RS-101", "name": "Central Province Rescue Unit", "units": 2, "eta": "10 mins"}
            ]
        }
    },

    "mexico": {
        "mexico city": {
            "earthquake": [
                {"id": "EQ-001", "name": "Mexico City Seismic Response Unit", "units": 5, "eta": "6 mins"},
                {"id": "EQ-002", "name": "Urban Search & Rescue MX-1", "units": 4, "eta": "8 mins"}
            ],
            "medical": [
                {"id": "MD-501", "name": "Mexico City Trauma Response", "units": 3, "eta": "7 mins"}
            ],
            "fire": [
                {"id": "FR-501", "name": "Mexico City Fire Department", "units": 5, "eta": "5 mins"}
            ]
        },
        "puebla": {
            "earthquake": [
                {"id": "EQ-101", "name": "Puebla Seismic Response Team", "units": 3, "eta": "9 mins"}
            ],
            "rescue": [
                {"id": "RS-501", "name": "Puebla Urban Search Unit", "units": 2, "eta": "10 mins"}
            ]
        }
    },

    "india": {
        "mumbai": {
            "flood": [
                {"id": "FD-301", "name": "Mumbai Flood Control Unit", "units": 4, "eta": "8 mins"}
            ],
            "fire": [
                {"id": "FR-401", "name": "Mumbai Fire Brigade", "units": 6, "eta": "5 mins"}
            ],
            "medical": [
                {"id": "MD-601", "name": "Mumbai Emergency Medical Response", "units": 5, "eta": "7 mins"}
            ]
        },
        "delhi": {
            "fire": [
                {"id": "FR-501", "name": "Delhi Fire Service", "units": 7, "eta": "6 mins"}
            ],
            "earthquake": [
                {"id": "EQ-201", "name": "Delhi Seismic Rescue Force", "units": 3, "eta": "9 mins"}
            ],
            "medical": [
                {"id": "MD-701", "name": "Delhi Ambulance Corps", "units": 4, "eta": "5 mins"}
            ]
        }
    }
}



def find_available_responders(location, disaster_types):
    """
    Find available responders based on location and disaster type
    
    Args:
        location: String location name
        disaster_types: List of disaster type strings
        
    Returns:
        List of responder dictionaries
    """
    if not location:
        return []
    
    location_lower = location.lower()
    responders = []
    
    # Search through the database
    for state, cities in RESPONDER_DATABASE.items():
        for city, services in cities.items():
            if city in location_lower or location_lower in city:
                for disaster_type in disaster_types:
                    if disaster_type in services:
                        responders.extend(services[disaster_type])
    
    return responders


def get_all_locations():
    """Get list of all available locations in database"""
    locations = []
    for state, cities in RESPONDER_DATABASE.items():
        for city in cities.keys():
            locations.append(f"{city}, {state}")
    return locations


def get_responder_by_id(responder_id):
    """Get specific responder by ID"""
    for state, cities in RESPONDER_DATABASE.items():
        for city, services in cities.items():
            for service_type, responders in services.items():
                for responder in responders:
                    if responder['id'] == responder_id:
                        return responder
    return None