import requests

def test_weather_api():
    API_KEY = "9683ebc01f9b0cd0c52b68e625e0b69c"
    location = "London"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={API_KEY}&units=metric"
    
    print(f"Testing weather API for location: {location}")
    print(f"Using URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Response status code: {response.status_code}")
        
        data = response.json()
        print(f"Response data: {data}")
        
        if response.status_code == 200 and data.get("cod") == 200:
            print("API key is working correctly!")
            weather = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            print(f"Weather in {location}: {weather}, {temperature}°C")
            return True
        else:
            print(f"API key is not working. Error code: {data.get('cod')}, Message: {data.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"Error testing API: {e}")
        return False

if __name__ == "__main__":
    test_weather_api() 