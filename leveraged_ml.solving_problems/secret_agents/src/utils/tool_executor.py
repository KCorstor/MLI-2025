from gadgets.decryptor import decrypt_message
from gadgets.weather import get_weather


def execute_tool(tool_name, parameters):
    """
    - Extract parameters
    - Execute the requested tool
    - Return the result.
    """

    if tool_name == "weather":
        city = parameters.get("city")
        # TODO: Run the weather tool

    # TODO: ADD OTHER TOOLS HERE

    else:
        result = "Unknown tool requested."

    return result
