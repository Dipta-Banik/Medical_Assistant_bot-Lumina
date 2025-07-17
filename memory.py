# ---------------------- Memory ------------------------

from bot_logic import handle_query
import pandas as pd
import re

chat_history = []
class ConversationMemory:
    def __init__(self):
        self.stage = None
        self.user_name = None
        self.age = None
        self.gender = None
        self.selected_doctor = None
        self.appointment_time = None
        self.contact = None
        self.payment = None
        self.last_department = None
        self.selected_date = None
        self.selected_time = None
        self.doc_list = None

    def reset(self):
        self.stage = None
        self.user_name = None
        self.age = None
        self.gender = None
        self.selected_doctor = None
        self.appointment_time = None
        self.contact = None
        self.payment = None
        self.last_department = None
        self.selected_date = None
        self.selected_time = None
        self.doc_list = None

global_memory = ConversationMemory()


print("👍🏼")

""""while True:
    user_input = input("🧑 You: ").strip()

    if user_input.lower() in ["exit", "quit", "bye"]:
        print("🤖 Bot: Thank you! Stay healthy! 👋")
        break

    # Chatbot response
    #bot_response = handle_query(user_input)
    #print("🤖 Bot:", bot_response)"""
