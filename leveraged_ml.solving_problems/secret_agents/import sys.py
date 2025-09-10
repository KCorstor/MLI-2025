import sys
import os
import json
import asyncio
import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create server parameters for stdio connection to our MCP weather server
server_params = StdioServerParameters(
    command="python",
    args=[os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/llm/mcp_weather_server.py")],
    env=None,
)

async def main():
    print("Connecting to MCP weather server...")
    # Connect to MCP server and get tools
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {tools}")
            
            # Call the weather tool directly for Toronto
            location = "Toronto"
            print(f"Getting weather for {location} using MCP...")
            
            # Call the weather tool via MCP
            weather_result = await session.call_tool("weather", {"location": location})
            print(f"\nWeather info from MCP: {weather_result}")
            
            # Format tools for Ollama - simplified version
            ollama_tools = [{
                "name": "weather",
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city or location to get weather for"
                        }
                    },
                    "required": ["location"]
                }
            }]
            
            # Get user query
            query = f"What's the weather like in {location}?"
            print(f"\nSending query to LLM: {query}")
            
            # Send to Ollama
            client = ollama.Client()
            response = client.chat(
                model="llama3.2",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant with access to weather information. ALWAYS use the weather tool when asked about weather conditions."},
                    {"role": "user", "content": query}
                ],
                tools=ollama_tools,
                stream=False
            )
            
            print("\nLLM response:")
            print(response["message"]["content"])
            
            # Check for tool calls
            if "tool_calls" in response and response["tool_calls"]:
                for tool_call in response["tool_calls"]:
                    tool_name = tool_call["name"]
                    tool_args = json.loads(tool_call["arguments"])
                    
                    print(f"\nTool call detected: {tool_name}")
                    print(f"Arguments: {tool_args}")
                    
                    # Call the tool via MCP
                    tool_result = await session.call_tool(tool_name, tool_args)
                    
                    # Send result back to Ollama
                    final_response = client.chat(
                        model="llama3.2",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant with access to weather information."},
                            {"role": "user", "content": query},
                            {"role": "assistant", "content": None, "tool_calls": [tool_call]},
                            {"role": "tool", "name": tool_name, "content": tool_result}
                        ],
                        stream=False
                    )
                    
                    print("\nFinal response:")
                    print(final_response["message"]["content"])
            else:
                print("\nNo tool call was made, but we already got the weather directly from MCP.")

if __name__ == "__main__":
    asyncio.run(main())
