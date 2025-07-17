import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from doctor import get_doctors_df, extract_department
import re
import os

dept_words = {
    # Cardiology
    "cardio": "Cardiology",
    "cardiology": "Cardiology",
    "heart": "Cardiology",

    # Neurology
    "neuro": "Neurology",
    "neurology": "Neurology",
    "brain": "Neurology",
    "nerve": "Neurology",

    # Orthopedics
    "ortho": "Orthopedics",
    "orthopedics": "Orthopedics",
    "bone": "Orthopedics",
    "joint": "Orthopedics",

    # Pediatrics
    "pedia": "Pediatrics",
    "pediatrics": "Pediatrics",
    "child": "Pediatrics",
    "children": "Pediatrics",
    "kid": "Pediatrics",

    # ENT
    "ent": "ENT",
    "ear": "ENT",
    "nose": "ENT",
    "throat": "ENT",

    # Dermatology
    "derma": "Dermatology",
    "dermatology": "Dermatology",
    "skin": "Dermatology",
    "rash": "Dermatology",

    # General Surgery
    "surgery": "General Surgery",
    "surgeon": "General Surgery",
    "operation": "General Surgery",

    # Psychiatry
    "psych": "Psychiatry",
    
    
    "psychiatry": "Psychiatry",
    "mental": "Psychiatry",
    "depression": "Psychiatry",
    "anxiety": "Psychiatry",
    "stress": "Psychiatry",
    "psychology": "Psychiatry",

    # Ophthalmology
    "eye": "Ophthalmology",
    "eyes": "Ophthalmology",
    "vision": "Ophthalmology",
    "ophthalmology": "Ophthalmology",
    "sight": "Ophthalmology",

    # Gynecology
    "gyne": "Gynecology",
    "gynecology": "Gynecology",
    "women": "Gynecology",
    "pregnancy": "Gynecology",
    "obstetric": "Gynecology",
    "gynae": "Gynecology",
    "period": "Gynecology",

    # Urology
    "urology": "Urology",
    "urine": "Urology",
    "kidney": "Urology",
    "bladder": "Urology",

    # General Medicine
    "general": "General Medicine",
    "medicine": "General Medicine",
    "general medicine": "General Medicine",
    "internal": "General Medicine",
    "physician": "General Medicine",
    "fever": "General Medicine",
    "cold": "General Medicine",

    # Dental
    "dental": "Dental",
    "tooth": "Dental",
    "teeth": "Dental",
    "dentist": "Dental",
    "cavity": "Dental"
}


doctors_df = get_doctors_df()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DISEASES_PATH = os.path.join(BASE_DIR, '..', 'Data', 'Disease_List.csv')

diseases_df = pd.read_csv(DISEASES_PATH)


diseases_df['Symptoms'] = diseases_df['Symptoms'].str.lower()
doctors_df = get_doctors_df()

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(diseases_df['Symptoms'])

def get_diseases_df():
    return diseases_df

def extract_department_from_input(text):
    words = re.findall(r'\b\w+\b', text.lower())
    for word in words:
        if word in dept_words:
            return dept_words[word]
    return None

def match_symptoms(user_input, doctors_df, diseases_df, top_n=2, threshold=0.2):
    user_input = user_input.lower()
    matches = []

    dept = extract_department_from_input(user_input)
    if dept:
        # Filter diseases related to that department
        filtered_df = diseases_df[diseases_df['Department'] == dept]
        for _, row in filtered_df.iterrows():
            doctor_info = recommend_doctor(dept, doctors_df)
            matches.append({
                "Disease": row["Disease"],
                "Department": dept,
                "Quick Action": row["Quick Action"],
                "Doctor Recommendation": doctor_info
            })
        return matches[:top_n]  # Return top_n if too many
    else:
        # Step 2: Fall back to semantic similarity
        user_vec = vectorizer.transform([user_input])
        similarities = cosine_similarity(user_vec, tfidf_matrix)[0]
        top_indices = similarities.argsort()[-top_n:][::-1]

        for idx in top_indices:
            if similarities[idx] >= threshold:
                row = diseases_df.iloc[idx]
                dept = row['Department']
                doctor_info = recommend_doctor(dept, doctors_df)

                matches.append({
                    "Disease": row["Disease"],
                    "Department": dept,
                    "Quick Action": row["Quick Action"],
                    "Doctor Recommendation": doctor_info
                })

    return matches


def recommend_doctor(department, doctors_df):
    doctors = doctors_df[doctors_df['Department'].str.lower() == department.lower()]
    if not doctors.empty:
        doc = doctors.iloc[0]
        return f"👨‍⚕️ Recommended Doctor: Dr. {doc['Doctor Name']} ({doc['Department']})"
    return f"No doctor found in {department}."
