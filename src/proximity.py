from math import radians, cos, sin, asin, sqrt
from typing import Tuple

class ProximityCalculator:
    """Calculate distance between hotel and event location."""
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points 
        on the earth (specified in decimal degrees).
        
        Returns distance in kilometers.
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        
        return c * r
    
    def is_within_radius(self, hotel_lat: float, hotel_lon: float, 
                        event_title: str, event_desc: str, 
                        radius_km: float = 10) -> Tuple[bool, float]:
        """
        Determine if event is within search radius.
        
        For now, uses title/description matching to detect if event 
        is near the location. In production, could use geocoding.
        
        Returns:
            Tuple of (is_within_radius, estimated_distance)
        """
        # If event mentions the specific address/coordinates, assume it's relevant
        event_content = f"{event_title} {event_desc}".lower()
        
        # Extract distance if mentioned in article
        import re
        distance_match = re.search(r'(\d+(?:\.\d+)?)\s*km', event_content)
        if distance_match:
            distance = float(distance_match.group(1))
            return distance <= radius_km, distance
        
        # If specific location mentioned and within typical city radius, assume within range
        within_city_phrases = [
            'downtown', 'city center', 'near', 'nearby', 
            'downtown area', 'city limits', 'kilometers away'
        ]
        
        for phrase in within_city_phrases:
            if phrase in event_content:
                # Assume 5 km average for city-based incidents
                return True, 5.0
        
        # Default: assume it's relevant if article exists
        # (More sophisticated geocoding can be added later)
        return True, 0.0
