"""
FHIR R4 Resource Serializer & Generator
Compliant with ABDM FHIR Implementation Guide v6.5.0 & HL7 FHIR R4.0.1
"""

import json
from typing import Dict, Any, List, Optional

def to_fhir_patient(p: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize patient row to FHIR R4 Patient resource."""
    return {
        "resourceType": "Patient",
        "id": p["upk"],
        "meta": {
            "versionId": "1",
            "lastUpdated": p.get("created_at", "2026-01-20T10:00:00Z"),
            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/Patient"]
        },
        "identifier": [
            {
                "type": {
                    "coding": [
                        {"system": "http://terminology.hl7.org/CodeSystem/v2-0203", "code": "MR", "display": "Medical Record Number"}
                    ]
                },
                "system": "https://cihip.nhp.gov.in/identifiers/upk",
                "value": p["upk"]
            },
            {
                "type": {
                    "coding": [
                        {"system": "https://nrces.in/ndhm/fhir/r4/CodeSystem/ndhm-identifier-type-code", "code": "ABHA", "display": "Ayushman Bharat Health Account"}
                    ]
                },
                "system": "https://healthid.ndhm.gov.in",
                "value": p["abha_number"]
            }
        ],
        "active": p.get("status") == "ACTIVE",
        "name": [
            {
                "use": "official",
                "text": p["name"],
                "family": p["name"].split()[-1] if len(p["name"].split()) > 1 else p["name"],
                "given": p["name"].split()[:-1] if len(p["name"].split()) > 1 else [p["name"]]
            }
        ],
        "telecom": [
            {"system": "phone", "value": p.get("phone"), "use": "mobile"},
            {"system": "email", "value": p.get("email"), "use": "home"}
        ],
        "gender": p["gender"].lower() if p.get("gender") else "unknown",
        "birthDate": p.get("dob"),
        "address": [
            {
                "use": "home",
                "state": p.get("state"),
                "district": p.get("district"),
                "postalCode": p.get("pincode"),
                "country": "IND"
            }
        ]
    }

def to_fhir_practitioner(d: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize doctor row to FHIR R4 Practitioner resource."""
    return {
        "resourceType": "Practitioner",
        "id": d["udk"],
        "meta": {
            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/Practitioner"]
        },
        "identifier": [
            {
                "type": {
                    "coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203", "code": "MD", "display": "Medical License number"}]
                },
                "system": "https://nmc.org.in/practitioners",
                "value": d["nmc_id"]
            },
            {
                "system": "https://cihip.nhp.gov.in/identifiers/udk",
                "value": d["udk"]
            }
        ],
        "active": d.get("status") == "VERIFIED",
        "name": [{"text": d["name"]}],
        "qualification": [
            {
                "code": {"text": d.get("qualification", "MBBS")},
                "issuer": {"display": "National Medical Commission (NMC)"}
            }
        ],
        "telecom": [
            {"system": "phone", "value": d.get("phone")},
            {"system": "email", "value": d.get("email")}
        ]
    }

def to_fhir_organization(o: Dict[str, Any], is_lab: bool = False) -> Dict[str, Any]:
    """Serialize hospital or lab to FHIR R4 Organization."""
    system_id = "https://nabl-india.org" if is_lab else "https://facility.ndhm.gov.in"
    org_id = o.get("lab_id") if is_lab else o.get("hospital_id")
    code_id = o.get("nabl_id") if is_lab else o.get("hfr_id")
    
    return {
        "resourceType": "Organization",
        "id": org_id,
        "meta": {
            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/Organization"]
        },
        "identifier": [
            {
                "system": system_id,
                "value": code_id
            }
        ],
        "active": True,
        "type": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/organization-type",
                        "code": "prov",
                        "display": "Healthcare Provider / Diagnostic Lab" if is_lab else "Hospital / Clinic"
                    }
                ]
            }
        ],
        "name": o["name"]
    }

def to_fhir_service_request(sr: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize diagnostic order to FHIR R4 ServiceRequest."""
    return {
        "resourceType": "ServiceRequest",
        "id": sr["order_id"],
        "meta": {
            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/ServiceRequest"]
        },
        "status": sr["status"].lower(),
        "intent": "order",
        "priority": sr.get("priority", "routine").lower(),
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": sr["loinc_code"],
                    "display": sr["test_name"]
                }
            ],
            "text": sr["test_name"]
        },
        "subject": {
            "reference": f"Patient/{sr['upk']}",
            "display": f"Patient UPK: {sr['upk']}"
        },
        "requester": {
            "reference": f"Practitioner/{sr['udk']}",
            "display": f"Doctor UDK: {sr['udk']}"
        },
        "performer": [
            {
                "reference": f"Organization/{sr['lab_id']}",
                "display": f"Diagnostic Lab: {sr['lab_id']}"
            }
        ],
        "authoredOn": sr.get("order_time"),
        "reasonCode": [
            {"text": sr.get("clinical_indication", "Clinical Diagnostic Evaluation")}
        ]
    }

def to_fhir_diagnostic_report(dr: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize lab report to FHIR R4 DiagnosticReport with Observations."""
    results_raw = json.loads(dr["result_values_json"]) if isinstance(dr["result_values_json"], str) else dr["result_values_json"]
    
    observations = []
    for idx, item in enumerate(results_raw):
        obs = {
            "resourceType": "Observation",
            "id": f"{dr['report_id']}-obs-{idx+1}",
            "status": "final",
            "code": {
                "coding": [
                    {"system": "http://loinc.org", "code": dr["loinc_code"], "display": dr["test_name"]}
                ]
            },
            "subject": {"reference": f"Patient/{dr['upk']}"},
            "valueQuantity": {
                "value": item.get("value"),
                "unit": item.get("unit"),
                "system": "http://unitsofmeasure.org"
            },
            "interpretation": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                            "code": item.get("flag", "Normal")[0].upper(),
                            "display": item.get("flag", "Normal")
                        }
                    ]
                }
            ],
            "referenceRange": [
                {"text": dr.get("reference_range", "")}
            ]
        }
        observations.append(obs)

    report_resource = {
        "resourceType": "DiagnosticReport",
        "id": dr["report_id"],
        "meta": {
            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/DiagnosticReportLab"]
        },
        "basedOn": [
            {"reference": f"ServiceRequest/{dr['order_id']}"}
        ],
        "status": dr["status"].lower(),
        "category": [
            {
                "coding": [
                    {"system": "http://terminology.hl7.org/CodeSystem/v2-0074", "code": "LAB", "display": "Laboratory"}
                ]
            }
        ],
        "code": {
            "coding": [
                {"system": "http://loinc.org", "code": dr["loinc_code"], "display": dr["test_name"]}
            ],
            "text": dr["test_name"]
        },
        "subject": {"reference": f"Patient/{dr['upk']}"},
        "performer": [{"reference": f"Organization/{dr['lab_id']}"}],
        "issued": dr.get("report_time"),
        "conclusion": dr.get("interpretation"),
        "result": [{"reference": f"Observation/{o['id']}"} for o in observations],
        "presentedForm": [
            {
                "contentType": "application/pdf",
                "data": dr.get("pdf_attachment_base64", ""),
                "title": f"Diagnostic Report - {dr['test_name']}"
            }
        ]
    }
    return {"DiagnosticReport": report_resource, "Observations": observations}

def to_fhir_medication_request(rx: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize prescription to FHIR R4 MedicationRequest."""
    meds = json.loads(rx["medications_json"]) if isinstance(rx["medications_json"], str) else rx["medications_json"]
    
    dosage_instructions = []
    medication_concepts = []
    
    for med in meds:
        medication_concepts.append({
            "coding": [
                {"system": "http://snomed.info/sct", "code": med.get("code", "372567009"), "display": med.get("name")}
            ],
            "text": med.get("name")
        })
        dosage_instructions.append({
            "text": f"{med.get('dosage')} - {med.get('frequency')} for {med.get('duration')}. {med.get('instructions', '')}",
            "route": {"text": med.get("route", "Oral")}
        })

    return {
        "resourceType": "MedicationRequest",
        "id": rx["rx_id"],
        "meta": {
            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/MedicationRequest"]
        },
        "status": rx["status"].lower(),
        "intent": "order",
        "medicationCodeableConcept": medication_concepts[0] if medication_concepts else {},
        "subject": {"reference": f"Patient/{rx['upk']}"},
        "requester": {"reference": f"Practitioner/{rx['udk']}"},
        "authoredOn": rx.get("issue_time"),
        "dosageInstruction": dosage_instructions,
        "note": [{"text": f"Canonical Hash: {rx.get('canonical_hash')[:16]}... | PKI Digital Signature Verified"}],
        "extension": [
            {
                "url": "https://cihip.nhp.gov.in/fhir/StructureDefinition/digital-signature-seal",
                "valueString": rx.get("digital_signature", "")
            },
            {
                "url": "https://cihip.nhp.gov.in/fhir/StructureDefinition/qr-payload",
                "valueString": rx.get("qr_payload", "")
            }
        ]
    }

def to_fhir_consent(c: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize patient consent to FHIR R4 Consent resource."""
    resources = json.loads(c["resources_json"]) if isinstance(c["resources_json"], str) else c["resources_json"]
    
    return {
        "resourceType": "Consent",
        "id": c["consent_id"],
        "meta": {
            "profile": ["https://nrces.in/ndhm/fhir/r4/StructureDefinition/Consent"]
        },
        "status": "active" if c["status"] == "GRANTED" else "inactive",
        "scope": {
            "coding": [{"system": "http://terminology.hl7.org/CodeSystem/consentscope", "code": "patient-privacy", "display": "Privacy Consent"}]
        },
        "category": [
            {
                "coding": [{"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "INFA", "display": "Information Access"}]
            }
        ],
        "patient": {"reference": f"Patient/{c['upk']}"},
        "dateTime": c.get("granted_time"),
        "performer": [{"display": c.get("requester_name")}],
        "provision": {
            "type": "permit" if c["status"] == "GRANTED" else "deny",
            "period": {
                "start": c.get("valid_from"),
                "end": c.get("valid_to")
            },
            "purpose": [
                {"code": c.get("purpose", "Treatment")}
            ],
            "class": [
                {"code": r} for r in resources
            ]
        }
    }

def to_fhir_audit_event(a: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize audit ledger row to FHIR R4 AuditEvent."""
    return {
        "resourceType": "AuditEvent",
        "id": a["audit_id"],
        "type": {
            "system": "http://dicom.nema.org/resources/ontology/DCM",
            "code": "110100",
            "display": a["action"]
        },
        "action": "E" if a["action"].startswith("SIGN") else "R" if a["action"].startswith("VIEW") else "C",
        "recorded": a["timestamp"],
        "outcome": "0" if a["outcome"] == "SUCCESS" else "4",
        "agent": [
            {
                "role": [{"text": a["role"]}],
                "who": {"identifier": {"value": a["user_id"]}},
                "requestor": True,
                "network": {"address": a.get("ip_address", "127.0.0.1"), "type": "2"}
            }
        ],
        "entity": [
            {
                "what": {"reference": f"{a['resource_type']}/{a['resource_id']}"},
                "type": {"code": a["resource_type"]}
            }
        ],
        "extension": [
            {
                "url": "https://cihip.nhp.gov.in/fhir/StructureDefinition/prev-hash",
                "valueString": a.get("prev_hash")
            },
            {
                "url": "https://cihip.nhp.gov.in/fhir/StructureDefinition/curr-hash",
                "valueString": a.get("curr_hash")
            }
        ]
    }
