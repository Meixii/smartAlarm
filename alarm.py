#!/usr/bin/env python3

import logging
import json
from datetime import datetime, timedelta
import os
import threading
import time

logger = logging.getLogger(__name__)

class AlarmManager:
    def __init__(self, hardware_controller):
        """Initialize the AlarmManager"""
        self.hardware = hardware_controller
        self.alarms = []
        self.active_alarm = None
        self.snooze_duration = timedelta(minutes=9)  # Default snooze time
        self.gradual_wake_duration = timedelta(minutes=30)  # Duration for wake-up routine
        
        # Sound configuration
        self.sounds_dir = "sounds"
        self.default_alarm_sound = os.path.join(self.sounds_dir, "digital.mp3")
        
        # Threading
        self.alarm_thread = None
        self.stop_thread = False

    def update_settings(self, settings):
        """Update alarm settings from website data"""
        try:
            if 'alarms' in settings:
                self.alarms = []
                for alarm_data in settings['alarms']:
                    alarm = {
                        'time': datetime.strptime(alarm_data['time'], "%H:%M").time(),
                        'days': alarm_data.get('days', []),  # Days of week (0-6, 0 is Monday)
                        'enabled': alarm_data.get('enabled', True),
                        'sound': alarm_data.get('sound', self.default_alarm_sound),
                        'gradual_wake': alarm_data.get('gradual_wake', True),
                        'snooze_enabled': alarm_data.get('snooze_enabled', True)
                    }
                    self.alarms.append(alarm)
            
            if 'snooze_duration' in settings:
                self.snooze_duration = timedelta(minutes=settings['snooze_duration'])
            
            if 'gradual_wake_duration' in settings:
                self.gradual_wake_duration = timedelta(
                    minutes=settings['gradual_wake_duration']
                )
            
            logger.info("Alarm settings updated successfully")
        except Exception as e:
            logger.error(f"Failed to update alarm settings: {str(e)}")

    def get_active_alarms(self):
        """Get list of active alarms"""
        return [alarm for alarm in self.alarms if alarm['enabled']]

    def check_alarms(self):
        """Check if any alarms should be triggered"""
        if self.active_alarm:
            return  # Don't check for new alarms while one is active
        
        current_time = datetime.now()
        current_weekday = current_time.weekday()
        
        for alarm in self.alarms:
            if not alarm['enabled']:
                continue
            
            # Check if alarm should trigger on current day
            if alarm['days'] and current_weekday not in alarm['days']:
                continue
            
            alarm_time = datetime.combine(current_time.date(), alarm['time'])
            
            # Check if it's time for gradual wake-up
            if alarm['gradual_wake']:
                wake_start_time = alarm_time - self.gradual_wake_duration
                if wake_start_time <= current_time <= alarm_time:
                    self._start_gradual_wake(alarm, alarm_time)
            
            # Check if it's alarm time
            if (current_time - alarm_time).total_seconds() < 60:  # Within 1 minute
                self._trigger_alarm(alarm)

    def _start_gradual_wake(self, alarm, alarm_time):
        """Start gradual wake-up routine"""
        try:
            # Calculate progress through wake-up period
            current_time = datetime.now()
            wake_start_time = alarm_time - self.gradual_wake_duration
            progress = (current_time - wake_start_time).total_seconds() / \
                      self.gradual_wake_duration.total_seconds()
            
            # Gradually increase brightness
            brightness = int(progress * 100)
            self.hardware.set_led_brightness(brightness)
            
            # Gradually change color temperature (warm to cool)
            r = int(255 * (1 - progress))  # Decrease red
            b = int(255 * progress)        # Increase blue
            g = int(128)                   # Keep some green
            self.hardware.set_led_color(r, g, b, transition_time=1)
            
        except Exception as e:
            logger.error(f"Error during gradual wake: {str(e)}")

    def _trigger_alarm(self, alarm):
        """Trigger the alarm"""
        try:
            self.active_alarm = alarm
            
            # Start alarm in separate thread
            self.stop_thread = False
            self.alarm_thread = threading.Thread(target=self._alarm_routine)
            self.alarm_thread.start()
            
            logger.info("Alarm triggered successfully")
        except Exception as e:
            logger.error(f"Failed to trigger alarm: {str(e)}")
            self.active_alarm = None

    def _alarm_routine(self):
        """Run the alarm routine"""
        try:
            while not self.stop_thread:
                # Set maximum brightness
                self.hardware.set_led_brightness(100)
                self.hardware.set_led_color(255, 255, 255)
                
                # Play alarm sound
                self.hardware.play_sound(
                    self.active_alarm['sound'],
                    loop=True
                )
                
                # Wait for stop or snooze
                time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"Error in alarm routine: {str(e)}")
        finally:
            self.hardware.stop_sound()
            self.hardware.set_led_brightness(0)

    def snooze(self):
        """Snooze the current alarm"""
        if self.active_alarm and self.active_alarm['snooze_enabled']:
            try:
                self.stop_thread = True
                if self.alarm_thread:
                    self.alarm_thread.join()
                
                # Create new alarm time
                current_time = datetime.now()
                snooze_time = (current_time + self.snooze_duration).time()
                
                # Create temporary snooze alarm
                snooze_alarm = self.active_alarm.copy()
                snooze_alarm['time'] = snooze_time
                snooze_alarm['gradual_wake'] = False  # Disable gradual wake for snooze
                
                # Replace active alarm with snooze alarm
                self.active_alarm = None
                self.alarms.append(snooze_alarm)
                
                logger.info("Alarm snoozed successfully")
            except Exception as e:
                logger.error(f"Failed to snooze alarm: {str(e)}")

    def stop_alarm(self):
        """Stop the current alarm"""
        if self.active_alarm:
            try:
                self.stop_thread = True
                if self.alarm_thread:
                    self.alarm_thread.join()
                self.active_alarm = None
                logger.info("Alarm stopped successfully")
            except Exception as e:
                logger.error(f"Failed to stop alarm: {str(e)}")

    def cleanup(self):
        """Clean up resources"""
        self.stop_alarm() 