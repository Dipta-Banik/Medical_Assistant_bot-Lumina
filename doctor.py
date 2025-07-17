import pandas as pd
from datetime import datetime
from difflib import SequenceMatcher
import re
import os

doctors_df = os.path.join(BASE_DIR, '..', 'Data', 'Doctor_List.csv')

def get_doctors_df():
    return doctors_df

def get_departments_and_counts():
    """Return list of departments and number of doctors in each."""
    dept_counts = doctors_df['Department'].value_counts()
    return "\n".join([f"🩺 {dept}: {count} doctor(s)" for dept, count in dept_counts.items()])



def get_doctors_by_department(user_input):
    """Identify the department from the input and return doctors in that department."""
    user_input = user_input.strip().lower()

    # Mapping from keywords to department names
    dept_words = {
        # Cardiology
        "cardio": "Cardiology", "cardiology": "Cardiology", "heart": "Cardiology",

        # Neurology
        "neuro": "Neurology", "neurology": "Neurology", "brain": "Neurology", "nerve": "Neurology",

        # Orthopedics
        "ortho": "Orthopedics", "orthopedics": "Orthopedics", "bone": "Orthopedics", "joint": "Orthopedics",

        # Pediatrics
        "pedia": "Pediatrics", "pediatrics": "Pediatrics", "child": "Pediatrics", "children": "Pediatrics", "kid": "Pediatrics",

        # ENT
        "ent": "ENT", "ear": "ENT", "nose": "ENT", "throat": "ENT",

        # Dermatology
        "derma": "Dermatology", "dermatology": "Dermatology", "skin": "Dermatology", "rash": "Dermatology",

        # General Surgery
        "surgery": "General Surgery", "surgeon": "General Surgery", "operation": "General Surgery",

        # Psychiatry
        "psych": "Psychiatry", "psychiatry": "Psychiatry", "mental": "Psychiatry",
        "depression": "Psychiatry", "anxiety": "Psychiatry", "stress": "Psychiatry", "psychology": "Psychiatry",

        # Ophthalmology
        "eye": "Ophthalmology", "eyes": "Ophthalmology", "vision": "Ophthalmology",
        "ophthalmology": "Ophthalmology", "sight": "Ophthalmology",

        # Gynecology
        "gyne": "Gynecology", "gynecology": "Gynecology", "women": "Gynecology",
        "pregnancy": "Gynecology", "obstetric": "Gynecology", "gynae": "Gynecology", "period": "Gynecology",

        # Urology
        "urology": "Urology", "urine": "Urology", "kidney": "Urology", "bladder": "Urology",

        # General Medicine
        "general": "General Medicine", "medicine": "General Medicine", "general medicine": "General Medicine",
        "internal": "General Medicine", "physician": "General Medicine", "fever": "General Medicine", "cold": "General Medicine",

        # Dental
        "dental": "Dental", "tooth": "Dental", "teeth": "Dental", "dentist": "Dental", "cavity": "Dental"
    }

    # Try to identify the department from the input using the mapping
    identified_dept = None
    for word in user_input.split():
        if word in dept_words:
            identified_dept = dept_words[word]
            break

    if not identified_dept:
        return "❌ Could not identify the department. Please try again with different keywords."

    # Filter doctors in the identified department
    df = doctors_df[doctors_df['Department'].str.lower() == identified_dept.lower()]
    if df.empty:
        return f"❌ No doctors found in '{identified_dept}'."
    
    # Return formatted list of doctors
    return f"✅ Doctors in {identified_dept}:\n" + "\n".join(
        [f"- {row['Doctor Name']} ({row['Qualification']}, ₹{row['Fees']})"
         for _, row in df.iterrows()]
    )







"""def get_doctors_by_department(dept_name):
    
    dept_name = dept_name.strip().lower()
    df = doctors_df[doctors_df['Department'].str.lower() == dept_name]
    if df.empty:
        return "❌ No such department found. Please check the name."
    return "\n".join(
        [f"- {row['Doctor Name']} ({row['Qualification']}, ₹{row['Fees']})"
         for _, row in df.iterrows()]
    )
"""
"""def get_fees_info():
    return doctors_df[['Doctor Name', 'Department', 'Fees']].to_string(index=False)"""
    
def get_fees_info():
    """Return fee range per department with doctor names and average fee insights."""
    summary = []

    grouped = doctors_df.groupby('Department')

    for dept, group in grouped:
        min_fee = group['Fees'].min()
        max_fee = group['Fees'].max()
        avg_fee = group['Fees'].mean()

        min_doctors = group[group['Fees'] == min_fee]['Doctor Name'].tolist()
        max_doctors = group[group['Fees'] == max_fee]['Doctor Name'].tolist()

        min_names = ', '.join(min_doctors)
        max_names = ', '.join(max_doctors)

        summary.append({
            'Department': dept,
            'Min Fee': min_fee,
            'Min Fee Doctor(s)': min_names,
            'Max Fee': max_fee,
            'Max Fee Doctor(s)': max_names,
            'Average Fee': round(avg_fee, 2)
        })

    return pd.DataFrame(summary).to_string(index=False)



def get_availability_info(doctor_name=None):
    """
    Returns:
    - If doctor_name is provided: that doctor's availability string (e.g., 'Mon-Wed-Fri (10am–1pm)')
    - If no doctor_name: returns the full dictionary of all doctors' availabilities
    """
    availability_dict = dict(zip(doctors_df['Doctor Name'], doctors_df['Available']))
    
    if doctor_name:
        return availability_dict.get(doctor_name)
    return availability_dict


def parse_availability_string(availability_str):
    """
    Converts 'Mon-Wed-Fri (10am–1pm)' → ['Monday', 'Wednesday', 'Friday'], ('10 AM', '1 PM')
    """
    days_map = {
        "Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday",
        "Thu": "Thursday", "Fri": "Friday", "Sat": "Saturday", "Sun": "Sunday"
    }
    
    day_abbrs = re.findall(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b', availability_str)
    full_days = [days_map[d] for d in day_abbrs]
    
    time_match = re.search(r'\(([\damp–\-–\s]+)\)', availability_str, re.IGNORECASE)
    if time_match:
        time_range = time_match.group(1).replace("–", "-").strip()
        start_time, end_time = [t.strip().upper() for t in re.split(r'-|–', time_range)]
    else:
        start_time, end_time = None, None

    return full_days, (start_time, end_time)


def is_doctor_available_on_date(doctor_name, selected_date_str):
    """
    Check if the doctor is available on the given date (e.g., '17 July').
    Returns a tuple (True, day_name, (start_time, end_time)) if available, else (False, day_name, None)
    """
    availability_info = get_availability_info()
    availability_str = availability_info.get(doctor_name)
    if not availability_str:
        return False, None, None
    try:
        date_obj = datetime.strptime(selected_date_str.strip().title(), "%d %B")
        date_obj = date_obj.replace(year=datetime.now().year)
        day_name = date_obj.strftime("%A")
    except ValueError:
        return False, None, None

    available_days, time_range = parse_availability_string(availability_str)

    if day_name in available_days:
        return True, day_name, time_range  # e.g., ('Wednesday', ('10 AM', '1 PM'))
    else:
        return False, day_name, None


def get_doctor_details(doctor_name):
    """Return detailed information of a specific doctor."""
    name = doctor_name.strip().lower()
    match = doctors_df[doctors_df['Doctor Name'].str.lower().str.contains(name)]
    if match.empty:
        return "❌ Doctor not found."
    row = match.iloc[0]
    return (
        f"👨‍⚕️ **{row['Doctor Name']}**\n"
        f"📚 Qualification: {row['Qualification']}\n"
        f"💼 Experience: {row['Experience']} yrs\n"
        f"🩺 Department: {row['Department']}\n"
        f"💰 Fees: ₹{row['Fees']}\n"
        f"⏰ Available: {row['Available']}"
    )


def extract_doctor_name(text):
    """Extract the best matching doctor name from text."""
    text = text.lower()
    best_match = None
    best_score = 0.0

    for doctor in doctors_df['Doctor Name']:
        doctor_lower = doctor.lower()

        # Direct match
        if doctor_lower in text:
            return doctor

        # Fuzzy match
        ratio = SequenceMatcher(None, doctor_lower, text).ratio()
        if ratio > best_score and ratio > 0.6: 
            best_score = ratio
            best_match = doctor

    return best_match


"""def extract_department(text):
    
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)

    for word in words:
        if word in department_keywords:
            return department_keywords[word]

    return None"""

def extract_department(text):
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)

    for dept in doctors_df['Department'].unique():
        dept_words = dept.lower().split()
        if all(word in words for word in dept_words):
            return dept

def doctor_info():
    """Return readable format of a doctor DataFrame subset."""
    df = get_doctors_df()
    grouped = df.groupby('Department')

    output = ""
    for dept, group in grouped:
        output += f"\n🩺 {dept}:\n"
        for _, row in group.iterrows():
            output += f"- {row['Doctor Name']} ({row['Qualification']})\n"

    return output.strip()

