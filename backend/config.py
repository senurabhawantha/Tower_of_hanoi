"""
Configuration settings for Tower of Hanoi application
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'tower_of_hanoi')
    
    # Game settings
    MIN_DISKS = 5
    MAX_DISKS = 10
    MIN_PEGS = 3
    MAX_PEGS = 4
