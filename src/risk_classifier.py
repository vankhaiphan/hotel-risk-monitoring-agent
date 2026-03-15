from datetime import datetime, timedelta
from typing import List, Dict, Optional
from src.config import HIGH_SEVERITY_KEYWORDS, MEDIUM_SEVERITY_KEYWORDS, IGNORE_KEYWORDS

class RiskClassifier:
    """Classifies news events by severity and relevance."""
    
    def __init__(self):
        self.high_keywords = HIGH_SEVERITY_KEYWORDS
        self.medium_keywords = MEDIUM_SEVERITY_KEYWORDS
        self.ignore_keywords = IGNORE_KEYWORDS
    
    def classify_event(self, article: Dict, hotel_name: str = None) -> Optional[Dict]:
        """
        Classify an article into risk severity.
        
        Args:
            article: News article from API
            hotel_name: Hotel name (for proximity scoring)
        
        Returns:
            Risk classification dict or None if should be ignored
        """
        title = article.get('title', '').lower()
        description = article.get('description', '').lower()
        content = f"{title} {description}".lower()
        
        # Check false positives
        if self._is_false_positive(article, content):
            return None
        
        # Check ignore keywords (forecasts, future events, etc.)
        if self._should_ignore(content):
            return None
        
        # Classify severity
        severity, event_type = self._determine_severity(content)
        
        if severity == 'HIGH':
            return {
                'article': article,
                'severity': severity,
                'event_type': event_type,
                'title': article.get('title', ''),
                'description': article.get('description', ''),
                'url': article.get('url', ''),
                'source': article.get('source', {}).get('name', 'Unknown'),
                'published_at': article.get('publishedAt', ''),
                'confidence': self._calculate_confidence(content, event_type)
            }
        
        return None
    
    def _determine_severity(self, content: str) -> tuple:
        """
        Determine severity level and event type.
        
        Returns:
            Tuple of (severity_level, event_type)
        """
        for category, keywords in self.high_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content:
                    return 'HIGH', category
        
        for category, keywords in self.medium_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content:
                    return 'MEDIUM', category
        
        return 'LOW', 'unknown'
    
    def _should_ignore(self, content: str) -> bool:
        """
        Check if event should be ignored (forecast, historical, etc.)
        """
        for ignore_phrase in self.ignore_keywords:
            if ignore_phrase.lower() in content:
                return True
        
        return False
    
    def _is_false_positive(self, article: Dict, content: str) -> bool:
        """
        Filter false positives:
        - Ambiguous hotel name matches
        - Historical events
        - Too old events
        """
        
        # Check age - reject if older than lookback period
        published_at = article.get('publishedAt', '')
        if published_at:
            try:
                # Handle both ISO format with Z and without
                if published_at.endswith('Z'):
                    pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                else:
                    pub_date = datetime.fromisoformat(published_at)
                    if pub_date.tzinfo is None:
                        # Assume UTC if no timezone
                        from datetime import timezone
                        pub_date = pub_date.replace(tzinfo=timezone.utc)
                
                age_hours = (datetime.fromisoformat(datetime.utcnow().isoformat()).replace(tzinfo=None) - pub_date.replace(tzinfo=None)).total_seconds() / 3600
                if age_hours > 72:
                    return True
            except Exception as e:
                # If we can't parse date, don't filter it out
                pass
        
        # Check for historical/anniversary language
        historical_phrases = [
            'on this day',
            'years ago',
            'anniversary',
            'remembering',
            'historical',
            'in history'
        ]
        
        for phrase in historical_phrases:
            if phrase.lower() in content:
                return True
        
        return False
    
    def _calculate_confidence(self, content: str, event_type: str) -> float:
        """
        Calculate confidence score (0.0 to 1.0) for the classification.
        """
        score = 0.5
        
        # Increase confidence for certain keywords
        high_confidence_keywords = [
            'confirmed', 'reported', 'emergency', 'alert', 'warning',
            'evacuation', 'closure', 'disruption'
        ]
        
        for keyword in high_confidence_keywords:
            if keyword in content:
                score += 0.1
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def filter_and_rank(self, events: List[Dict]) -> List[Dict]:
        """
        Filter high-risk events and rank by confidence and date.
        """
        high_risk = [e for e in events if e and e.get('severity') == 'HIGH']
        
        # Sort by confidence (descending) and date (most recent first)
        sorted_events = sorted(
            high_risk,
            key=lambda x: (
                -x.get('confidence', 0),
                -datetime.fromisoformat(
                    x.get('published_at', '').replace('Z', '+00:00')
                ).timestamp()
            )
        )
        
        return sorted_events
