# ClimaTrip: Weather-Based Travel Planning System

ClimaTrip is an intelligent travel planning application that provides personalized destination recommendations in the USA based on weather preferences, complete with tourist attraction information and seasonal travel insights.

## 🌦️ Project Overview

Planning the perfect vacation often involves juggling multiple websites—checking weather forecasts, researching destinations, and finding attractions. ClimaTrip streamlines this process by combining weather data analysis with destination insights in one intuitive interface.

Users can either:
- Search for destinations matching their preferred weather conditions
- Get comprehensive information about a specific state they plan to visit

## ✨ Features

- **Weather-Based Recommendations**: Find US states with your preferred climate during specific travel periods
- **Historical Weather Analysis**: View past weather patterns to make informed travel decisions
- **Tourist Attraction Database**: Discover must-visit attractions for each US state
- **Seasonal Travel Insights**: Access monthly travel recommendations for optimal experiences
- **Live Weather Updates**: View current temperatures for potential destinations
- **Intuitive Interface**: Simple, user-friendly design built with Gradio

## 🔧 Technical Implementation

### Data Sources
- **OpenWeather API**: Real-time weather conditions for destinations
- **Historical Weather Datasets**: Monthly state-level climate data from UCI datasets
- **Web Scraping**: Tourist attractions from "My Joy-Filled Life" and monthly travel recommendations from "Unmissable Trips"

### Tech Stack
- **Python**: Core application logic and data processing
- **Gradio**: Web interface framework
- **BeautifulSoup**: HTML parsing for web scraping
- **Pandas**: Data manipulation and analysis
- **Requests**: API integration and web requests
- **SSL**: Secure data access configuration

### Key Components
- **Data Integration Pipeline**: Combines multiple data sources for comprehensive results
- **Caching System**: Stores scraped data in CSV format for improved reliability
- **Input Validation**: Robust date parsing and error handling
- **State Mapping System**: Standardized state code-to-name dictionary for consistent references

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Required libraries: gradio, pandas, requests, beautifulsoup4, ssl

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/climatrip.git
cd climatrip
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python final.py
```

4. Open the Gradio interface URL displayed in the terminal

## 📊 Usage

### Weather-Based Planning
1. Enter your planned travel date in MM-DD-YYYY format
2. Select your preferred weather type (very cold, cold, mild, hot, very hot)
3. Leave the state field empty
4. Submit to get matching destinations with attractions

### Destination-Based Planning
1. Enter your planned travel date in MM-DD-YYYY format
2. Select your destination state
3. Leave the weather type field empty
4. Submit to get weather forecast and attractions for your chosen destination

## 🛠️ Future Enhancements
- International destination support
- Accommodation and transportation recommendations
- Machine learning for personalized recommendations

## 🙏 Acknowledgments
- OpenWeather API for weather data
- My Joy-Filled Life and Unmissable Trips websites for tourism data
- UC Davis weather dataset repository
