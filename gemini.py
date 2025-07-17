import google.generativeai as genai
import os
from dotenv import load_dotenv
import pyttsx3

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-2.0-flash')

engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.setProperty('volume', 1.0)  

def speak_text(text):
    engine.say(text)
    engine.runAndWait()


def ask_gemini(prompt):
    response = model.generate_content(prompt)
    raw_text = response.text
    formatted_text = f"\n{raw_text}\n"
    #speak_text(raw_text)
    return formatted_text


"""if __name__ == "__main__":
    user_prompt = input("Ask something: ")
    reply = ask_gemini(user_prompt)
    print(reply)"""