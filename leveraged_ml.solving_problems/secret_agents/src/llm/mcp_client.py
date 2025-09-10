import asyncio
import json
import sys
import os
import ollama

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add the parent directory to sys.path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="python",  # Executable
    args=[os.path.join(os.path.dirname(__file__), "mcp_weather_server.py")],  # Path to our MCP server
    env=None,  # Optional environment variables
)

async def get_tools_from_mcp_server():
    """Connect to the MCP server and get the available tools"""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            return tools

async def call_mcp_tool(tool_name, arguments):
    """Call a specific tool on the MCP server"""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Call the tool
            result = await session.call_tool(tool_name, arguments)
            return result

def format_tools_for_ollama(tools):
    """Format MCP tools in a way Ollama can understand"""
    ollama_tools = []
    
    for tool in tools:
        ollama_tool = {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
        
        for arg in tool.arguments:
            ollama_tool["parameters"]["properties"][arg.name] = {
                "type": "string",
                "description": arg.description
            }
            if arg.required:
                ollama_tool["parameters"]["required"].append(arg.name)
        
        ollama_tools.append(ollama_tool)
    
    return ollama_tools

async def chat_with_mcp_tools(prompt):
    """Chat with Ollama using MCP tools"""
    # Get tools from MCP server
    mcp_tools = await get_tools_from_mcp_server()
    ollama_tools = format_tools_for_ollama(mcp_tools)
    
    # Initialize Ollama client
    client = ollama.Client()
    model_name = "llama3.2"
    
    print(f"Available tools: {[tool.name for tool in mcp_tools]}")
    
    # Create the message with tools
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant with access to weather information. Use the weather tool when asked about weather conditions."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    # Generate response from ollama with tools
    response = client.chat(
        model=model_name,
        messages=messages,
        tools=ollama_tools,
        stream=False
    )
    
    # Check if the response contains tool calls
    if "tool_calls" in response and response["tool_calls"]:
        for tool_call in response["tool_calls"]:
            tool_name = tool_call["name"]
            tool_args = json.loads(tool_call["arguments"])
            
            print(f"Calling tool: {tool_name} with arguments: {tool_args}")
            
            # Call the MCP tool
            tool_result = await call_mcp_tool(tool_name, tool_args)
            
            # Add the tool result to the conversation
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call]
            })
            
            messages.append({
                "role": "tool",
                "name": tool_name,
                "content": tool_result
            })
            
            # Get a final response with the tool result
            final_response = client.chat(
                model=model_name,
                messages=messages,
                stream=False
            )
            
            return final_response["message"]["content"]
    
    # Return the original response if no tool was used
    return response["message"]["content"]

async def main():
    while True:
        user_input = input("\nEnter your question (or 'quit' to exit): ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
            
        response = await chat_with_mcp_tools(user_input)
        print(f"\nResponse: {response}")

if __name__ == "__main__":
    asyncio.run(main()) 