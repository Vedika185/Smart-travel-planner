import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration for Smart Travel Planner."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'smart-travel-planner-ahmedabad-secret-key-2025-gujarat')
    
    # MySQL Database Settings
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'smart_travel_db')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Company Location & Identity (Ahmedabad, Gujarat)
    COMPANY_NAME = "Smart Travel Planner"
    COMPANY_TAGLINE = "Incredible Journeys Crafted From The Heart of Gujarat"
    COMPANY_CITY = "Ahmedabad"
    COMPANY_STATE = "Gujarat"
    COMPANY_COUNTRY = "India"
    COMPANY_ADDRESS = "Suite 504, Westgate Business Bay, SG Highway, Makarba, Ahmedabad, Gujarat 380051"
    COMPANY_PHONE = "+91 (079) 4912-8800"
    COMPANY_EMAIL = "support@smarttravelplanner.in"
    DEFAULT_ORIGIN = "Ahmedabad, Gujarat (AMD)"
    
    # Currency Settings
    CURRENCY_CODE = "INR"
    CURRENCY_SYMBOL = "₹"
    
    # Session timeout
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
