import sys
import os
from mcp.server.fastmcp import FastMCP

# Add the parent directory to sys.path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gadgets.weather import get_weather

# Create an MCP server
mcp = FastMCP("Weather Assistant")

@mcp.tool()
def weather(location: str) -> str:
    """Get current weather for a location"""
    return get_weather(location)

if __name__ == "__main__":
    mcp.run() 