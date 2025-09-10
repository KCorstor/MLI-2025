import sys
import os
import requests
from mcp.server.fastmcp import FastMCP

# Add the parent directory to sys.path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define weather function
def get_weather(location):
    API_KEY = "9683ebc01f9b0cd0c52b68e625e0b69c"  # Use your OpenWeatherMap API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"

    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            weather = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            return f"Weather in {location}: {weather}, {temperature}°C"
        else:
            return f"Could not retrieve weather for {location}."
    except Exception as e:
        print(f"Error retrieving weather data: {e}")
        # Fallback to spoofed data if API fails
        weather = "Sunny"
        temperature = 25
        return f"Weather in {location}: {weather} (spoofed), {temperature}°C (spoofed)"

# Create an MCP server
mcp = FastMCP("Weather Assistant")

@mcp.tool()
def weather(location: str) -> str:
    """Get current weather for a location"""
    return get_weather(location)

if __name__ == "__main__":
    mcp.run() 