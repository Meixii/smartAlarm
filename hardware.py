#!/usr/bin/env python3

import time
import board
import neopixel
import RPi.GPIO as GPIO
import busio
import adafruit_ds3231
import pygame
import logging

logger = logging.getLogger(__name__)

class HardwareController:
    # GPIO pins configuration
    SPEAKER_PIN = 18
    LED_PIN = 12
    LED_COUNT = 8
    I2C_SDA = board.SDA
    I2C_SCL = board.SCL

    def __init__(self):
        """Initialize hardware components"""
        logger.info("Initializing hardware components...")
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Initialize RGB LED strip
        try:
            self.pixels = neopixel.NeoPixel(
                board.D12,  # GPIO12
                self.LED_COUNT,
                brightness=0.5,
                auto_write=False
            )
            self.pixels.fill((0, 0, 0))
            self.pixels.show()
        except Exception as e:
            logger.error(f"Failed to initialize LED strip: {str(e)}")
            self.pixels = None

        # Initialize RTC
        try:
            i2c = busio.I2C(self.I2C_SCL, self.I2C_SDA)
            self.rtc = adafruit_ds3231.DS3231(i2c)
        except Exception as e:
            logger.error(f"Failed to initialize RTC: {str(e)}")
            self.rtc = None

        # Initialize audio
        try:
            pygame.mixer.init()
            self.sound_volume = 0.5
            pygame.mixer.music.set_volume(self.sound_volume)
        except Exception as e:
            logger.error(f"Failed to initialize audio: {str(e)}")

    def set_led_brightness(self, brightness_level):
        """Set LED strip brightness (0-100)"""
        if self.pixels:
            try:
                normalized_brightness = max(0, min(1.0, brightness_level / 100))
                self.pixels.brightness = normalized_brightness
                self.pixels.show()
            except Exception as e:
                logger.error(f"Failed to set LED brightness: {str(e)}")

    def set_led_color(self, r, g, b, transition_time=0):
        """Set LED strip color with optional transition"""
        if self.pixels:
            try:
                if transition_time == 0:
                    self.pixels.fill((r, g, b))
                    self.pixels.show()
                else:
                    # Gradual transition
                    current = self.pixels[0]
                    steps = 50
                    r_step = (r - current[0]) / steps
                    g_step = (g - current[1]) / steps
                    b_step = (b - current[2]) / steps
                    
                    for i in range(steps):
                        new_r = int(current[0] + (r_step * i))
                        new_g = int(current[1] + (g_step * i))
                        new_b = int(current[2] + (b_step * i))
                        self.pixels.fill((new_r, new_g, new_b))
                        self.pixels.show()
                        time.sleep(transition_time / steps)
            except Exception as e:
                logger.error(f"Failed to set LED color: {str(e)}")

    def play_sound(self, sound_file, loop=False):
        """Play a sound file"""
        try:
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception as e:
            logger.error(f"Failed to play sound: {str(e)}")

    def stop_sound(self):
        """Stop playing sound"""
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            logger.error(f"Failed to stop sound: {str(e)}")

    def set_volume(self, volume_level):
        """Set sound volume (0-100)"""
        try:
            self.sound_volume = max(0, min(1.0, volume_level / 100))
            pygame.mixer.music.set_volume(self.sound_volume)
        except Exception as e:
            logger.error(f"Failed to set volume: {str(e)}")

    def get_rtc_time(self):
        """Get current time from RTC"""
        if self.rtc:
            try:
                return self.rtc.datetime
            except Exception as e:
                logger.error(f"Failed to get RTC time: {str(e)}")
                return None
        return None

    def set_rtc_time(self, datetime_obj):
        """Set RTC time"""
        if self.rtc:
            try:
                self.rtc.datetime = datetime_obj
            except Exception as e:
                logger.error(f"Failed to set RTC time: {str(e)}")

    def cleanup(self):
        """Clean up hardware resources"""
        try:
            if self.pixels:
                self.pixels.fill((0, 0, 0))
                self.pixels.show()
            pygame.mixer.quit()
            GPIO.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}") 