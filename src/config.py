import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', '')

# Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL_FROM = os.getenv('EMAIL_FROM', '')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')
EMAIL_TO = os.getenv('EMAIL_TO', '').split(',')

# Alert Settings
MAX_ALERTS_PER_RUN = int(os.getenv('MAX_ALERTS_PER_RUN', 5))
SEARCH_RADIUS_KM = float(os.getenv('SEARCH_RADIUS_KM', 10))
EVENT_LOOKBACK_HOURS = int(os.getenv('EVENT_LOOKBACK_HOURS', 72))

# Hotels Configuration
HOTELS_FILE = os.path.join(os.path.dirname(__file__), '../config/hotels.json')

# Severity Keywords
HIGH_SEVERITY_KEYWORDS = {
    'natural_disaster': [
        'earthquake', 'hurricane', 'typhoon', 'tornado', 'flood', 'wildfire', 
        'volcanic eruption', 'severe storm', 'landslide'
    ],
    'civil_unrest': [
        'riot', 'violent protest', 'armed conflict', 'terrorist attack', 'insurgency'
    ],
    'security_incident': [
        'shooting', 'bombing', 'stabbing', 'hostage', 'armed robbery', 'assassination'
    ],
    'hotel_incident': [
        'hotel fire', 'hotel evacuation', 'building collapse', 'hotel crime'
    ],
    'transport_disruption': [
        'airport closure', 'airline disruption', 'nationwide strike', 'city lockdown',
        'rail strike', 'transport shutdown'
    ]
}

MEDIUM_SEVERITY_KEYWORDS = {
    'protests': ['protest', 'demonstration'],
    'crime': ['robbery', 'theft', 'assault', 'crime'],
    'fire': ['fire', 'blaze'],
    'incidents': ['accident', 'collision', 'traffic']
}

IGNORE_KEYWORDS = [
    'forecast', 'warning', 'expected', 'potential', 'may occur', 'could happen',
    'historical', 'anniversary', 'memorial'
]
