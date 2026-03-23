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
                        radius_km: float = 10,
                        city: str = None) -> Tuple[bool, float]:
        """
        Determine if a news/weather event is relevant to a specific hotel.

        Strategy:
          1. If the article explicitly mentions a distance in km, use that.
          2. If a city name is provided, require it to appear in the article text
             (prevents country-wide articles being assigned to every hotel).
          3. City-named events are treated as city-centre distance (5 km).

        Returns:
            Tuple of (is_within_radius, estimated_distance_km)
        """
        import re
        event_content = f"{event_title} {event_desc}".lower()

        # 1. Explicit km distance mentioned in article
        distance_match = re.search(r'(\d+(?:\.\d+)?)\s*km', event_content)
        if distance_match:
            distance = float(distance_match.group(1))
            return distance <= radius_km, distance

        # 2. City-specific check — article must mention the hotel's city
        if city:
            city_lower = city.lower()
            if city_lower not in event_content:
                # Article doesn't mention this city — not relevant to this hotel
                return False, 999.0
            # City mentioned → treat as city-centre event
            return True, 5.0

        # 3. Fallback for weather alerts (always city-specific via lat/lon)
        return True, 0.0
