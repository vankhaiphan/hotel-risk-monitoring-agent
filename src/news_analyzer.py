import requests
from datetime import datetime, timedelta
from typing import List, Dict
from src.config import NEWS_API_KEY, EVENT_LOOKBACK_HOURS

class NewsAnalyzer:
    """Analyzes news articles for hotel-related risks."""
    
    def __init__(self):
        self.api_key = NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2/everything"
        self.lookback_hours = EVENT_LOOKBACK_HOURS
    
    def search_news(self, query: str, from_date: str = None) -> List[Dict]:
        """
        Search for news articles using News API.
        
        Args:
            query: Search query (hotel name, city, keywords)
            from_date: ISO date string, defaults to lookback_hours ago
        
        Returns:
            List of news articles
        """
        if not self.api_key or self.api_key == 'your_newsapi_key_here':
            print("⚠️  Warning: NEWS_API_KEY not configured. Using mock data.")
            return self._get_mock_data()
        
        if not from_date:
            from_date = (datetime.utcnow() - timedelta(hours=self.lookback_hours)).isoformat()
        
        params = {
            'q': query,
            'from': from_date,
            'sortBy': 'publishedAt',
            'apiKey': self.api_key,
            'language': 'en',
            'pageSize': 50
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'ok':
                print(f"News API Error: {data.get('message', 'Unknown error')}")
                return []
            
            return data.get('articles', [])
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching news: {e}")
            return []
    
    def search_hotel_risks(self, hotel_name: str, city: str, country: str) -> List[Dict]:
        """
        Search for risks specific to a hotel.
        """
        search_queries = [
            f'"{hotel_name}"',
            f'{hotel_name} incident',
        ]
        
        all_articles = []
        for query in search_queries:
            articles = self.search_news(query)
            all_articles.extend(articles)
        
        return self._deduplicate_articles(all_articles)
    
    def search_city_risks(self, city: str, country: str) -> List[Dict]:
        """
        Search for risks affecting the city around the hotel.
        """
        search_queries = [
            f'{city} earthquake',
            f'{city} hurricane',
            f'{city} flood',
            f'{city} riot',
            f'{city} shooting',
            f'{city} evacuation',
            f'{city} airport closure',
            f'{city} fire',
        ]
        
        all_articles = []
        for query in search_queries:
            articles = self.search_news(query)
            all_articles.extend(articles)
        
        return self._deduplicate_articles(all_articles)
    
    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles."""
        seen = set()
        unique = []
        
        for article in articles:
            url = article.get('url', '')
            if url not in seen:
                seen.add(url)
                unique.append(article)
        
        return unique
    
    def _get_mock_data(self) -> List[Dict]:
        """Return mock news data for testing."""
        mock_events = [
            {
                'title': 'Natural Disaster Alert: Earthquake in Budapest Region',
                'description': 'A 5.2 magnitude earthquake was detected 8km south of Budapest',
                'url': 'https://example.com/earthquake-budapest',
                'publishedAt': datetime.utcnow().isoformat(),
                'source': {'name': 'Global News Network'}
            },
            {
                'title': 'Hurricane Maria Intensifies Approaching Caribbean',
                'description': 'Category 4 hurricane approaching Cancun area. Tourist areas evacuation ordered.',
                'url': 'https://example.com/hurricane-maria',
                'publishedAt': datetime.utcnow().isoformat(),
                'source': {'name': 'Weather Alert Network'}
            },
            {
                'title': 'Bangkok Airport Closure Extended Due to Flooding',
                'description': 'Suvarnabhumi Airport remains closed. All flights suspended indefinitely.',
                'url': 'https://example.com/bangkok-airport',
                'publishedAt': datetime.utcnow().isoformat(),
                'source': {'name': 'Thai News Agency'}
            }
        ]
        return mock_events
