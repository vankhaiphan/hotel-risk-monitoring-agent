import json
from datetime import datetime
from typing import List, Dict
from src.news_analyzer import NewsAnalyzer
from src.weather_analyzer import WeatherAnalyzer
from src.risk_classifier import RiskClassifier
from src.proximity import ProximityCalculator
from src.alerter import Alerter
from src.config import HOTELS_FILE, MAX_ALERTS_PER_RUN

class HotelRiskMonitoringAgent:
    """Main agent that monitors and alerts on hotel risks."""
    
    def __init__(self):
        self.weather_analyzer = WeatherAnalyzer()
        self.news_analyzer = NewsAnalyzer()
        self.risk_classifier = RiskClassifier()
        self.proximity_calc = ProximityCalculator()
        self.alerter = Alerter()
        self.hotels = self._load_hotels()
    
    def _load_hotels(self) -> List[Dict]:
        """Load hotel list from configuration."""
        try:
            with open(HOTELS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading hotels: {e}")
            return []
    
    def run_monitoring(self) -> bool:
        """
        Execute daily monitoring cycle.
        
        Returns:
            True if execution was successful
        """
        print(f"\n{'='*70}")
        print(f"Hotel Risk Monitoring Agent - Run Started")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"{'='*70}\n")
        
        all_alerts = []
        
        for hotel in self.hotels:
            print(f"Processing: {hotel['name']} ({hotel['city']}, {hotel['country']})...")
            
            alerts = self._analyze_hotel(hotel)
            all_alerts.extend(alerts)
            
            if len(alerts) > 0:
                print(f"  ✓ Found {len(alerts)} alert(s)")
            else:
                print(f"  ✓ No high-risk events")
        
        # Limit to MAX_ALERTS_PER_RUN
        if len(all_alerts) > MAX_ALERTS_PER_RUN:
            print(f"\n⚠️  Limiting alerts to {MAX_ALERTS_PER_RUN} (found {len(all_alerts)})")
            all_alerts = all_alerts[:MAX_ALERTS_PER_RUN]
        
        # Send alerts
        print(f"\n{'='*70}")
        if all_alerts:
            print(f"Summary: {len(all_alerts)} high-risk event(s) detected")
            self.alerter.send_alerts(all_alerts)
        else:
            print("Summary: NO_ALERT - No high-risk events detected")
        
        print(f"{'='*70}\n")
        
        return True
    
    def _analyze_hotel(self, hotel: Dict) -> List[Dict]:
        """
        Analyze a single hotel for weather risks only.
        Skips news API calls, uses weather/disaster data.
        
        Returns:
            List of high-risk alerts for this hotel
        """
        alerts = []
        
        # DISABLED: News API calls - Skip hotel-specific and city news searches
        # Instead, use only weather/disaster alerts from OpenWeatherMap API
        weather_articles = self._get_weather_alerts(
            hotel['city'],
            hotel['country'],
            hotel['lat'],
            hotel['lon'],
            hotel['name']
        )
        
        # Classify and filter events
        for article in weather_articles:
            risk_event = self.risk_classifier.classify_event(article, hotel['name'])
            
            if risk_event:
                # Check proximity
                within_radius, distance = self.proximity_calc.is_within_radius(
                    hotel['lat'],
                    hotel['lon'],
                    risk_event['title'],
                    risk_event['description']
                )
                
                if within_radius:
                    # Generate impact assessment
                    impact = self._generate_impact_assessment(
                        risk_event['event_type'],
                        hotel['name'],
                        hotel['city'],
                        distance
                    )
                    
                    alert = {
                        'hotel_name': hotel['name'],
                        'city': hotel['city'],
                        'country': hotel['country'],
                        'lat': hotel['lat'],
                        'lon': hotel['lon'],
                        'title': risk_event['title'],
                        'description': risk_event['description'],
                        'event_type': risk_event['event_type'],
                        'severity': risk_event['severity'],
                        'distance': distance,
                        'impact_assessment': impact,
                        'source': risk_event['source'],
                        'published_at': risk_event['published_at'],
                        'url': risk_event['url'],
                        'confidence': risk_event['confidence']
                    }
                    
                    alerts.append(alert)
        
        # Rank alerts by confidence
        alerts = self.risk_classifier.filter_and_rank(alerts)
        
        return alerts
    
    def _get_weather_alerts(self, city: str, country: str, lat: float, lon: float, hotel_name: str) -> List[Dict]:
        """
        Get real weather alerts from OpenWeatherMap API.
        """
        # Get real weather alerts from OpenWeatherMap
        weather_alerts = self.weather_analyzer.get_weather_alerts(lat, lon, hotel_name)
        
        return weather_alerts
    
    def _generate_impact_assessment(self, event_type: str, hotel_name: str, 
                                   city: str, distance: float) -> str:
        """
        Generate a human-readable impact assessment.
        """
        proximity_desc = "at the hotel" if distance < 1 else f"{distance:.1f} km away"
        
        impact_templates = {
            'natural_disaster': (
                f"Natural disaster event {proximity_desc} poses immediate safety risk to guests "
                f"and staff. May require evacuation, operational disruption, and potential "
                f"infrastructure damage. Recommend activating emergency protocols."
            ),
            'civil_unrest': (
                f"Civil unrest event {proximity_desc} may affect guest safety, travel routes, "
                f"and hotel accessibility. Recommend enhanced security, guest communication, "
                f"and monitoring of situation escalation."
            ),
            'security_incident': (
                f"Security incident {proximity_desc} poses direct safety concern. Recommend "
                f"immediate review of hotel security protocols, guest notification procedures, "
                f"and coordination with local authorities."
            ),
            'hotel_incident': (
                f"Incident at hotel {proximity_desc}. Direct impact on hotel operations, "
                f"guest safety, and reputation. Recommend immediate escalation to management "
                f"and coordination with emergency services."
            ),
            'transport_disruption': (
                f"Transport disruption {proximity_desc} affects guest arrivals, departures, "
                f"and accessibility. Recommend adjusting check-in policies, communicating with "
                f"guests, and preparing alternative transportation options."
            ),
            'unknown': (
                f"Potential risk event {proximity_desc}. Recommend monitoring situation "
                f"and taking appropriate precautionary measures."
            )
        }
        
        return impact_templates.get(event_type, impact_templates['unknown'])


def main():
    """Run the monitoring agent."""
    agent = HotelRiskMonitoringAgent()
    agent.run_monitoring()


if __name__ == '__main__':
    main()
