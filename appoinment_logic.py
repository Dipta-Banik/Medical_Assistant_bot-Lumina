import re
import dns.resolver
from datetime import datetime, timedelta
from doctor import (
    extract_doctor_name,
    extract_department,
    get_doctor_details,
    get_doctors_by_department,
    get_departments_and_counts,
    get_fees_info,
    get_availability_info,
    get_doctors_df,
    doctor_info
)

def is_valid_name(name):
    return bool(re.match(r"^[A-Z][a-z]+(?: [A-Z][a-z]+)*$", name.strip()))

def is_valid_age(age):
    return age.isdigit() and 0 < int(age) < 120

def is_valid_gender(gender):
    gender = gender.strip().lower()
    if gender in ['male', 'm', 'M', 'MALE']:
        return 'Male'
    elif gender in ['female', 'f', 'F', 'FEMALE']:
        return 'Female'
    else:
        return None 

def is_valid_date(dt_text):
    """
    Check if the input is a valid date (e.g., '15 July') and is not in the past.
    Returns True if valid, else False.
    """
    try:
        # Parse date assuming current year
        input_date = datetime.strptime(dt_text.strip().title(), "%d %B")
        input_date = input_date.replace(year=datetime.now().year)
        
        # Compare with today's date
        today = datetime.now().date()
        if input_date.date() < today:
            return False
        return True
    except ValueError:
        return False


def is_valid_time(time_text):
    """
    Check if the input is a valid time string (e.g., '3 PM').
    Returns True if valid, else False.
    """
    try:
        datetime.strptime(time_text.strip().upper(), "%I %p")
        return True
    except ValueError:
        return False
    
   
def get_next_slots(doctor_name, n=5):
    """
    Suggests the next 'n' available slots for the given doctor.
    Returns a list of strings like ['17 July, 10 AM', '17 July, 3 PM', ...]
    """
    today = datetime.now()
    slots = []

    availability = get_availability_info.get(doctor_name)
    if not availability:
        return ["❌ Doctor's availability not found."]

    available_days = availability["days"]
    available_times = availability["times"]

    # Loop through the next 14 days to find up to n slots
    for day_offset in range(0, 14):
        date_candidate = today + timedelta(days=day_offset)
        weekday_name = date_candidate.strftime("%A")

        if weekday_name in available_days:
            for time_str in available_times:
                try:
                    time_obj = datetime.strptime(time_str, "%I %p").time()
                    combined_datetime = datetime.combine(date_candidate.date(), time_obj)

                    if combined_datetime > today:
                        formatted = combined_datetime.strftime("%d %B, %I %p")
                        slots.append(formatted)

                        if len(slots) >= n:
                            return slots
                except ValueError:
                    continue

    return slots if slots else ["❌ No available slots in the next 14 days."]



def is_valid_email(email):
    """
    Validate email format and check if domain has valid MX DNS records.
    """
    if not isinstance(email, str):
        return False

    email = email.strip()

    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(regex, email):
        return False

    if ".." in email or email.startswith(".") or email.endswith(".") or email.count("@") != 1:
        return False
    try:
        domain = email.split("@")[1]
        dns.resolver.resolve(domain, 'MX')
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.resolver.Timeout):
        return False

    return True


