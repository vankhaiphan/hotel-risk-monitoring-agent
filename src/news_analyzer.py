import feedparser
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from src.config import EVENT_LOOKBACK_HOURS

# Free RSS feeds — no API key, no CORS, works on GitHub Actions
RSS_FEEDS = [
    # Global news
    {"name": "Reuters World", "url": "https://feeds.reuters.com/reuters/worldNews"},
    {"name": "BBC World", "url": "https://feeds.bbci.co.uk/news/world/rss.xml"},
    {"name": "AP News", "url": "https://apnews.com/rss"},
    # Australia-specific
    {"name": "ABC Australia", "url": "https://www.abc.net.au/news/feed/51120/rss.xml"},
    {"name": "ABC Australia World", "url": "https://www.abc.net.au/news/feed/45910/rss.xml"},
    # Asia/Middle East
    {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
]

class NewsAnalyzer:
    """Analyzes RSS news feeds for hotel-related risks. No API key required."""

    def __init__(self):
        self.lookback_hours = EVENT_LOOKBACK_HOURS
        self._feed_cache: Optional[List[Dict]] = None  # cache feeds for one run
    
    def _fetch_all_feeds(self) -> List[Dict]:
        """
        Fetch all RSS feeds once and cache for this run.
        Cost: 6 HTTP requests total regardless of number of hotels.
        """
        if self._feed_cache is not None:
            return self._feed_cache

        cutoff = datetime.now(timezone.utc) - timedelta(hours=self.lookback_hours)
        articles = []

        for feed_info in RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_info["url"])
                for entry in feed.entries:
                    published = self._parse_date(entry)
                    if published and published < cutoff:
                        continue  # too old

                    articles.append({
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', entry.get('description', '')),
                        'url': entry.get('link', ''),
                        'publishedAt': published.isoformat() if published else datetime.now(timezone.utc).isoformat(),
                        'source': {'name': feed_info['name']},
                    })
            except Exception as e:
                print(f"  ⚠️  RSS feed error ({feed_info['name']}): {e}")

        self._feed_cache = articles
        return articles

    def _parse_date(self, entry) -> Optional[datetime]:
        """Parse published date from a feed entry."""
        try:
            import time
            t = entry.get('published_parsed') or entry.get('updated_parsed')
            if t:
                return datetime.fromtimestamp(time.mktime(t), tz=timezone.utc)
        except Exception:
            pass
        return None

    def search_city_risks(self, city: str, country: str) -> List[Dict]:
        """
        Filter cached RSS articles for mentions of the specific city.
        City match is required — country-only matches are too broad when
        multiple hotels share the same country.
        """
        all_articles = self._fetch_all_feeds()
        city_lower = city.lower()

        matched = []
        for article in all_articles:
            text = f"{article['title']} {article['description']}".lower()
            if city_lower in text:
                matched.append(article)

        return matched

    def search_hotel_risks(self, hotel_name: str, city: str, country: str) -> List[Dict]:
        """
        Filter cached RSS articles for mentions of the hotel name,
        combined with city-level results.
        """
        all_articles = self._fetch_all_feeds()
        hotel_lower = hotel_name.lower()

        matched = []
        seen_urls = set()
        for article in all_articles:
            text = f"{article['title']} {article['description']}".lower()
            if hotel_lower in text:
                url = article.get('url', '')
                if url not in seen_urls:
                    seen_urls.add(url)
                    matched.append(article)

        # Also include city-level results
        for article in self.search_city_risks(city, country):
            url = article.get('url', '')
            if url not in seen_urls:
                seen_urls.add(url)
                matched.append(article)

        return matched

    def _deduplicate_articles(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles by URL."""
        seen = set()
        unique = []
        for article in articles:
            url = article.get('url', '')
            if url not in seen:
                seen.add(url)
                unique.append(article)
        return unique
