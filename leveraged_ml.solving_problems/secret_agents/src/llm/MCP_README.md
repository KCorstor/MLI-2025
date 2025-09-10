# MCP Weather Implementation

This directory contains an implementation of the Model Context Protocol (MCP) for accessing weather data.

## Files

- `mcp_weather_server.py`: The MCP server that provides weather tools and resources
- `mcp_client.py`: A client that connects to the MCP server and uses Ollama to chat with the tools

## Prerequisites

1. Install the MCP Python SDK:
   ```
   pip install mcp
   ```

2. Make sure you have Ollama installed and the llama3.2 model downloaded:
   ```
   ollama pull llama3.2
   ```

## How It Works

### MCP Server

The MCP server (`mcp_weather_server.py`) provides:

1. A **tool** called `weather` that gets weather information for a location
2. A **resource** at `weather://{location}` that provides weather data
3. A **prompt** template for asking about weather

### MCP Client

The client (`mcp_client.py`):

1. Connects to the MCP server
2. Gets the available tools
3. Formats the tools for Ollama
4. Uses Ollama to chat with the tools
5. When the LLM calls a tool, it sends the request to the MCP server
6. Returns the final response with the weather information

## Running the Example

1. First, make sure the MCP server is installed:
   ```
   pip install mcp
   ```

2. Run the client script:
   ```
   python mcp_client.py
   ```

3. Ask questions about the weather, for example:
   ```
   What's the weather like in London?
   ```

## Differences from Custom Implementation

This MCP implementation differs from the custom tool implementation in several ways:

1. **Standardization**: Uses the official MCP protocol for communication
2. **Separation of Concerns**: The server and client are separate components
3. **Extensibility**: Easy to add new tools, resources, and prompts
4. **Interoperability**: Can work with any MCP-compatible client or server
5. **Structured Communication**: Uses a well-defined protocol for requests and responses

## Next Steps

- Add more tools and resources to the MCP server
- Implement authentication and authorization
- Deploy the MCP server as a standalone service
- Connect to other MCP clients like Claude Desktop 