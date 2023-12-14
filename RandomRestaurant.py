# This script uses Google Geocoding API and Google Places API to find a random restaurant near a given ZIP code.

import requests
import random
import datetime

# Convert a price range symbol to the corresponding price level
def price_symbol_to_level(symbol):
    return len(symbol) - 1

# Convert numerical price level to $ symbols
def price_level_to_symbols(level):
    if level is None or level < 0 or level > 4:
        return "Price level not available"
    return '$' * (level + 1) if level > 0 else '$'

# Convert ZIP code to coordinates using Google Geocoding API
def get_coordinates_from_zip(api_key, zip_code):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={zip_code}&key={api_key}"
    response = requests.get(geocode_url)
    if response.status_code != 200:
        return None, None

    results = response.json()['results']
    if not results:
        return None, None

    location = results[0]['geometry']['location']
    return location['lat'], location['lng']

# Fetch restaurants using Google Places API with price level filtering
def fetch_restaurants(api_key, lat, lon, radius, open_now, min_price_level, max_price_level):
    places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius={radius}&type=restaurant&key={api_key}"
    if open_now:
        places_url += '&opennow=true'
    if min_price_level is not None:
        places_url += f'&minprice={min_price_level}'
    if max_price_level is not None:
        places_url += f'&maxprice={max_price_level}'

    response = requests.get(places_url)
    if response.status_code != 200:
        return []

    results = response.json()['results']
    return [(place['name'], place['vicinity'], place['place_id']) for place in results]

# Fetch details of a specific place using Google Places API
def fetch_place_details(api_key, place_id):
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,vicinity,opening_hours,price_level&key={api_key}"
    response = requests.get(details_url)
    if response.status_code != 200:
        return None

    return response.json().get('result', {})

# Main function to randomly select a restaurant
def find_random_restaurant(api_key, zip_code, radius_miles, min_price_range, max_price_range, open_now):
    lat, lon = get_coordinates_from_zip(api_key, zip_code)
    if lat is None or lon is None:
        return "Invalid ZIP code or API Error."

    radius_meters = radius_miles * 1609.34  # Convert miles to meters
    min_price_level = price_symbol_to_level(min_price_range)
    max_price_level = price_symbol_to_level(max_price_range)
    restaurants = fetch_restaurants(api_key, lat, lon, radius_meters, open_now, min_price_level, max_price_level)

    if not restaurants:
        return "No restaurants found in the given radius."

    selected_restaurant = random.choice(restaurants)
    restaurant_details = fetch_place_details(api_key, selected_restaurant[2])  # Fetch details using place_id

    if restaurant_details and 'opening_hours' in restaurant_details and 'weekday_text' in restaurant_details['opening_hours']:
        today = datetime.datetime.now().strftime("%A")
        today_hours = next((s for s in restaurant_details['opening_hours']['weekday_text'] if today in s), None)
        closing_time = today_hours.split(" – ")[-1] if today_hours else "Closing time not available"
    else:
        closing_time = "Closing time not available"

    price_range = price_level_to_symbols(restaurant_details.get('price_level'))

    return f"Selected Restaurant: {selected_restaurant[0]} \nAddress: {selected_restaurant[1]} \nPrice Range: {price_range} \nClosing Time: {closing_time} \n"

api_key = "YOUR_GOOGLE_API_KEY"  # Replace with your actual API key
zip_code = input("Enter your ZIP code: ")
radius = float(input("Enter radius in miles: "))
min_price_range = input("Enter minimum price range ($ to $$$$): ")
max_price_range = input("Enter maximum price range ($ to $$$$): ")
open_now = input("Only show restaurants open now? (yes/no): ").lower() == 'yes'

print(find_random_restaurant(api_key, zip_code, radius, min_price_range, max_price_range, open_now))
