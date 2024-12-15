#!/usr/bin/env python3

import pygame
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Display:
    # Display configuration
    DISPLAY_WIDTH = 800
    DISPLAY_HEIGHT = 480
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    BLUE = (0, 0, 255)

    def __init__(self):
        """Initialize the display"""
        logger.info("Initializing display...")
        
        try:
            # Initialize Pygame
            pygame.init()
            pygame.display.init()
            
            # Set up the display
            self.screen = pygame.display.set_mode(
                (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT)
            )
            pygame.display.set_caption("Smart Alarm")
            
            # Initialize fonts
            self.large_font = pygame.font.Font(None, 120)  # Time display
            self.medium_font = pygame.font.Font(None, 60)  # Date and weather
            self.small_font = pygame.font.Font(None, 40)   # Additional info
            
            logger.info("Display initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize display: {str(e)}")
            raise

    def _render_time(self, time):
        """Render the time display"""
        time_str = time.strftime("%H:%M")
        time_surface = self.large_font.render(time_str, True, self.WHITE)
        time_rect = time_surface.get_rect(center=(self.DISPLAY_WIDTH//2, 120))
        self.screen.blit(time_surface, time_rect)

    def _render_date(self, time):
        """Render the date display"""
        date_str = time.strftime("%A, %B %d")
        date_surface = self.medium_font.render(date_str, True, self.GRAY)
        date_rect = date_surface.get_rect(center=(self.DISPLAY_WIDTH//2, 200))
        self.screen.blit(date_surface, date_rect)

    def _render_weather(self, weather):
        """Render weather information"""
        if weather:
            try:
                # Temperature
                temp_str = f"{weather['temperature']}°C"
                temp_surface = self.medium_font.render(temp_str, True, self.WHITE)
                temp_rect = temp_surface.get_rect(center=(self.DISPLAY_WIDTH//2, 280))
                self.screen.blit(temp_surface, temp_rect)
                
                # Condition
                condition_surface = self.small_font.render(
                    weather['condition'], True, self.GRAY
                )
                condition_rect = condition_surface.get_rect(
                    center=(self.DISPLAY_WIDTH//2, 330)
                )
                self.screen.blit(condition_surface, condition_rect)
            except Exception as e:
                logger.error(f"Error rendering weather: {str(e)}")

    def _render_alarms(self, active_alarms):
        """Render active alarms"""
        if active_alarms:
            try:
                y_pos = 380
                alarm_text = "Next Alarm: "
                next_alarm = min(
                    (alarm for alarm in active_alarms if alarm['enabled']),
                    key=lambda x: x['time']
                )
                alarm_text += next_alarm['time'].strftime("%H:%M")
                
                alarm_surface = self.small_font.render(alarm_text, True, self.BLUE)
                alarm_rect = alarm_surface.get_rect(center=(self.DISPLAY_WIDTH//2, y_pos))
                self.screen.blit(alarm_surface, alarm_rect)
            except Exception as e:
                logger.error(f"Error rendering alarms: {str(e)}")

    def update(self, time=None, weather=None, active_alarms=None):
        """Update the display with current information"""
        try:
            # Clear the screen
            self.screen.fill(self.BLACK)
            
            # Render components
            if time:
                self._render_time(time)
                self._render_date(time)
            
            if weather:
                self._render_weather(weather)
            
            if active_alarms:
                self._render_alarms(active_alarms)
            
            # Update the display
            pygame.display.flip()
        except Exception as e:
            logger.error(f"Error updating display: {str(e)}")

    def cleanup(self):
        """Clean up display resources"""
        try:
            pygame.quit()
        except Exception as e:
            logger.error(f"Error during display cleanup: {str(e)}") 