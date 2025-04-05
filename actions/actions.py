import requests
import random
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, EventType
import re
from bs4 import BeautifulSoup


class ActionCalculate(Action):
    def name(self) -> Text:
        return "action_calculate"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:

        user_message = tracker.latest_message.get('text', '')  # Get the user's message
        print(f"User message: {user_message}")

        # Use regex to find numbers and operators in the message
        numbers = re.findall(r'\d+', user_message)  # Extract all numbers
        operator = None

        # Determine the operator from the user's message
        if '+' in user_message:
            operator = '+'
        elif '-' in user_message:
            operator = '-'
        elif '*' in user_message or 'x' in user_message:
            operator = '*'
        elif '/' in user_message:
            operator = '/'

        if len(numbers) == 2 and operator:
            number1, number2 = map(int, numbers)  # Unpack and convert the first two numbers
            print(f"Extracted number1: {number1}, number2: {number2}, operator: {operator}")

            try:
                if operator == '+':
                    result = number1 + number2
                elif operator == '-':
                    result = number1 - number2
                elif operator == '*':
                    result = number1 * number2
                elif operator == '/':
                    if number2 != 0:  # Check for division by zero
                        result = number1 / number2
                    else:
                        dispatcher.utter_message(text="Cannot divide by zero.")
                        return []

                dispatcher.utter_message(text=f"The result is: {result}")
            except ValueError:
                dispatcher.utter_message(text="Invalid input for numbers. Please enter valid numbers.")
        else:
            dispatcher.utter_message(text="Please provide exactly two numbers and an operator to calculate.")

        return []


class ActionFetchWeather(Action):
    def name(self) -> str:
        return "action_tell_weather"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:
        city = tracker.get_slot("city")

        if not city:
            dispatcher.utter_message("I couldn't find the city. Please make sure to mention a city for the weather.")
            return []

        api_key = "a2469c509f107841321178648c660045"
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric"
        }
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            temperature = data['main']['temp']
            weather_description = data['weather'][0]['description']
            dispatcher.utter_message(
                f"The weather in {city} is {weather_description} with a temperature of {temperature}°C.")
        else:
            dispatcher.utter_message("Unable to fetch weather information. Please check the city name.")

        return []


class ActionTellJoke(Action):
    def name(self) -> str:
        return "action_tell_joke"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "I told my computer I needed a break, and now it won't stop sending me KitKat ads.",
            "What do you call fake spaghetti? An impasta!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "Why did the bicycle fall over? Because it was two-tired!",
            "Why don't skeletons fight each other? They don't have the guts.",
            "What did one wall say to the other wall? I'll meet you at the corner!",
            "Why don't programmers like nature? It has too many bugs.",
            "Why was the math book sad? Because it had too many problems.",
            "What do you call cheese that isn't yours? Nacho cheese!",
            "I told my wife she was drawing her eyebrows too high. She looked surprised.",
            "Why don't some couples go to the gym? Because some relationships don't work out.",
            "I would avoid the sushi if I was you. It’s a little fishy.",
            "What did the ocean say to the beach? Nothing, it just waved.",
            "Why did the coffee file a police report? It got mugged.",
            "How do you organize a space party? You planet.",
            "Why did the golfer bring two pairs of pants? In case he got a hole in one.",
            "I'm reading a book on anti-gravity. It's impossible to put down!",
            "Why do cows have hooves instead of feet? Because they lactose.",
            "What do you call a factory that makes good products? A satisfactory!",
        ]

        # Select a random joke from the list
        joke = random.choice(jokes)
        dispatcher.utter_message(joke)

        return []


class ActionInterpretEmotion(Action):
    def name(self) -> str:
        return "action_interpret_emotion"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:
        emotions = {
            "sad": ["I am feeling sad", "I feel like crying", "I feel heartbroken"],
            "happy": ["I am happy today", "I feel great", "I feel joyful in my accomplishments"],
            "angry": ["I feel angry", "I am feeling frustrated", "I feel irritated"],
            "excited": ["I am excited", "I feel like I'm on top of the world", "I feel invigorated"],
            "overwhelmed": ["I feel overwhelmed", "I am feeling overwhelmed with stress",
                            "I feel like I have too much on my plate"],
            "anxious": ["I am feeling anxious", "I feel anxious about the future",
                        "I feel anxious about social situations"],
            "hopeful": ["I am feeling hopeful", "I am feeling hopeful for the future", "I feel optimistic today"],
            "grateful": ["I am feeling grateful", "I feel grateful for my support system", "I feel blessed"],
            "content": ["I feel content", "I feel fulfilled", "I feel secure in my relationships"],
            "bored": ["I feel bored", "I feel like I’m in a rut", "I feel like I'm missing out"],
            "confused": ["I feel confused", "I feel perplexed", "I feel confused about my choices"],
            "proud": ["I feel proud", "I feel incredibly proud of myself", "I feel proud of my growth"],
            "motivated": ["I feel motivated", "I feel inspired", "I am feeling motivated to change"],
            "relaxed": ["I am feeling relaxed", "I feel at peace", "I feel light as a feather"],
            "guilty": ["I feel guilty", "I am feeling guilty about my choices", "I feel unworthy"],
            "lonely": ["I am feeling lonely", "I feel isolated", "I feel disconnected"],
            "stressed": ["I feel stressed", "I am feeling overwhelmed with stress",
                         "I feel burdened by responsibilities"],
            "indifferent": ["I feel indifferent", "I feel apathetic", "I feel like everything is okay"],
            "energized": ["I feel energized", "I am feeling invigorated", "I feel alive"],
            "restless": ["I am feeling restless", "I feel like I need to move", "I feel an urge to change"],
        }

        user_message = tracker.latest_message.get('text', '').lower()
        response = []

        for emotion, phrases in emotions.items():
            if any(phrase.lower() in user_message for phrase in phrases):
                response.append(f"Your expression of feeling {emotion} is noted. How can I assist you with this?")

        if not response:
            response.append("I didn't quite catch your feelings. Can you elaborate on how you're feeling?")

        dispatcher.utter_message(text=" ".join(response))

        return []


class ActionFetchInfo(Action):
    def name(self) -> str:
        return "action_fetch_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:
        query = tracker.latest_message.get('text')

        if not query:
            dispatcher.utter_message("I couldn't find any information to fetch. Please ask a question.")
            return []

        duckduckgo_url = f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1"
        response = requests.get(duckduckgo_url)

        if response.status_code == 200:
            data = response.json()
            if 'Abstract' in data and data['Abstract']:
                summary = data['Abstract']
                dispatcher.utter_message(f"Here is a brief summary: {summary}")
            else:
                dispatcher.utter_message("Sorry, I couldn't find any information on that topic.")
        else:
            dispatcher.utter_message("There was an error fetching the information. Please try again.")

        return []


class ActionFetchLiveScores(Action):
    def name(self) -> str:
        return "action_fetch_live_scores"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[EventType]:

        cricket_api_key = "83b8ead8-03c8-4cef-87f8-9cf6f0ed9488"
        api_url = "https://api.cricapi.com/v1/series?apikey=83b8ead8-03c8-4cef-87f8-9cf6f0ed9488&offset=0&search="
        params = {
            "apikey": cricket_api_key,
            "offset": 0
        }

        response = requests.get(api_url, params=params)

        # Check if the response is successful
        if response.status_code == 200:
            data = response.json()

            if 'data' in data and data['data']:
                series_info = data['data'][0]  # Get the first series for simplicity
                series_name = series_info.get('name', 'Series name not found')
                matches_count = series_info.get('matches', 'No matches found')

                # Send series details to user
                dispatcher.utter_message(
                    f"Current Series: {series_name}, Matches Scheduled: {matches_count}.")
            else:
                dispatcher.utter_message("There are no ongoing series at the moment.")
        else:
            dispatcher.utter_message("Unable to fetch live scores. Please try again later.")

        return []

