import ollama
import json
import sys
import os
import asyncio

# Add the parent directory to sys.path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Create server parameters for stdio connection to our MCP weather server
server_params = StdioServerParameters(
    command="python",  # Executable
    args=[os.path.join(os.path.dirname(__file__), "mcp_weather_server.py")],  # Path to our MCP server
    env=None,  # Optional environment variables
)

async def get_mcp_tools():
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

def format_mcp_tools_for_ollama(tools):
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

async def send_to_llm(prompt, context=None, user_info=None, conversation_history=None):
    """Send a prompt to the LLM with MCP tools available"""
    # Initialize the Ollama client
    client = ollama.Client()
    model_name = "llama3.2"  # Updated to match your installed model
    
    # Get MCP tools
    mcp_tools = await get_mcp_tools()
    ollama_tools = format_mcp_tools_for_ollama(mcp_tools)
    
    # Construct the messages
    messages = []
    
    # Add context if provided
    if context:
        messages.append({
            "role": "system",
            "content": f"Context: {context}"
        })
    
    # Add user info if provided
    if user_info:
        messages.append({
            "role": "system",
            "content": f"User Information: {user_info}"
        })
    
    # Add conversation history if provided
    if conversation_history:
        messages.append({
            "role": "system",
            "content": f"Conversation History: {conversation_history}"
        })
    
    # Add system message about tools
    messages.append({
        "role": "system",
        "content": "You are a helpful assistant with access to weather information. Use the weather tool when asked about weather conditions."
    })
    
    # Add the user's prompt
    messages.append({
        "role": "user",
        "content": prompt
    })

    try:
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
                
                print(f"Calling MCP tool: {tool_name} with arguments: {tool_args}")
                
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

    except Exception as e:
        print(f"Error communicating with the LLM: {e}")
        return {"message": "Failed to communicate with the LLM server."}

async def main():
    # Example with weather tool
    weather_prompt = "What's the weather like in London?"
    print(f"\nSending weather query: {weather_prompt}")
    
    weather_response = await send_to_llm(weather_prompt)
    
    print("\nResponse for weather query:")
    print(weather_response)
    
    # Interactive mode
    while True:
        user_input = input("\nEnter your question (or 'quit' to exit): ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
            
        response = await send_to_llm(user_input)
        print(f"\nResponse: {response}")

if __name__ == "__main__":
    asyncio.run(main()) 