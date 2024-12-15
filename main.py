#!/usr/bin/env python3

import time
import sys
import json
import requests
from datetime import datetime
import logging

# Local module imports
from display import Display
from alarm import AlarmManager
from weather import WeatherManager
from hardware import HardwareController

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SmartAlarm:
    def __init__(self):
        logger.info("Initializing SmartAlarm system...")
        
        # Initialize components
        try:
            self.hardware = HardwareController()
            self.display = Display()
            self.alarm_manager = AlarmManager(self.hardware)
            self.weather_manager = WeatherManager()
            
            # Configuration
            self.update_interval = 60  # Update display every 60 seconds
            self.weather_update_interval = 1800  # Update weather every 30 minutes
            self.last_weather_update = 0
            
            logger.info("All components initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize components: {str(e)}")
            sys.exit(1)

    def fetch_website_data(self):
        """Fetch alarm settings and configurations from the xhosting website"""
        try:
            # TODO: Replace with actual API endpoint
            response = requests.get('https://your-xhosting-website.com/api/alarm-settings')
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch website data: {str(e)}")
            return None

    def update_display(self):
        """Update the display with current information"""
        try:
            current_time = datetime.now()
            weather_data = self.weather_manager.get_current_weather()
            
            # Update display with current information
            self.display.update(
                time=current_time,
                weather=weather_data,
                active_alarms=self.alarm_manager.get_active_alarms()
            )
        except Exception as e:
            logger.error(f"Failed to update display: {str(e)}")

    def run(self):
        """Main loop of the SmartAlarm system"""
        logger.info("Starting SmartAlarm main loop")
        
        while True:
            try:
                current_time = time.time()
                
                # Check and update weather if needed
                if current_time - self.last_weather_update >= self.weather_update_interval:
                    self.weather_manager.update_weather()
                    self.last_weather_update = current_time
                
                # Fetch latest settings from website
                website_data = self.fetch_website_data()
                if website_data:
                    self.alarm_manager.update_settings(website_data)
                
                # Check and trigger alarms
                self.alarm_manager.check_alarms()
                
                # Update display
                self.update_display()
                
                # Sleep for the update interval
                time.sleep(self.update_interval)
                
            except KeyboardInterrupt:
                logger.info("Shutting down SmartAlarm system...")
                self.hardware.cleanup()
                sys.exit(0)
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    smart_alarm = SmartAlarm()
    smart_alarm.run() 