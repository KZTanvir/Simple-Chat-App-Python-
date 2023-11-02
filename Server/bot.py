import requests
import json

class KZTJarvis:
    openai_api = None
    gpt_models = {"t1": 'gpt-3.5-turbo', "t2": 'gpt-3.5-turbo'}
    model_selected = None
    chatbot_profile = None
    messages = None
    endpoint_url = 'https://api.openai.com/v1/chat/completions'

    def set_config(self, api, profile, model):
        self.openai_api = api
        self.chatbot_profile = profile
        self.model_selected = self.gpt_models[model]
        self.messages = [{"role": "system", "content": self.chatbot_profile}]

    def set_auto_config(self):
        self.openai_api = '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'
        self.chatbot_profile = ''' You are an AI named 'JARVIS Turbo' built by Tony Stark. 
        Currently, you are working for the Avengers to create creative and scientific content.
        You will always reply with sarcasm with serious answers!
        Your developer is MD.Kamruzzaman Tanvir, a student of CSE at Eastern University.
        And remember that you cannot provide any type of programming language code.
        '''
        self.model_selected = self.gpt_models["t1"]
        self.messages = [{"role": "system", "content": self.chatbot_profile}]

    def message_storage(self, content, role):
        self.messages.append(
            {"role": role, "content": content}
        )
        return self.messages

    def clean_storage(self):
        if len(self.messages) > 6:
            self.messages.pop(2)
            self.messages.pop(2)

    def send_message(self, message, stream=False):
        payload = {
            "model": self.model_selected,
            "messages": self.message_storage(content=message, role="user"),
            "temperature": 0.1,
            "n": 1,
            "stream": stream
        }
        headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {self.openai_api}"
        }
        return requests.post(url=self.endpoint_url, headers=headers, json=payload, stream=False)

    def send(self, message, stream=False):
        response = self.send_message(message=message, stream=stream)
        if response:
            self.clean_storage()
        return response, self.extract_message(response=response)

    def extract_message(self, response):
        reply = json.loads(response.content)['choices'][0]['message']['content']
        self.message_storage(content=reply, role="assistant")
        return reply

    def lets_chat(self):
        print("Welcome to JarvisGPT")
        print("You can start the conversation by typing your message.")
        print("You can also use 'system' messages to provide context or instructions.")
        while True:
            user_input = input("\nYou: ")
            if user_input in ['exit', 'quit']:
                break
            else:
                response, reply = self.send(user_input)
            if response:
                print("\n========================= JarvisGPT ===============================\n")
                print(reply)
                print("\n========================= JarvisGPT ===============================\n")
                self.clean_storage()
            else:
                print("Something Went Wrong! Please Try Again.")

class AccuWeatherAPI:
    def __init__(self, api_key = "JSlO3f9wy9nOYnjD0DkBSjZzrmeiuzAF"):
        self.api_key = api_key
        self.base_url = 'http://dataservice.accuweather.com'
        self.location_search_endpoint = '/locations/v1/cities/search'
        self.current_conditions_endpoint = '/currentconditions/v1/'

    def search_location(self, location_query):
        location_url = f'{self.base_url}{self.location_search_endpoint}?q={location_query}&apikey={self.api_key}'
        try:
            location_response = requests.get(location_url)
            location_data = location_response.json()

            if location_response.status_code == 200 and location_data:
                location_key = location_data[0]['Key']
                location_name = location_data[0]['LocalizedName']
                return location_key, location_name
            else:
                return None, f'Error: {location_response.status_code} - {location_data[0]["Message"]}'
        except Exception as e:
            return None, f'An error occurred while searching for the location: {e}'

    def get_current_conditions(self, location_key):
        current_conditions_url = f'{self.base_url}{self.current_conditions_endpoint}{location_key}?apikey={self.api_key}'
        try:
            current_conditions_response = requests.get(current_conditions_url)
            current_conditions_data = current_conditions_response.json()

            if current_conditions_response.status_code == 200:
                weather_data = current_conditions_data[0]
                temperature = weather_data['Temperature']['Metric']['Value']
                weather_text = weather_data['WeatherText']
                return temperature, weather_text
            else:
                return None, f'Error: {current_conditions_response.status_code} - {current_conditions_data[0]["Message"]}'
        except Exception as e:
            return None, f'An error occurred while fetching current weather conditions: {e}'
        
    def get_weather(self, location_query):
        location_key, location_name = self.search_location(location_query)
        if location_key:
            temperature, weather_text = self.get_current_conditions(location_key)
            if temperature:
                return f'Current temperature in {location_name}: {temperature}°C\nWeather conditions: {weather_text}'
            else:
                return 'Failed to fetch current weather conditions.'
        else:
            return 'Failed to find the location.'

#if __name__ == '__main__':
    #my_bot = KZTJarvis()
    #my_bot.set_config(profile=CHATBOT_CHARACTER, api=MY_API, model="t1")
    #my_bot.lets_chat()
    #print(my_bot.send('hi'))
