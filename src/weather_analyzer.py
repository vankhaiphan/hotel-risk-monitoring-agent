import requests
from typing import List, Dict
from datetime import datetime
from src.config import WEATHER_API_KEY

class WeatherAnalyzer:
    """Analyzes weather alerts from OpenWeatherMap API."""
    
    def __init__(self):
        self.api_key = WEATHER_API_KEY
        self.owm_alerts_url = "https://api.openweathermap.org/data/3.0/alerts"
        self.owm_weather_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather_alerts(self, lat: float, lon: float, hotel_name: str) -> List[Dict]:
        """
        Get severe weather alerts for a specific location.
        Uses OpenWeatherMap free tier current weather endpoint to detect extreme conditions.
        
        Args:
            lat: Hotel latitude
            lon: Hotel longitude
            hotel_name: Hotel name for context
        
        Returns:
            List of weather alert objects
        """
        if not self.api_key or self.api_key == 'your_openweathermap_key_here':
            print(f"⚠️  Warning: WEATHER_API_KEY not configured")
            return []
        
        try:
            # Get current weather for extreme conditions (free tier endpoint)
            weather_data = self._get_current_weather(lat, lon)
            
            return self._normalize_alerts(weather_data, hotel_name)
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather alerts: {e}")
            return []
    
    def _get_current_weather(self, lat: float, lon: float) -> List[Dict]:
        """Get current weather and detect extreme conditions."""
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.owm_weather_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            extreme_alerts = []
            
            # Check for extreme conditions
            main = data.get('main', {})
            weather = data.get('weather', [{}])[0]
            wind = data.get('wind', {})
            
            temp = main.get('temp', 0)
            feels_like = main.get('feels_like', 0)
            wind_speed = wind.get('speed', 0)
            condition = weather.get('main', '')
            description = weather.get('description', '')
            
            # Detect extreme weather
            if wind_speed > 25:  # >90 km/h is hurricane force
                extreme_alerts.append({
                    'title': f'Extreme Wind Alert: {wind_speed} m/s ({wind_speed * 3.6:.1f} km/h)',
                    'description': f'Extremely strong winds detected. Potential hurricane/cyclone conditions.',
                    'event': 'wind_alert'
                })
            
            if condition.lower() in ['thunderstorm', 'tornado', 'squall']:
                extreme_alerts.append({
                    'title': f'Severe Storm Alert: {description.title()}',
                    'description': f'Severe {description} warning in effect. Take shelter.',
                    'event': 'storm_alert'
                })
            
            if temp < -20 or feels_like < -20:
                extreme_alerts.append({
                    'title': f'Extreme Cold Alert: {temp}°C',
                    'description': f'Extreme cold warning. Temperature at {temp}°C.',
                    'event': 'cold_alert'
                })
            
            if temp > 45 or feels_like > 45:
                extreme_alerts.append({
                    'title': f'Extreme Heat Alert: {temp}°C',
                    'description': f'Extreme heat warning. Temperature at {temp}°C.',
                    'event': 'heat_alert'
                })
            
            if condition.lower() in ['rain', 'drizzle']:
                # Check if heavy rain
                rain = data.get('rain', {})
                if rain.get('1h', 0) > 50:  # >50mm/hour is extreme
                    extreme_alerts.append({
                        'title': f'Extreme Rainfall Alert: {rain.get("1h", 0)}mm/hour',
                        'description': f'Flash flood risk. Heavy rainfall detected.',
                        'event': 'flood_alert'
                    })
            
            return extreme_alerts
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching current weather: {e}")
            return []
    
    def _normalize_alerts(self, alerts: List[Dict], hotel_name: str) -> List[Dict]:
        """Normalize OpenWeatherMap alerts to standard format."""
        normalized = []
        current_time = datetime.utcnow().isoformat() + 'Z'
        
        for alert in alerts:
            # Handle both API alert format and extreme weather format
            if 'event' in alert:
                # Extreme weather detected
                normalized.append({
                    'title': alert['title'],
                    'description': alert['description'],
                    'url': '',
                    'publishedAt': current_time,
                    'source': {'name': 'OpenWeatherMap'},
                    'event_type': alert.get('event', 'weather')
                })
            else:
                # Standard API alert format
                normalized.append({
                    'title': alert.get('event', 'Weather Alert'),
                    'description': alert.get('description', ''),
                    'url': '',
                    'publishedAt': alert.get('start', current_time),
                    'source': {'name': 'OpenWeatherMap'},
                    'event_type': 'weather_alert'
                })
        
        return normalized
