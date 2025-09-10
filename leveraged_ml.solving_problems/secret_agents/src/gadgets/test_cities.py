import sys
import os

# Add the parent directory to sys.path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gadgets.weather import get_weather

def test_cities():
    cities = ["London", "San Francisco", "New York", "Paris", "Tokyo"]
    
    print("Testing weather function for multiple cities:")
    print("-" * 50)
    
    for city in cities:
        print(f"\nTesting city: {city}")
        result = get_weather(city)
        print(f"Result: {result}")

if __name__ == "__main__":
    test_cities() 