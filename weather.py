#!/usr/bin/env python3

import requests
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class WeatherManager:
    def __init__(self):
        """Initialize the WeatherManager"""
        # OpenWeatherMap configuration
        self.api_key = None  # Set via update_api_key method
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.city_id = None  # Set via update_settings method
        
        # Cache configuration
        self.cache = {}
        self.cache_duration = timedelta(minutes=30)
        self.last_update = None

    def update_settings(self, settings):
        """Update weather settings"""
        try:
            self.api_key = settings.get('weather_api_key')
            self.city_id = settings.get('city_id')
            logger.info("Weather settings updated successfully")
        except Exception as e:
            logger.error(f"Failed to update weather settings: {str(e)}")

    def update_weather(self):
        """Fetch current weather data from OpenWeatherMap API"""
        if not self.api_key or not self.city_id:
            logger.error("Weather API key or city ID not set")
            return
        
        try:
            # Build API URL
            params = {
                'id': self.city_id,
                'appid': self.api_key,
                'units': 'metric'  # Use Celsius for temperature
            }
            
            # Make API request
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            # Parse response
            weather_data = response.json()
            
            # Extract relevant information
            self.cache = {
                'temperature': round(weather_data['main']['temp']),
                'condition': weather_data['weather'][0]['main'],
                'description': weather_data['weather'][0]['description'],
                'humidity': weather_data['main']['humidity'],
                'wind_speed': weather_data['wind']['speed'],
                'icon': weather_data['weather'][0]['icon']
            }
            
            self.last_update = datetime.now()
            logger.info("Weather data updated successfully")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch weather data: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse weather data: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error updating weather: {str(e)}")

    def get_current_weather(self):
        """Get the current weather data"""
        # Check if cache needs updating
        if (not self.last_update or 
            datetime.now() - self.last_update > self.cache_duration):
            self.update_weather()
        
        return self.cache if self.cache else None

    def get_forecast(self):
        """Get weather forecast (to be implemented)"""
        # TODO: Implement forecast functionality
        pass 