# Hotel Risk Monitoring Agent

An AI-powered risk monitoring system for hotel operations. Continuously analyzes news, weather alerts, and government reports to detect high-risk events that may affect hotel operations, guest safety, reputation, or demand.

## Features

✅ **Automated News Monitoring** - Scans global and local news via NewsAPI
✅ **Risk Classification** - Intelligent severity detection (HIGH/MEDIUM/LOW)
✅ **Smart Filtering** - False positive detection (historical events, forecasts, etc.)
✅ **Proximity Analysis** - Filters events within 10 km radius of hotels
✅ **Email Alerts** - Direct alerts to revenue managers via email
✅ **Daily Scheduling** - Automated daily monitoring runs
✅ **WhatsApp Format** - SMS/WhatsApp-friendly message format

## Requirements

- Python 3.8+
- NewsAPI account (free at https://newsapi.org)
- Email account (Gmail recommended for SMTP)
- Internet connection

## Installation

### 1. Clone and Setup

```bash
cd /Users/vankhaiphan/WorkSpace/hotel-risk-monitoring-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```
NEWS_API_KEY=your_newsapi_key_here
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_FROM=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=manager1@hotel.com,manager2@hotel.com
```

**Getting NewsAPI Key:**
1. Visit https://newsapi.org
2. Sign up for free account
3. Copy your API key

**Gmail SMTP Setup:**
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use app password (not regular password)

### 3. Add Your Hotels

Edit `config/hotels.json` with your properties:

```json
[
  {
    "name": "Your Hotel Name",
    "city": "City",
    "country": "Country",
    "lat": 0.0000,
    "lon": 0.0000
  }
]
```

## Usage

### Run Once (Testing)

```bash
python -m src.scheduler --mode once
```

### Daily Scheduled Monitoring

```bash
python -m src.scheduler --mode daemon --time 09:00
```

Runs daily at 09:00 (change --time for different time)

### Manual One-Time Run

```bash
python -m src.main
```

## Alert Output

### Console Output (No Email Configured)
```
⚠️ HOTEL RISK ALERT
Hotel: Hilton Budapest
City: Budapest
Country: Hungary

Event: Earthquake in Budapest Region
Severity: HIGH
Distance: 5.0 km

Impact Assessment:
Natural disaster event 5.0 km away poses immediate safety risk to guests...

Source: Global News Network
Date: 2026-03-15T14:30:00Z
```

### Email Format
HTML email with:
- Alert summary
- Hotel details
- Event description
- Impact assessment
- Link to original source

### WhatsApp-Style Message
```
⚠️ Daily Hotel Risk Briefing
2 alert(s) detected today.
2026-03-15

1. HOTEL: Hilton Budapest
   LOCATION: Budapest, Hungary
   EVENT: Natural disaster alert
   DISTANCE: 5.0 km
   ...
```

## Event Types Monitored

### HIGH SEVERITY (Alerts Triggered)

**Natural Disasters:**
- Earthquake, Hurricane, Typhoon, Tornado, Flood, Wildfire, Volcanic Eruption, Severe Storm

**Civil Unrest:**
- Riot, Violent Protest, Armed Conflict, Terrorist Attack

**Security Incidents:**
- Shooting, Bombing, Stabbing, Hostage Situation

**Hotel-Specific:**
- Hotel Fire, Hotel Evacuation, Building Collapse, Major Crime

**Transport Disruptions:**
- Airport Closure, Airline Disruption, Nationwide Strike, City Lockdown

### MEDIUM SEVERITY (Ignored Unless <1km)
- Normal protests
- Minor crimes
- Weather warnings without impact
- Traffic incidents
- Small fires
- Political news without disruption

## Configuration Options

Edit `.env` file:

```
NEWS_API_KEY=                    # NewsAPI key
WEATHER_API_KEY=                 # OpenWeatherMap key (optional)
SMTP_SERVER=smtp.gmail.com       # Email server
SMTP_PORT=587                    # SMTP port
EMAIL_FROM=                      # Your email (sender)
EMAIL_PASSWORD=                  # App password
EMAIL_TO=                        # Recipient emails (comma-separated)
MAX_ALERTS_PER_RUN=5             # Max alerts per daily run
SEARCH_RADIUS_KM=10              # Search radius around hotels
EVENT_LOOKBACK_HOURS=72          # How many hours back to search
```

## Architecture

```
src/
├── main.py                 # Main monitoring agent
├── scheduler.py            # Daily scheduler
├── news_analyzer.py        # NewsAPI integration
├── risk_classifier.py      # Event classification logic
├── proximity.py            # Distance calculations
├── alerter.py              # Email alert sender
└── config.py               # Configuration & constants
```

## How It Works

1. **Load Hotels** - Reads hotel list from config/hotels.json
2. **Search News** - Searches for incidents by hotel name and city
3. **Classify Events** - Rates severity using keyword matching
4. **Filter False Positives** - Removes outdated/historical events
5. **Check Proximity** - Ensures events are within 10 km radius
6. **Generate Impact** - Assesses how event affects hotel
7. **Send Alerts** - Emails revenue managers if HIGH-RISK found
8. **Schedule Daily** - Runs again tomorrow at configured time

## Extending the System

### Add Weather API Integration

Edit `src/weather_analyzer.py`:

```python
import requests

class WeatherAnalyzer:
    def get_alerts(self, lat, lon):
        # OpenWeatherMap API
        response = requests.get(
            f"https://api.openweathermap.org/data/3.0/alerts",
            params={"lat": lat, "lon": lon, "appid": API_KEY}
        )
        return response.json().get('alerts', [])
```

### Custom Data Sources

Edit `src/news_analyzer.py` to add:
- Government alert APIs
- Social media monitoring
- Disaster databases
- Airport/airline APIs

### Additional Filtering Rules

Edit `src/config.py`:

```python
HIGH_SEVERITY_KEYWORDS = {
    'custom_category': ['keyword1', 'keyword2']
}
```

## Troubleshooting

**No alerts received?**
- Check .env file configuration
- Verify EMAIL_TO recipients
- Run with --mode once to test immediate run

**API errors?**
- Verify NEWS_API_KEY is valid
- Check API rate limits (free tier: 100 requests/day)
- Ensure internet connection

**Email not sending?**
- Verify Gmail App Password (not regular password)
- Check SMTP settings
- Try disabling 2FA temporarily for testing

**Too many false positives?**
- Adjust keywords in src/config.py
- Increase EVENT_LOOKBACK_HOURS threshold
- Manually edit risk thresholds

## License

Proprietary - Hotel Revenue Management System

## Support

For issues or feature requests, contact your system administrator.

---

**Last Updated:** March 15, 2026
**Version:** 1.0.0
