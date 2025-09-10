import ollama
import json
import sys
import os
import argparse
import re

# Add the parent directory to sys.path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gadgets.weather import get_weather


def send_to_llm(prompt, context=None, user_info=None, conversation_history=None, tools=None):
    # Initialize the Ollama client
    client = ollama.Client()
    model_name = "llama3.2"  # Updated to match your installed model
    # Build the tools section and construct the prompt
    tools_section = ""
    if tools:
        tools_section = "Available tools:\n" + "\n".join([f"- {tool}" for tool in tools]) + "\n\nUse tools by responding with: [USE_TOOL:tool_name:parameters]\n"

    full_prompt = f"""Context: {context or 'No additional context provided'}
{tools_section}
User Query: {prompt}

Please provide a helpful response."""

    try:
        # Generate response from ollama
        response = client.generate(model=model_name, prompt=full_prompt)
        response_text = response['response']
        
        # Check if the response contains a tool command
        if "[USE_TOOL:" in response_text:
            # Extract tool command
            tool_start = response_text.find("[USE_TOOL:")
            tool_end = response_text.find("]", tool_start)
            tool_command = response_text[tool_start+10:tool_end].strip()
            
            # Parse tool command
            parts = tool_command.split(":")
            if len(parts) >= 2:
                tool_name = parts[0]
                params = parts[1:]
                
                # Execute the appropriate tool
                if tool_name == "weather" and params:
                    location = params[0]
                    weather_info = get_weather(location)
                    
                    # Send follow-up with tool results
                    follow_up_prompt = f"""Previous query: {prompt}
You suggested using the weather tool for location: {location}
Tool result: {weather_info}
Please provide your final response based on this information."""
                    
                    follow_up_response = client.generate(model=model_name, prompt=follow_up_prompt)
                    return follow_up_response['response']
            
        # Return the original response if no tool was used
        return response_text

    except Exception as e:
        print(f"Error communicating with the LLM: {e}")
        return {"message": "Failed to communicate with the LLM server."}


if __name__ == "__main__":
    # Example with weather tool
    weather_prompt = "What's the weather like in San Francisco?"
    weather_response = send_to_llm(
        prompt=weather_prompt,
        tools=["weather:location - Get weather information for a location"]
    )
    print("\nResponse for weather query:")
    print(weather_response)


# - **Weather Gadget**: Retrieves real-time weather data.
# - **Decryption Gadget**: Solves puzzles like Caesar ciphers.
# - **Additional Gadgets**: Time zone converter, translator.

# 1. **User Input**: Message sent via chat interface.
# 2. **LLM Processing**: LLM determines required actions and tool(s).
# 3. **Tool Invocation**: Flask executes tools as requested.
# 4. **Tool Result Handling**: Results are sent back to the LLM.
# 5. **LLM Response**: Final response is generated and returned to the user.
