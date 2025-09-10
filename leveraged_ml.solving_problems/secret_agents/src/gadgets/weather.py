import requests


# def get_weather(location):
#     API_KEY = "9683ebc01f9b0cd0c52b68e625e0b69c"  # Use your OpenWeatherMap API key
#     url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"

#     try:
#         response = requests.get(url)
#         data = response.json()
#         if data["cod"] == 200:
#             weather = data["weather"][0]["description"]
#             temperature = data["main"]["temp"]
#             return f"Weather in {location}: {weather}, {temperature}°C"
#         else:
#             return f"Could not retrieve weather for {location}."
#     except Exception as e:
#         print(f"Error retrieving weather data: {e}")
#         # Fallback to spoofed data if API fails
#         weather = "Sunny"
#         temperature = 25
#         return f"Weather in {location}: {weather} (spoofed), {temperature}°C (spoofed)"


def create_mcp_weather_server():
    """
    Creates and returns an MCP server with weather tools and resources.
    """
    from mcp.server import Server
    from mcp.types import ToolCall, ToolResult

    # Create MCP server
    server = Server()

    # Register the weather tool
    @server.tool("weather", "Get current weather for a location")
    def weather_tool(location: str) -> str:
        """Get the current weather for a specified location."""
        return get_weather(location)

    # Register a weather resource
    @server.resource("weather://{location}")
    def weather_resource(location: str) -> dict:
        """Get weather data as a structured resource."""
        try:
            API_KEY = "9683ebc01f9b0cd0c52b68e625e0b69c"
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()
            if data["cod"] == 200:
                return {
                    "location": location,
                    "description": data["weather"][0]["description"],
                    "temperature": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "wind_speed": data["wind"]["speed"]
                }
            else:
                return {"error": f"Could not retrieve weather for {location}."}
        except Exception as e:
            return {"error": str(e), "spoofed": True}

    # Register a weather prompt template
    server.prompt("weather_query", """
    You are a helpful weather assistant.
    When asked about weather, use the weather tool to get accurate information.
    Current query: {query}
    """)

    return server


if __name__ == "__main__":
    # Create and start the MCP server when this module is run directly
    server = create_mcp_weather_server()
    print("Starting MCP Weather Server on http://localhost:8000")
    server.start(host="0.0.0.0", port=8000)

