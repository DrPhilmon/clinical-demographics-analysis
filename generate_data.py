import csv
import random
import os

random.seed(42)

NUM_PATIENTS  = 200
GENDERS       = ["Male", "Female"]
BLOOD_GROUPS  = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
CONDITIONS    = ["Hypertension", "Diabetes Type 2", "Asthma",
                 "Chronic Kidney Disease", "None"]
DEPARTMENTS   = ["Cardiology", "Endocrinology", "Pulmonology",
                 "Nephrology", "General Medicine"]
NATIONALITIES = ["Nigerian", "Ghanaian", "Kenyan", "South African",
                 "Ethiopian", "British", "American", "Indian"]
WEIGHT_RANGE  = {"Male": (60, 110), "Female": (50, 95)}

def generate_patient(patient_id):
    gender   = random.choice(GENDERS)
    age      = random.randint(18, 85)
    weight   = round(random.uniform(*WEIGHT_RANGE[gender]), 1)
    height   = round(random.uniform(1.50, 1.95), 2)
    bmi      = round(weight / (height ** 2), 1)
    systolic = random.randint(100 + age // 5, 160 + age // 5)
    return {
        "patient_id":        f"PT{patient_id:04d}",
        "age":               age,
        "gender":            gender,
        "blood_group":       random.choice(BLOOD_GROUPS),
        "nationality":       random.choice(NATIONALITIES),
        "weight_kg":         weight,
        "height_m":          height,
        "bmi":               bmi,
        "systolic_bp":       systolic,
        "diastolic_bp":      random.randint(60, 100),
        "primary_condition": random.choice(CONDITIONS),
        "department":        random.choice(DEPARTMENTS),
    }

FIELDNAMES = ["patient_id","age","gender","blood_group","nationality",
              "weight_kg","height_m","bmi","systolic_bp","diastolic_bp",
              "primary_condition","department"]

os.makedirs("data", exist_ok=True)
with open("data/patients.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    writer.writeheader()
    for i in range(1, NUM_PATIENTS + 1):
        writer.writerow(generate_patient(i))

print(f"Done! Generated data/patients.csv with {NUM_PATIENTS} patients")


import csv

def load_patients(filepath):
    patients = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            patients.append(row)
    return patients

patients = load_patients("data/patients.csv")

print(f"Total patients loaded: {len(patients)}")
print("\nColumn names:", list(patients[0].keys()))
print("\nFirst patient:")
for key, value in patients[0].items():
    print(f"  {key:20s} : {value}")


def classify_age_group(age_str):
    age = int(age_str)
    if age <= 35:
        return "Young Adult (18-35)"
    elif age <= 50:
        return "Middle-Aged Adult (36-50)"
    elif age <= 65:
        return "Older Adult (51-65)"
    else:
        return "Elderly (66+)"

# Test it manually before using it on real data
print(classify_age_group("22"))
print(classify_age_group("45"))
print(classify_age_group("60"))
print(classify_age_group("75"))


from collections import defaultdict

def group_by_age(patients):
    groups = defaultdict(list)
    for patient in patients:
        label = classify_age_group(patient["age"])
        groups[label].append(patient)
    return groups

groups = group_by_age(patients)

print("Patients per age group:")
for label, group in groups.items():
    pct = len(group) / len(patients) * 100
    print(f"  {label:35s}: {len(group)} patients ({pct:.1f}%)")


from collections import Counter

def summarise_group(group_patients):
    n = len(group_patients)

    avg_bmi       = sum(float(p["bmi"])          for p in group_patients) / n
    avg_systolic  = sum(float(p["systolic_bp"])  for p in group_patients) / n
    avg_diastolic = sum(float(p["diastolic_bp"]) for p in group_patients) / n

    gender_counts    = Counter(p["gender"] for p in group_patients)
    pct_male         = (gender_counts["Male"] / n) * 100

    condition_counts = Counter(p["primary_condition"] for p in group_patients)
    top_condition, top_count = condition_counts.most_common(1)[0]

    hypertensive = sum(1 for p in group_patients if float(p["systolic_bp"]) >= 140)

    bmi_cats = Counter()
    for p in group_patients:
        bmi = float(p["bmi"])
        if bmi < 18.5:   bmi_cats["Underweight"] += 1
        elif bmi < 25.0: bmi_cats["Normal"] += 1
        elif bmi < 30.0: bmi_cats["Overweight"] += 1
        else:            bmi_cats["Obese"] += 1

    return {
        "n":                 n,
        "avg_bmi":           round(avg_bmi, 1),
        "avg_systolic":      round(avg_systolic, 1),
        "avg_diastolic":     round(avg_diastolic, 1),
        "pct_male":          round(pct_male, 1),
        "top_condition":     top_condition,
        "pct_top_condition": round(top_count / n * 100, 1),
        "pct_hypertensive":  round(hypertensive / n * 100, 1),
        "bmi_categories":    dict(bmi_cats),
    }

# Test on just the Young Adults first
young_adults = groups["Young Adult (18-35)"]
stats = summarise_group(young_adults)
print("Young Adult stats:")
for key, value in stats.items():
    print(f"  {key:20s} : {value}")


AGE_GROUP_ORDER = [
    "Young Adult (18-35)",
    "Middle-Aged Adult (36-50)",
    "Older Adult (51-65)",
    "Elderly (66+)",
]

divider = "=" * 60
print(f"\n{divider}")
print("  PATIENT DEMOGRAPHICS ANALYSIS - CLINICAL SUMMARY")
print(divider)
print(f"  Total patients: {len(patients)}")
print(divider)

for group_label in AGE_GROUP_ORDER:
    if group_label not in groups:
        continue
    s = summarise_group(groups[group_label])
    print(f"\n  >> {group_label}")
    print(f"     Patients        : {s['n']} ({s['n']/len(patients)*100:.1f}% of total)")
    print(f"     Gender (% male) : {s['pct_male']}%")
    print(f"     Mean BMI        : {s['avg_bmi']} kg/m2")
    print(f"     Mean BP         : {s['avg_systolic']}/{s['avg_diastolic']} mmHg")
    print(f"     Elevated BP     : {s['pct_hypertensive']}%")
    print(f"     Top condition   : {s['top_condition']} ({s['pct_top_condition']}%)")
    bmi_parts = [f"{cat}: {s['bmi_categories'].get(cat,0)}"
                 for cat in ["Underweight","Normal","Overweight","Obese"]
                 if s['bmi_categories'].get(cat,0) > 0]
    print(f"     BMI breakdown   : {'  |  '.join(bmi_parts)}")

print(f"\n{divider}")
print("  END OF REPORT")
print(f"{divider}\n")


def filter_by_age_group(patients, target_group):
    return [
        p for p in patients
        if classify_age_group(p["age"]) == target_group
    ]

elderly = filter_by_age_group(patients, "Elderly (66+)")
stats   = summarise_group(elderly)

print(f"Elderly patients: {stats['n']}")
print(f"Mean systolic BP: {stats['avg_systolic']} mmHg")
print(f"% elevated BP   : {stats['pct_hypertensive']}%")
print(f"Top condition   : {stats['top_condition']}")
