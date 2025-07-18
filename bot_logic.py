import pandas as pd
import os, csv, re
from datetime import datetime
from email_sent import send_email
from gemini import ask_gemini
from diseases import (
    match_symptoms, 
    get_diseases_df, 
    recommend_doctor
)
from appoinment_logic import (
    is_valid_name, 
    is_valid_age, 
    is_valid_gender, 
    is_valid_date, 
    is_valid_time, 
    is_valid_email,  
    get_next_slots
)
from doctor import (
    extract_doctor_name,
    extract_department,
    get_doctor_details,
    get_doctors_by_department,
    get_departments_and_counts,
    get_fees_info,
    get_availability_info,
    get_doctors_df,
    doctor_info,
    is_doctor_available_on_date
)

doctors_df = get_doctors_df()
diseases_df = get_diseases_df()
import os
from datetime import datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(BASE_DIR, '..', 'Data')
os.makedirs(DATA_FOLDER, exist_ok=True)

# ---------------------- Utility Functions ------------------------
def detect_intent(text):
    prompt = f"""
You are **Lumina**, the intelligent and friendly medical assistant. 
Your job is to understand and categorize the user's question into one of the following intent keywords:
- cancel
- department_info 
- appointment_booking
- fees_info
- availability_info
- symptom_check
- general_query
- yes_query
- no_query
- get_user_details
- doctor_info



User question: "{text}"

Reply with **ONLY** the correct intent keyword
"""
    intent = ask_gemini(prompt).strip().lower()
    return intent

def save_appointment(doctor, department, user_name, appointment_time, age, gender, email):
    filename = os.path.join(DATA_FOLDER, "appointments.csv")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.exists(filename)

    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Doctor", "Department", "User Name", "Appointment Time", "Name", "age", "gender", "contact",])
        writer.writerow([
            now,
            doctor,
            department,
            user_name,
            appointment_time,
            user_name,
            age,
            gender,
            email,
        ])
        
    send_email(
        full_name=user_name,
        doctor=doctor,
        department=department,
        appointment_time=appointment_time,
        age=age,
        gender=gender,
        to_email=email
    )
           
 #---------------------- Brain --------------------------
        
def handle_query(text):
    from memory import global_memory
    memory = global_memory
    text_lower = text.lower()
    intent = detect_intent(text_lower)
    
    if memory.selected_doctor and not memory.user_name:
        name = text.strip().title()
        if not is_valid_name(name):
            return "❌ Please enter a valid name (e.g., John Doe) or type 'cancel' to cancel booking."
        memory.user_name = name
        memory.stage = "get_age"
        return(
            f"🧑 Thanks, {memory.user_name}!\n\n"
            f"Let's keep going — could you please tell me **How old are you?** (e.g. 25)"
        )

    if memory.stage == "get_age" and not memory.age:
        if not is_valid_age(text.strip()):
            return "❌ Please enter a valid age (e.g., 25) or type 'cancel' to cancel booking."
        memory.age = text.strip()
        memory.stage = "get_gender"
        return "⚧️ Got it. What's your gender? (Male/Female)"

    if memory.stage == "get_gender" and not memory.gender:
        gender = text.strip().title()
        if not is_valid_gender(gender):
            return "❌ Please enter a valid gender (Male or Female) or type 'cancel' to cancel booking."
        memory.gender = gender
        memory.stage = "get_date"
        return "📅 Please mention your preferred appointment **datee** (e.g., 15 July)."

    if memory.stage == "get_date" and not memory.selected_date:
        if not is_valid_date(text.strip()):
            return "❌ Please enter a valid **future date** (e.g., 15 July)."
    
        memory.selected_date = text.strip().title()
        available, day_name, time_range = is_doctor_available_on_date(memory.selected_doctor, memory.selected_date)

        if not available:
            return f"❌ The doctor is not available on **{memory.selected_date}** because it's a **{day_name}**. Please choose a different date for your appointment."
        start, end = time_range
        memory.stage = "get_time"
        return f"🗓️ You selected **{memory.selected_date}** ({day_name}).\n" \
           f"⏰ The doctor is available from **{start} to {end}**.\n" \
           f"Please enter your preferred time (e.g., {start})."


    if memory.stage == "get_time" and not memory.appointment_time:
        selected_time = text.strip().upper()
        memory.appointment_time = f"{memory.selected_date}, {selected_time}"
        memory.stage = "get_email"
        return ("📧 Please provide your **valid email ID** (e.g., xyz@gmail.com)."
                "📧 A valid email is required so I can send you the appointment details — this is important even for demo purposes. 😊"
                )


    if memory.stage == "get_email" and memory.selected_doctor and memory.user_name and memory.appointment_time and not memory.contact:
        if not is_valid_email(text.strip()):
            return (
                "❌ Please provide a valid email address (e.g., yourname@gmail.com) or type 'cancel' to cancel the booking.\n\n"
                "📧 A valid email is required so I can send you the appointment details — this is important even for demo purposes. 😊"
            )
        memory.contact = text.strip()
        save_appointment(
            doctor=memory.selected_doctor,
            department = memory.last_department,
            user_name = memory.user_name,
            appointment_time=memory.appointment_time,
            age=memory.age,
            gender=memory.gender,
            email=memory.contact
            )
            
        confirmed = (
            f"✅ Appointment confirmed with **{memory.selected_doctor}**\n"
            f"🏥Department:{memory.last_department}"
            f"👤 Name: {memory.user_name}\n"
            f"📅 Time: {memory.appointment_time}\n"
            f"🎂 Age: {memory.age}\n"
            f"⚧️ Gender: {memory.gender}\n"
            f"📧 Email: {memory.contact}\n\n"
            f"📁 Your appointment has been successfully booked, and I’ve also sent you an email to **{memory.contact}** with all the details.\n\n Let me know if there’s anything else I can assist you with! 😊"
            )
   
        memory.reset()
        return confirmed
    
    elif memory.stage == "get_name":
        if intent == "cancel" or text_lower.strip() == "cancel":
            memory.stage = None
            memory.selected_doctor = None
            memory.last_department = None
            return "☃️ No worries, I've cancelled the process. Let me know if you need help with something else!"

        doctor_name = extract_doctor_name(text_lower)
        if doctor_name:
            doctor_info = get_doctor_details(doctor_name)
            memory.selected_doctor = doctor_name  # store doctor name in memory
            memory.stage = "get_user_details"
            return (
                    f"{doctor_info}\n\n"
                    f"📝 Great! You've selected **{doctor_name}** for your appointment.\n"
                    f"Please type the **patient's full name** to continue with the booking process."
            )
        else:
            return "❌ I couldn't find that doctor. Please provide a valid **doctor name** from the list or type 'cancel'."
        

    department = extract_department(text_lower)
    if department:
        memory.last_department = department
        doctors_list = get_doctors_by_department(department)
        memory.doc_list = doctors_list
        memory.stage = "awaiting_doctor_name"
        return (
            f"🩺 Here are our **{department}** doctors:\n\n{doctors_list}\n\n"
            "Would you like to book an appointment with any of them? If yes, type **yes**."
        )



    elif intent == "symptom_check":
        matches = match_symptoms(text, doctors_df, diseases_df)
        if matches:
            raw_disease_info = "\n\n".join([
            f"Disease: {m['Disease']}\n"
            f"Department: {m['Department']}"
            for m in matches
        ])
    
        prompt = (
            f"A user described the following symptoms. Based on that, here are the possible conditions and departments:\n\n"
            f"{raw_disease_info}\n\n"
            f"Respond like a caring medical assistant. Mention the possible conditions clearly, suggest the departments involved, "
            f"and ask the user which department they would like to explore. End by offering help to see doctor options or book an appointment."
        )
    
        return ask_gemini(prompt)
     
    elif intent == "appointment_booking":
        if not memory.selected_doctor:
            memory.stage = "get_name"
            return (
                f"🩺 To book your appointment, please enter the **doctor's name**.\n\n"
                f"If you're unsure which doctor to choose, click on the **Department Info** button on the screen to explore doctors by their departments.\n\n"
                f"Or type **cancel** to exit."
            )

        
    elif intent == "yes_query":
        if memory.stage == "ask_confirm_booking":
            memory.stage = "get_name"
            return (
                f"📝 Great! Please tell me the **doctor's name** you'd like to book with from the **{memory.last_department}** department.\n\n"
                f"Here are the available doctors:\n{memory.doc_list}\n Please choose a doctor by name to proceed with your appointment.\n"
            )
        
        elif not memory.selected_doctor:
            memory.stage = "ask_confirm_booking"
            return (
                    "✅ Great! Would you like to book an appointment now?\n"
                    "Please reply with **yes** or **no**.\n\n"
                    "👉 If you reply **yes**, you'll need to complete the appointment booking process.\n"
                    "👉 If you reply **no**, the process will be cancelled."
            )

        else:
            memory.stage = "get_user_details"
            return (
            f"📝 Great! Let's proceed with booking an appointment with **{memory.selected_doctor}**.\n"
            f"Please share your **name**."
            )
            
    elif intent == "no_query":
        if memory.stage == "ask_confirm_booking" or memory.stage == "awaiting_doctor_name":
            memory.stage = None
            memory.selected_doctor = None
            return "✅ No problem! Let me know if you want help with anything else."
        elif memory.stage == "get_name" or memory.stage == "get_user_details":
            memory.stage = None
            memory.selected_doctor = None
            return "❌ Appointment cancelled. Let me know if you need anything else."
        else:
            prompt = f"👍 Alright! Let you know if user need help with something else!"
            return ask_gemini(prompt)
    
    elif intent == "cancel":
        memory.stage = None
        memory.selected_doctor = None
        memory.last_department = None
        memory.age = None
        memory.gender = None
        memory.selected_time = None
        memory.selected_date = None
        return "❌ Cancelled. Let me know how else I can assist you!"

    elif intent == "fees_info":
        raw_fees = get_fees_info()
        prompt = (
            f"Here is the consultation fee range by department:\n\n{raw_fees}\n\n"
            f"Please respond like a helpful medical assistant. Summarize the departments in a **table format**, "
            f"including department name, min fee, max fee, average fee, and mention the most and least expensive departments overall."
        )
        return ask_gemini(prompt)

    elif intent == "availability_info":
        raw_availability = get_availability_info()
        prompt = f"Here is the doctor availability info:\n\n{raw_availability}\n\nRespond like a friendly assistant, summarizing which doctors are available today and which are available on other days."
        return ask_gemini(prompt)

    elif intent == "department_info":
        raw_departments = get_departments_and_counts()
        prompt = f"These are the available departments and the number of doctors in each:\n\n{raw_departments}\n\nPresent this information like a friendly assistant. Mention which departments are most staffed, try to explore department and invite the user to explore or ask about a department."
        return ask_gemini(prompt)

    elif intent == "general_query":
        info_prompt = f"""
Your name is Lumina, a warm, professional, and informative virtual medical assistant.

Your tone should be polite, empathetic, helpful, and conversational — like a real human assistant helping patients make informed decisions about their care.

You are assisting users by providing information about doctors, departments, qualifications, fees, and booking appointments.

Here are some of the available doctors:
{doctors_df[['Doctor Name', 'Department', 'Qualification']].head(5).to_string(index=False)}

The user said: "{text}"

Please respond clearly, naturally, and in a friendly manner – just as a real assistant named Lumina would.
"""
        return ask_gemini(info_prompt)

    fallback_prompt = f"""
Your name is Lumina — a smart, friendly, and helpful virtual medical assistant.

You assist patients in understanding symptoms, finding doctors, and navigating health services.

Known Doctors:
{doctors_df.head(5).to_string(index=False)}

Known Diseases:
{diseases_df.head(5).to_string(index=False)}

The user said: "{text}"

Please give a clear and helpful response. If you're unsure, kindly ask the user for clarification — always be friendly, polite and supportive.
"""
    return ask_gemini(fallback_prompt)
