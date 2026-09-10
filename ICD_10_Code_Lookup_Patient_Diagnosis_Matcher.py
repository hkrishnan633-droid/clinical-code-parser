import json
import os
import pandas as pd

csv_file_path = "codes.csv"
json_cache_path = "clinical_lookup_cache.json"

if not os.path.exists(csv_file_path):
    pd.DataFrame({
        "code": ["E11.9 ", " 001.1", "99203"], 
        "description": ["Type 2 diabetes", "Cholera due to Vibrio cholerae 01", "Office visit"],
        "code_system": ["ICD-10", "icd-9", "CPT"]
    }).to_csv(csv_file_path, index=False)
    
print("📖Reading clinical CSV file...")
    
df=pd.read_csv(csv_file_path,dtype={"code":str,"descrption":str,"code_system":str})

print("🧹 Parsing strings and cleaning dataset...")

df=df.dropna(subset=["code","description"])

df["code"]=df["code"].str.strip()
df["description"]=df["description"].str.strip()

if "code_system" in df.columns:
    df["code_system"] = df["code_system"].str.strip().str.upper()

print("🏗️ Structuring lookup dictionary...")

lookup_dict = {}

if "code_system" in df.columns:
    for system_name,group in df.groupby("code_system"):
        lookup_dict[system_name]= dict(zip(group["code"],group["description"]))
else:
    lookup_dict = dict(zip(df["code"],df["description"]))

print(f"💾 Saving processed dictionary to JSON cache: {json_cache_path}...")
with open(json_cache_path, "w", encoding="utf-8") as json_file:
    json.dump(lookup_dict, json_file, indent=4, ensure_ascii=False)
        
print("✅ Pipeline complete. Cache saved.")

print("-" * 50)
if os.path.exists(json_cache_path):
    print("⚡ Found existing cache! Loading dictionary directly from JSON...")
    with open(json_cache_path, "r", encoding="utf-8") as json_file:
        clinical_lookup = json.load(json_file)
else:
    print("ℹ️ Cache not found. Initialising data pipeline...")
    clinical_lookup = build_and_cache_lookup()
print("-" * 50)

def find_medical_description(system: str, medical_code: str) -> str:
    """Queries the built dictionary structure safely without risking key exceptions."""
    sys_key = str(system).strip().upper()
    code_key = str(medical_code).strip()
    
    system_bucket = clinical_lookup.get(sys_key, {})
    return system_bucket.get(code_key, f"⚠️ Code '{code_key}' not found in system '{sys_key}'")

print("🔍 Running test lookups against the system:")
print(f"Result 1: {find_medical_description('icd-10', 'E11.9')}")
print(f"Result 2: {find_medical_description('ICD-9', '001.1')}") 
print(f"Result 3: {find_medical_description('ICD-10', 'INVALID')}")