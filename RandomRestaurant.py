# This script uses Google Geocoding API and Google Places API to find a random restaurant near a given ZIP code.

import requests
import random

# Function to convert ZIP code to coordinates using Google Geocoding API
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

# Function to fetch restaurants using Google Places API
def fetch_restaurants(api_key, lat, lon, radius):
    places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lon}&radius={radius}&type=restaurant&key={api_key}"
    response = requests.get(places_url)
    if response.status_code != 200:
        return []

    results = response.json()['results']
    return [(place['name'], place['vicinity']) for place in results]

# Main function to randomly select a restaurant
def find_random_restaurant(api_key, zip_code, radius_miles):
    lat, lon = get_coordinates_from_zip(api_key, zip_code)
    if lat is None or lon is None:
        return "Invalid ZIP code or API Error."

    radius_meters = radius_miles * 1609.34  # Convert miles to meters
    restaurants = fetch_restaurants(api_key, lat, lon, radius_meters)
    
    if not restaurants:
        return "No restaurants found in the given radius."

    selected_restaurant = random.choice(restaurants)
    return f"Selected Restaurant: {selected_restaurant[0]}, Address: {selected_restaurant[1]}"

# Example Usage
api_key = "GOOGLE_API_KEY"  # Replace with your actual API key
zip_code = input("Enter your ZIP code: ")
radius = float(input("Enter radius in miles: "))
print(find_random_restaurant(api_key, zip_code, radius))
