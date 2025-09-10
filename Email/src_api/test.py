import os 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUSINESS_SUBJECT_PATH = os.path.join(BASE_DIR, "..", "business", "business_subject_sample.txt")

with open (BUSINESS_SUBJECT_PATH, "r", encoding="utf-8") as f:
    BUSINESS_SUBJECT = f.read().strip()
print(BUSINESS_SUBJECT)