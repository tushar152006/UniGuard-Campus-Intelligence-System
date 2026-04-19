import pandas as pd
from datetime import datetime, timedelta

data = [
    {
        "Serial Number": 1,
        "Student ID": "ST2026112",
        "Name": "Sneha Patel",
        "Hostel Block No": "Block 3",
        "Room Number": "102C",
        "Symptoms": "Severe rash, mild fever",
        "Prescribed Medicines": "Antihistamines, Paracetamol",
        "Mobile Number": "9876543210",
        "Date": "2026-03-25",
        "Notes": "Observation for 24 hrs. Not measles."
    },
    {
        "Serial Number": 2,
        "Student ID": "ST2026115",
        "Name": "Rohan Sharma",
        "Hostel Block No": "Block 1",
        "Room Number": "304A",
        "Symptoms": "Stomach ache, nausea, diarrhea",
        "Prescribed Medicines": "ORS, Domperidone",
        "Mobile Number": "9876543211",
        "Date": "2026-03-25",
        "Notes": "Suspected food poisoning from mess food. Check mess hygiene."
    },
    {
        "Serial Number": 3,
        "Student ID": "ST2026002",
        "Name": "Aisha Khan",
        "Hostel Block No": "Block 2",
        "Room Number": "201B",
        "Symptoms": "Headache, fatigue",
        "Prescribed Medicines": "Ibuprofen",
        "Mobile Number": "9876543212",
        "Date": "2026-03-25",
        "Notes": "Stress-related, advised rest."
    },
    {
        "Serial Number": 4,
        "Student ID": "ST2026201",
        "Name": "Arjun Das",
        "Hostel Block No": "Block 4",
        "Room Number": "405D",
        "Symptoms": "Ankle swelling, acute pain",
        "Prescribed Medicines": "Diclofenac gel, Cold compress",
        "Mobile Number": "9876543213",
        "Date": "2026-03-26",
        "Notes": "Sprained ankle during basketball practice. Advised RICE protocol."
    },
    {
        "Serial Number": 5,
        "Student ID": "ST2026045",
        "Name": "Meera Iyer",
        "Hostel Block No": "Block 2",
        "Room Number": "112A",
        "Symptoms": "Dry cough, sore throat, no fever",
        "Prescribed Medicines": "Cough syrup, Lozenges",
        "Mobile Number": "9876543214",
        "Date": "2026-03-26",
        "Notes": "Possible dust allergy. Advised salt water gargles."
    },
    {
        "Serial Number": 6,
        "Student ID": "ST2026330",
        "Name": "Vikram Singh",
        "Hostel Block No": "Block 1",
        "Room Number": "208C",
        "Symptoms": "High fever (102°F), body ache",
        "Prescribed Medicines": "Paracetamol (650mg), Vitamin C",
        "Mobile Number": "9876543215",
        "Date": "2026-03-26",
        "Notes": "Viral fever suspected. Blood test ordered if fever persists."
    },
    {
        "Serial Number": 7,
        "Student ID": "ST2026098",
        "Name": "Ananya Reddy",
        "Hostel Block No": "Block 3",
        "Room Number": "303B",
        "Symptoms": "Redness in eyes, itching, discharge",
        "Prescribed Medicines": "Antibiotic eye drops",
        "Mobile Number": "9876543216",
        "Date": "2026-03-26",
        "Notes": "Viral Conjunctivitis. Advised to stay in room to prevent spread."
    },
    {
        "Serial Number": 8,
        "Student ID": "ST2026156",
        "Name": "Kevin D'Souza",
        "Hostel Block No": "Block 4",
        "Room Number": "501A",
        "Symptoms": "Shortness of breath, wheezing",
        "Prescribed Medicines": "Salbutamol Inhaler",
        "Mobile Number": "9876543217",
        "Date": "2026-03-26",
        "Notes": "History of Asthma. Triggered by high pollen count today."
    }
]

df = pd.DataFrame(data)
df.to_excel("sample_doctor_report.xlsx", index=False)
print("Mock Excel sheet 'sample_doctor_report.xlsx' generated successfully.")
