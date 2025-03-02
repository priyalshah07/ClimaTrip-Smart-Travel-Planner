
import gradio as gr
import pandas as pd
import ssl
import requests
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime

# ---- Functions from gradio.ipynb ----

def extract_date(date):
    try:
        # Split the date string into components
        month, day, year = date.split("-")
        # Validate date format
        datetime(int(year), int(month), int(day))
        return month
    except:
        return None

def convert_link(mm):
    link = f"https://files.asmith.ucdavis.edu/weather/daily/state_noweight/2022{mm}.csv"
    return link

def replace_state_codes_with_names(df, column_name):
    state_dict = {
        'AL': 'Alabama', 'AR': 'Arkansas', 'AZ': 'Arizona', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida',
        'GA': 'Georgia', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois',
        'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana',
        'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan',
        'MN': 'Minnesota', 'MO': 'Missouri', 'MS': 'Mississippi', 'MT': 'Montana',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire',
        'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York',
        'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
        'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee',
        'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VT': 'Vermont',
        'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'
    }
    df_copy = df.copy()
    df_copy[column_name] = df_copy[column_name].map(state_dict)
    return df_copy

def get_matching_states(date, weather_type):
    try:
        if not date:
            return "Please enter a valid date in MM-DD-YYYY format"
            
        # Configure SSL context
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Extract month from date
        month = extract_date(date)
        if not month:
            return "Please enter a valid date in MM-DD-YYYY format"
        
        # Get the CSV link
        link = convert_link(month)
        
        # Read the CSV
        dataframe = pd.read_csv(link)
        dataframe_state_names = replace_state_codes_with_names(dataframe, 'st_abb')
        
        # Temperature ranges for weather types
        weather_ranges = {
            "very cold": (0, 8),
            "cold": (8, 17),
            "mild": (17, 24),
            "hot": (24, 33),
            "very hot": (33, 50)
        }
        
        # Get temperature range for selected weather type
        min_value, max_value = weather_ranges[weather_type]
        
        # Get states with matching weather
        mask = (dataframe_state_names['tavg'] >= min_value) & (dataframe_state_names['tavg'] <= max_value)
        matching_states = dataframe_state_names.loc[mask, 'st_abb'].unique()
        
        return list(matching_states)
        
    except Exception as e:
        return f"An error occurred: {str(e)}"

def get_state_temp(date, state):
    try:
        if not date:
            return "Please enter a valid date in MM-DD-YYYY format"
            
        # Configure SSL context
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Extract month from date
        month = extract_date(date)
        if not month:
            return "Please enter a valid date in MM-DD-YYYY format"
        
        # Get the CSV link
        link = convert_link(month)
        
        # Read the CSV
        dataframe = pd.read_csv(link)
        dataframe_state_names = replace_state_codes_with_names(dataframe, 'st_abb')
        
        # Get temperature for selected state
        state_temp = dataframe_state_names[dataframe_state_names['st_abb'] == state]['tavg'].mean()
        
        return state_temp
        
    except Exception as e:
        return f"An error occurred: {str(e)}"

# ---- Functions from live_temp_api.py ----

def get_lat_lon(state_name, api_key):
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={state_name},US&limit=1&appid={api_key}"
    
    response = requests.get(geo_url)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]["lat"], data[0]["lon"]
        else:
            return None, None
    else:
        return None, None

def get_current_temperature(state_name):
    api_key = "1567da2c68ff870ba0b299baa9c8b276"  # OpenWeather API key
    lat, lon = get_lat_lon(state_name, api_key)
    if lat is None or lon is None:
        return "Unable to get location data for this state."
    
    # Construct URL for NWS weather data
    nws_url = f"https://forecast.weather.gov/MapClick.php?textField1={lat}&textField2={lon}"
    
    response = requests.get(nws_url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        return "Error fetching weather data."
    
    soup = BeautifulSoup(response.content, 'html.parser')

    # Scrape the current temperature
    temp_element = soup.find(class_="myforecast-current-lrg")
    if temp_element:
        temp = temp_element.get_text()
        return temp
    else:
        return "Temperature data not found."

# ---- Functions from scraper_debug.py ----

def scrape_state_attractions():
    """Cache and return state attractions data"""
    cache_file = "state_attractions_cache.csv"
    
    # If cache exists, use it
    if os.path.exists(cache_file):
        try:
            return pd.read_csv(cache_file)
        except:
            pass  # If cache read fails, scrape data
    
    try:
        url = "https://www.myjoyfilledlife.com/must-do-attractions-must-see-places-in-all-50-states/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main content
        content_main = soup.find('div', class_='entry-content')
        if not content_main:
            return None

        states_data = []
        current_state = None
        
        # Iterate through all elements in the content
        for elem in content_main.find_all(['h2', 'ul']):
            if elem.name == 'h2':
                current_state = elem.get_text(strip=True)
            elif elem.name == 'ul' and current_state:
                # Get all attractions for the current state
                attractions = [li.get_text(strip=True) for li in elem.find_all('li')]
                # Join all attractions with a semicolon separator
                attractions_text = '; '.join(attractions)
                states_data.append({
                    'state': current_state,
                    'attractions': attractions_text
                })

        # Create DataFrame
        df = pd.DataFrame(states_data)
        
        # Save to cache
        if not df.empty:
            df.to_csv(cache_file, index=False)
            
        return df

    except Exception as e:
        return None

def get_attractions_for_state(state_name):
    """Get attractions for a specific state"""
    attractions_df = scrape_state_attractions()
    if attractions_df is None:
        return "Unable to retrieve attractions data."
    
    # Find the state in the dataframe (may need fuzzy matching)
    state_row = attractions_df[attractions_df['state'].str.contains(state_name, case=False)]
    if state_row.empty:
        return "No attractions found for this state."
    
    # Return the attractions
    return state_row.iloc[0]['attractions']

def scrape_monthly_recommendations():
    """Cache and return monthly travel recommendations"""
    cache_file = "monthly_recommendations_cache.csv"
    
    # If cache exists, use it
    if os.path.exists(cache_file):
        try:
            return pd.read_csv(cache_file)
        except:
            pass  # If cache read fails, scrape data
    
    try:
        url = "https://www.unmissabletrips.com/guides/the-united-states-a-month-by-month-travel-guide"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        month_sections = soup.find_all('h2')
        
        monthly_data = []
        for section in month_sections:
            month_info = {}
            month_info['month'] = section.text.strip()
            
            next_elem = section.find_next('p')
            if next_elem:
                month_info['recommendations'] = next_elem.text.strip()
                
            monthly_data.append(month_info)
        
        df = pd.DataFrame(monthly_data)
        
        # Save to cache
        if not df.empty:
            df.to_csv(cache_file, index=False)
            
        return df
        
    except Exception as e:
        return None

def get_month_recommendations(month_number):
    """Get recommendations for a specific month"""
    recommendations_df = scrape_monthly_recommendations()
    if recommendations_df is None:
        return "Unable to retrieve monthly recommendations."
    
    # Convert month number to month name
    month_names = {
        "01": "January", "02": "February", "03": "March", "04": "April",
        "05": "May", "06": "June", "07": "July", "08": "August",
        "09": "September", "10": "October", "11": "November", "12": "December"
    }
    month_name = month_names.get(month_number)
    
    if not month_name:
        return "Invalid month."
    
    # Find the month in the dataframe
    month_row = recommendations_df[recommendations_df['month'].str.contains(month_name, case=False)]
    if month_row.empty:
        return "No recommendations found for this month."
    
    # Return the recommendations
    return month_row.iloc[0]['recommendations']

# ---- Integrated Gradio Function ----

def integrated_app(date, weather_type, state):
    if not date:
        return "Please enter a valid date in MM-DD-YYYY format"
    
    month = extract_date(date)
    if not month:
        return "Please enter a valid date in MM-DD-YYYY format"
    
    # Scenario 1: User enters date and weather type
    if weather_type and not state:
        try:
            # Get states with matching weather
            matching_states = get_matching_states(date, weather_type)
            
            if isinstance(matching_states, str):  # Error message
                return matching_states
            
            # Get activities and current weather for a sample of states
            sample_states = matching_states[:3] if len(matching_states) > 3 else matching_states
            
            result = f"Results for {date} with {weather_type} weather:\n\n"
            result += f"All states with {weather_type} weather: {', '.join(matching_states)}\n\n"
            
            # Get monthly recommendations
            monthly_rec = get_month_recommendations(month)
            result += f"Travel recommendations for this month:\n{monthly_rec}\n\n"
            
            # Get details for sample states
            result += "Detailed information for selected states:\n\n"
            
            for state_code in sample_states:
                # Find the full state name
                state_dict = {
                    'AL': 'Alabama', 'AR': 'Arkansas', 'AZ': 'Arizona', 'CA': 'California',
                    'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida',
                    'GA': 'Georgia', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois',
                    'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana',
                    'MA': 'Massachusetts', 'MD': 'Maryland', 'ME': 'Maine', 'MI': 'Michigan',
                    'MN': 'Minnesota', 'MO': 'Missouri', 'MS': 'Mississippi', 'MT': 'Montana',
                    'NC': 'North Carolina', 'ND': 'North Dakota', 'NE': 'Nebraska', 'NH': 'New Hampshire',
                    'NJ': 'New Jersey', 'NM': 'New Mexico', 'NV': 'Nevada', 'NY': 'New York',
                    'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
                    'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee',
                    'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia', 'VT': 'Vermont',
                    'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia', 'WY': 'Wyoming'
                }
                state_name = state_dict.get(state_code, state_code)
                
                result += f"State: {state_name}\n"
                
                # Get current temperature
                current_temp = get_current_temperature(state_name)
                result += f"Current temperature: {current_temp}\n"
                
                # Get attractions
                attractions = get_attractions_for_state(state_name)
                result += f"Must-visit attractions: {attractions}\n\n"
            
            return result
            
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    # Scenario 2: User enters date and state
    elif state and not weather_type:
        try:
            # Get historical weather for the state
            state_temp = get_state_temp(date, state)
            
            if isinstance(state_temp, str):  # Error message
                return state_temp
            
            result = f"Results for {state} on {date}:\n\n"
            result += f"Historical average temperature: {state_temp:.1f}°C\n\n"
            
            # Get current temperature
            current_temp = get_current_temperature(state)
            result += f"Current temperature: {current_temp}\n\n"
            
            # Get state attractions
            attractions = get_attractions_for_state(state)
            result += f"Must-visit attractions: {attractions}\n\n"
            
            # Get monthly recommendations
            monthly_rec = get_month_recommendations(month)
            result += f"Travel recommendations for this month:\n{monthly_rec}"
            
            return result
            
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    # Both or neither provided
    elif state and weather_type:
        return "Please provide either weather type OR state, not both."
    else:
        return "Please provide either weather type OR state along with the date."

# ---- Gradio Interface ----

weather_types = ["very cold", "cold", "mild", "hot", "very hot"]

states_list = [
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 
    'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 
    'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 
    'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 
    'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 
    'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 
    'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 
    'Wisconsin', 'Wyoming'
]

iface = gr.Interface(
    fn=integrated_app,
    inputs=[
        gr.Textbox(label="Enter Date (MM-DD-YYYY)", placeholder="MM-DD-YYYY"),
        gr.Dropdown(choices=weather_types, label="Select Weather Type (Optional)", value=None),
        gr.Dropdown(choices=states_list, label="Select State (Optional)", value=None)
    ],
    outputs=gr.Textbox(label="Results"),
    title="Integrated Weather and Travel Planning System",
    description="Enter a date and either a weather type OR a state to get personalized travel information.",
    theme="default"
)

# Launch the interface
if __name__ == "__main__":
    # Configure SSL context for safety
    ssl._create_default_https_context = ssl._create_unverified_context
    iface.launch()