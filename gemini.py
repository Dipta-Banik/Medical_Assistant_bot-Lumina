import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel('gemini-2.0-flash')

def ask_gemini(prompt):
    response = model.generate_content(prompt)
    raw_text = response.text
    formatted_text = f"\n{raw_text}\n"
    return formatted_text


"""if __name__ == "__main__":
    user_prompt = input("Ask something: ")
    reply = ask_gemini(user_prompt)
    print(reply)"""
