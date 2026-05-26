import pandas as pd

data = [
    {
        "Serial Number": 1,
        "Student ID": "DEMO-112",
        "Name": "Demo Student A",
        "Hostel Block No": "Block 3",
        "Room Number": "102C",
        "Symptoms": "Severe rash, mild fever",
        "Prescribed Medicines": "Antihistamines, Paracetamol",
        "Mobile Number": "0000000001",
        "Date": "2026-03-25",
        "Notes": "Synthetic demo case. Measles ruled out."
    },
    {
        "Serial Number": 2,
        "Student ID": "DEMO-115",
        "Name": "Demo Student B",
        "Hostel Block No": "Block 1",
        "Room Number": "304A",
        "Symptoms": "Stomach ache, nausea, diarrhea",
        "Prescribed Medicines": "ORS, Domperidone",
        "Mobile Number": "0000000002",
        "Date": "2026-03-25",
        "Notes": "Synthetic demo case for food safety escalation."
    },
    {
        "Serial Number": 3,
        "Student ID": "DEMO-002",
        "Name": "Demo Student C",
        "Hostel Block No": "Block 2",
        "Room Number": "201B",
        "Symptoms": "Headache, fatigue",
        "Prescribed Medicines": "Ibuprofen",
        "Mobile Number": "0000000003",
        "Date": "2026-03-25",
        "Notes": "Synthetic demo case related to stress and rest."
    },
    {
        "Serial Number": 4,
        "Student ID": "DEMO-201",
        "Name": "Demo Student D",
        "Hostel Block No": "Block 4",
        "Room Number": "405D",
        "Symptoms": "Ankle swelling, acute pain",
        "Prescribed Medicines": "Diclofenac gel, Cold compress",
        "Mobile Number": "0000000004",
        "Date": "2026-03-26",
        "Notes": "Synthetic demo case for sports injury handling."
    },
    {
        "Serial Number": 5,
        "Student ID": "DEMO-045",
        "Name": "Demo Student E",
        "Hostel Block No": "Block 2",
        "Room Number": "112A",
        "Symptoms": "Dry cough, sore throat, no fever",
        "Prescribed Medicines": "Cough syrup, Lozenges",
        "Mobile Number": "0000000005",
        "Date": "2026-03-26",
        "Notes": "Synthetic demo case for allergy workflow."
    },
    {
        "Serial Number": 6,
        "Student ID": "DEMO-330",
        "Name": "Demo Student F",
        "Hostel Block No": "Block 1",
        "Room Number": "208C",
        "Symptoms": "High fever (102 F), body ache",
        "Prescribed Medicines": "Paracetamol (650mg), Vitamin C",
        "Mobile Number": "0000000006",
        "Date": "2026-03-26",
        "Notes": "Synthetic demo case for fever monitoring."
    },
    {
        "Serial Number": 7,
        "Student ID": "DEMO-098",
        "Name": "Demo Student G",
        "Hostel Block No": "Block 3",
        "Room Number": "303B",
        "Symptoms": "Redness in eyes, itching, discharge",
        "Prescribed Medicines": "Antibiotic eye drops",
        "Mobile Number": "0000000007",
        "Date": "2026-03-26",
        "Notes": "Synthetic demo case for temporary isolation guidance."
    },
    {
        "Serial Number": 8,
        "Student ID": "DEMO-156",
        "Name": "Demo Student H",
        "Hostel Block No": "Block 4",
        "Room Number": "501A",
        "Symptoms": "Shortness of breath, wheezing",
        "Prescribed Medicines": "Salbutamol Inhaler",
        "Mobile Number": "0000000008",
        "Date": "2026-03-26",
        "Notes": "Synthetic demo case for asthma-related support."
    }
]

df = pd.DataFrame(data)
df.to_excel("sample_doctor_report.xlsx", index=False)
print("Mock Excel sheet 'sample_doctor_report.xlsx' generated successfully.")
