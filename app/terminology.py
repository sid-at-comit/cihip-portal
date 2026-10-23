"""
Terminology Services: SNOMED CT & LOINC Dictionaries
Aligned with NRCeS (National Resource Centre for EHR Standards) & ABDM FHIR IG v6.5.0
"""

# LOINC Standard Laboratory Observations Catalog
LOINC_CATALOG = {
    "718-7": {
        "code": "718-7",
        "name": "Hemoglobin [Mass/volume] in Blood",
        "display": "Hemoglobin (Hb)",
        "department": "Hematology",
        "unit": "g/dL",
        "low_ref": 12.0,
        "high_ref": 16.5,
        "critical_low": 7.0,
        "critical_high": 20.0,
        "specimen": "Whole Blood (EDTA)",
    },
    "14804-9": {
        "code": "14804-9",
        "name": "Hemoglobin A1c/Hemoglobin.total in Blood by HPLC",
        "display": "Glycated Hemoglobin (HbA1c)",
        "department": "Biochemistry",
        "unit": "%",
        "low_ref": 4.0,
        "high_ref": 5.6,
        "critical_low": 3.5,
        "critical_high": 11.0,
        "specimen": "Whole Blood (EDTA)",
    },
    "2345-7": {
        "code": "2345-7",
        "name": "Glucose [Mass/volume] in Serum or Plasma -- Fasting",
        "display": "Fasting Blood Glucose (FBS)",
        "department": "Biochemistry",
        "unit": "mg/dL",
        "low_ref": 70.0,
        "high_ref": 99.0,
        "critical_low": 50.0,
        "critical_high": 300.0,
        "specimen": "Fluoride Plasma",
    },
    "2093-3": {
        "code": "2093-3",
        "name": "Cholesterol [Mass/volume] in Serum or Plasma",
        "display": "Total Cholesterol",
        "department": "Biochemistry",
        "unit": "mg/dL",
        "low_ref": 125.0,
        "high_ref": 200.0,
        "critical_low": 90.0,
        "critical_high": 350.0,
        "specimen": "Serum",
    },
    "2085-9": {
        "code": "2085-9",
        "name": "Cholesterol in HDL [Mass/volume] in Serum or Plasma",
        "display": "HDL Cholesterol (Good)",
        "department": "Biochemistry",
        "unit": "mg/dL",
        "low_ref": 40.0,
        "high_ref": 60.0,
        "critical_low": 25.0,
        "critical_high": 90.0,
        "specimen": "Serum",
    },
    "13457-7": {
        "code": "13457-7",
        "name": "Cholesterol in LDL [Mass/volume] in Serum or Plasma",
        "display": "LDL Cholesterol (Calculated)",
        "department": "Biochemistry",
        "unit": "mg/dL",
        "low_ref": 50.0,
        "high_ref": 100.0,
        "critical_low": 30.0,
        "critical_high": 190.0,
        "specimen": "Serum",
    },
    "2160-0": {
        "code": "2160-0",
        "name": "Creatinine [Mass/volume] in Serum or Plasma",
        "display": "Serum Creatinine",
        "department": "Nephrology / Biochemistry",
        "unit": "mg/dL",
        "low_ref": 0.7,
        "high_ref": 1.3,
        "critical_low": 0.4,
        "critical_high": 4.0,
        "specimen": "Serum",
    },
    "26464-8": {
        "code": "26464-8",
        "name": "Leukocytes [#/volume] in Blood",
        "display": "Total Leukocyte Count (TLC/WBC)",
        "department": "Hematology",
        "unit": "10^3/uL",
        "low_ref": 4.0,
        "high_ref": 11.0,
        "critical_low": 2.0,
        "critical_high": 30.0,
        "specimen": "Whole Blood (EDTA)",
    },
    "1975-2": {
        "code": "1975-2",
        "name": "Bilirubin.total [Mass/volume] in Serum or Plasma",
        "display": "Serum Bilirubin (Total)",
        "department": "Gastroenterology / Biochemistry",
        "unit": "mg/dL",
        "low_ref": 0.2,
        "high_ref": 1.2,
        "critical_low": 0.1,
        "critical_high": 10.0,
        "specimen": "Serum",
    },
    "2823-3": {
        "code": "2823-3",
        "name": "Potassium [Moles/volume] in Serum or Plasma",
        "display": "Serum Potassium",
        "department": "Biochemistry",
        "unit": "mmol/L",
        "low_ref": 3.5,
        "high_ref": 5.1,
        "critical_low": 2.8,
        "critical_high": 6.5,
        "specimen": "Serum",
    },
    "2951-2": {
        "code": "2951-2",
        "name": "Sodium [Moles/volume] in Serum or Plasma",
        "display": "Serum Sodium",
        "department": "Biochemistry",
        "unit": "mmol/L",
        "low_ref": 136.0,
        "high_ref": 145.0,
        "critical_low": 120.0,
        "critical_high": 160.0,
        "specimen": "Serum",
    },
}

# SNOMED CT Clinical Diagnoses & Findings
SNOMED_DIAGNOSES = {
    "44054006": {
        "code": "44054006",
        "name": "Type 2 diabetes mellitus (disorder)",
        "display": "Type 2 Diabetes Mellitus",
        "department": "Endocrinology",
    },
    "38341003": {
        "code": "38341003",
        "name": "Essential hypertension (disorder)",
        "display": "Essential Hypertension",
        "department": "Cardiology",
    },
    "53741008": {
        "code": "53741008",
        "name": "Coronary arteriosclerosis (disorder)",
        "display": "Coronary Artery Disease (CAD)",
        "department": "Cardiology",
    },
    "195967001": {
        "code": "195967001",
        "name": "Asthma (disorder)",
        "display": "Bronchial Asthma",
        "department": "Pulmonology",
    },
    "233604007": {
        "code": "233604007",
        "name": "Pneumonia (disorder)",
        "display": "Bacterial Pneumonia",
        "department": "Pulmonology",
    },
    "840539008": {
        "code": "840539008",
        "name": "Disease caused by Severe acute respiratory syndrome coronavirus 2 (disorder)",
        "display": "COVID-19 Infection",
        "department": "Infectious Disease",
    },
    "363346000": {
        "code": "363346000",
        "name": "Malignant neoplastic disease (disorder)",
        "display": "Oncology / Malignancy",
        "department": "Oncology",
    },
    "709044004": {
        "code": "709044004",
        "name": "Chronic kidney disease (disorder)",
        "display": "Chronic Kidney Disease (CKD)",
        "department": "Nephrology",
    },
    "235595009": {
        "code": "235595009",
        "name": "Gastroesophageal reflux disease (disorder)",
        "display": "GERD",
        "department": "Gastroenterology",
    },
    "414545008": {
        "code": "414545008",
        "name": "Ischemic stroke (disorder)",
        "display": "Acute Ischemic Stroke",
        "department": "Neurology",
    },
}

# SNOMED CT / Indian National Formulary Medications
MEDICATIONS_CATALOG = {
    "MED-MET-500": {
        "code": "372567009",
        "name": "Metformin hydrochloride 500 mg oral tablet",
        "display": "Tab. Metformin HCl 500 mg",
        "default_dosage": "500 mg",
        "default_frequency": "1-0-1 (Twice daily after meals)",
        "route": "Oral",
        "duration": "30 days",
        "indication": "Type 2 Diabetes Mellitus",
    },
    "MED-TEL-40": {
        "code": "386864001",
        "name": "Telmisartan 40 mg oral tablet",
        "display": "Tab. Telmisartan 40 mg",
        "default_dosage": "40 mg",
        "default_frequency": "1-0-0 (Once daily morning)",
        "route": "Oral",
        "duration": "30 days",
        "indication": "Essential Hypertension",
    },
    "MED-ATO-20": {
        "code": "387584000",
        "name": "Atorvastatin 20 mg oral tablet",
        "display": "Tab. Atorvastatin 20 mg",
        "default_dosage": "20 mg",
        "default_frequency": "0-0-1 (Once daily at bedtime)",
        "route": "Oral",
        "duration": "30 days",
        "indication": "Hyperlipidemia / CAD",
    },
    "MED-AMOX-500": {
        "code": "372687004",
        "name": "Amoxicillin 500 mg oral capsule",
        "display": "Cap. Amoxicillin 500 mg",
        "default_dosage": "500 mg",
        "default_frequency": "1-1-1 (Thrice daily)",
        "route": "Oral",
        "duration": "5 days",
        "indication": "Bacterial Infection",
    },
    "MED-PCM-650": {
        "code": "387591000",
        "name": "Paracetamol 650 mg oral tablet",
        "display": "Tab. Paracetamol 650 mg",
        "default_dosage": "650 mg",
        "default_frequency": "SOS (As needed, max 3x daily)",
        "route": "Oral",
        "duration": "3 days",
        "indication": "Fever & Pain Relief",
    },
    "MED-PANTO-40": {
        "code": "386965005",
        "name": "Pantoprazole 40 mg oral tablet",
        "display": "Tab. Pantoprazole 40 mg",
        "default_dosage": "40 mg",
        "default_frequency": "1-0-0 (30 mins before breakfast)",
        "route": "Oral",
        "duration": "14 days",
        "indication": "GERD / Gastric Acidity",
    },
    "MED-AZI-500": {
        "code": "386962008",
        "name": "Azithromycin 500 mg oral tablet",
        "display": "Tab. Azithromycin 500 mg",
        "default_dosage": "500 mg",
        "default_frequency": "1-0-0 (Once daily)",
        "route": "Oral",
        "duration": "3 days",
        "indication": "Respiratory Tract Infection",
    },
    "MED-SAL-INH": {
        "code": "372833007",
        "name": "Salbutamol 100 mcg inhaler",
        "display": "Salbutamol MDI 100 mcg",
        "default_dosage": "2 puffs",
        "default_frequency": "SOS (During acute wheeze/breathlessness)",
        "route": "Inhalation",
        "duration": "30 days",
        "indication": "Asthma / Bronchospasm",
    },
}

def evaluate_lab_result(loinc_code: str, numeric_val: float):
    """Evaluate numeric value against reference ranges and return flag."""
    meta = LOINC_CATALOG.get(loinc_code)
    if not meta:
        return "Normal", f"N/A"
    
    ref_str = f"{meta['low_ref']} - {meta['high_ref']} {meta['unit']}"
    if numeric_val < meta["critical_low"] or numeric_val > meta["critical_high"]:
        flag = "Critical"
    elif numeric_val < meta["low_ref"]:
        flag = "Low"
    elif numeric_val > meta["high_ref"]:
        flag = "High"
    else:
        flag = "Normal"
        
    return flag, ref_str
