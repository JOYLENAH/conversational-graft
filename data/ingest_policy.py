import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "processed"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def build_benefit_schedules():
    schedules = {
        "tiers": {
            "PLATINUM": {
                "provider_panel": "Enhanced Provider List",
                "geographical_scope": "Uganda or referral within East Africa + temporary cover abroad up to 6 weeks",
                "inpatient": {
                    "overall_limit_ugx": 300_000_000,
                    "daily_bed_limit_ugx": 300_000,
                    "accidents_and_emergency_ugx": 150_000_000,
                    "general_illness_ugx": 150_000_000,
                    "dental_inpatient_ugx": 22_500_000,
                    "ophthalmology_inpatient_ugx": 22_500_000,
                    "covid19_inpatient_ugx": 15_000_000,
                    "psychiatric_conditions_ugx": 30_000_000,
                    "chronic_pre_existing_ugx": 45_000_000,
                    "organ_transplant_ugx": 150_000_000,
                    "gynaecological_conditions_ugx": 15_000_000,
                    "ent_ugx": 7_500_000
                },
                "outpatient": {
                    "overall_limit_ugx": 6_000_000,
                    "chronic_pre_existing_ugx": 2_000_000,
                    "physiotherapy_sessions": 10,
                    "optical_limit_ugx": 800_000,
                    "dental_limit_ugx": 800_000,
                    "external_prosthesis_ugx": 1_200_000,
                    "wellness_checkup_ugx": 300_000
                },
                "maternity": {
                    "maternity_limit_ugx": 5_000_000,
                    "premature_delivery_ugx": 4_000_000
                },
                "funeral_ugx": 3_000_000
            },
            "GOLD": {
                "provider_panel": "Enhanced Provider List",
                "geographical_scope": "Uganda or referral within East Africa + temporary cover abroad up to 6 weeks",
                "inpatient": {
                    "overall_limit_ugx": 100_000_000,
                    "daily_bed_limit_ugx": 250_000,
                    "accidents_and_emergency_ugx": 100_000_000,
                    "general_illness_ugx": 100_000_000,
                    "dental_inpatient_ugx": 15_000_000,
                    "ophthalmology_inpatient_ugx": 15_000_000,
                    "covid19_inpatient_ugx": 10_000_000,
                    "psychiatric_conditions_ugx": 20_000_000,
                    "chronic_pre_existing_ugx": 30_000_000,
                    "organ_transplant_ugx": 50_000_000,
                    "gynaecological_conditions_ugx": 10_000_000,
                    "ent_ugx": 5_000_000
                },
                "outpatient": {
                    "overall_limit_ugx": 4_000_000,
                    "chronic_pre_existing_ugx": 1_500_000,
                    "physiotherapy_sessions": 10,
                    "optical_limit_ugx": 500_000,
                    "dental_limit_ugx": 500_000,
                    "external_prosthesis_ugx": 800_000,
                    "wellness_checkup_ugx": 200_000
                },
                "maternity": {
                    "maternity_limit_ugx": 3_500_000,
                    "premature_delivery_ugx": 2_800_000
                },
                "funeral_ugx": 2_500_000
            },
            "SILVER": {
                "provider_panel": "Enhanced Provider List",
                "geographical_scope": "Uganda or referral within East Africa + temporary cover abroad up to 6 weeks",
                "inpatient": {
                    "overall_limit_ugx": 50_000_000,
                    "daily_bed_limit_ugx": 200_000,
                    "accidents_and_emergency_ugx": 50_000_000,
                    "general_illness_ugx": 50_000_000,
                    "dental_inpatient_ugx": 7_500_000,
                    "ophthalmology_inpatient_ugx": 7_500_000,
                    "covid19_inpatient_ugx": 5_000_000,
                    "psychiatric_conditions_ugx": 10_000_000,
                    "chronic_pre_existing_ugx": 15_000_000,
                    "organ_transplant_ugx": 25_000_000,
                    "gynaecological_conditions_ugx": 5_000_000,
                    "ent_ugx": 2_500_000
                },
                "outpatient": {
                    "overall_limit_ugx": 3_000_000,
                    "chronic_pre_existing_ugx": 1_000_000,
                    "physiotherapy_sessions": 10,
                    "optical_limit_ugx": 400_000,
                    "dental_limit_ugx": 400_000,
                    "external_prosthesis_ugx": 600_000,
                    "wellness_checkup_ugx": 200_000
                },
                "maternity": {
                    "maternity_limit_ugx": 2_500_000,
                    "premature_delivery_ugx": 2_000_000
                },
                "funeral_ugx": 2_000_000
            },
            "BRONZE": {
                "provider_panel": "Standard Provider List",
                "geographical_scope": "Within Uganda only",
                "inpatient": {
                    "overall_limit_ugx": 20_000_000,
                    "daily_bed_limit_ugx": 200_000,
                    "accidents_and_emergency_ugx": 20_000_000,
                    "general_illness_ugx": 20_000_000,
                    "dental_inpatient_ugx": 3_000_000,
                    "ophthalmology_inpatient_ugx": 3_000_000,
                    "covid19_inpatient_ugx": 2_000_000,
                    "psychiatric_conditions_ugx": 4_000_000,
                    "chronic_pre_existing_ugx": 6_000_000,
                    "organ_transplant_ugx": 10_000_000,
                    "gynaecological_conditions_ugx": 2_000_000,
                    "ent_ugx": 1_000_000
                },
                "outpatient": {
                    "overall_limit_ugx": 2_000_000,
                    "chronic_pre_existing_ugx": 500_000,
                    "physiotherapy_sessions": 10,
                    "optical_limit_ugx": 200_000,
                    "dental_limit_ugx": 200_000,
                    "external_prosthesis_ugx": 400_000,
                    "wellness_checkup_ugx": 150_000
                },
                "maternity": {
                    "maternity_limit_ugx": 2_000_000,
                    "premature_delivery_ugx": 1_600_000
                },
                "funeral_ugx": 1_000_000
            },
            "COPPER": {
                "provider_panel": "Standard Provider List",
                "geographical_scope": "Within Uganda only",
                "inpatient": {
                    "overall_limit_ugx": 10_000_000,
                    "daily_bed_limit_ugx": 150_000,
                    "accidents_and_emergency_ugx": 10_000_000,
                    "general_illness_ugx": 10_000_000,
                    "dental_inpatient_ugx": 1_500_000,
                    "ophthalmology_inpatient_ugx": 1_500_000,
                    "covid19_inpatient_ugx": 1_000_000,
                    "psychiatric_conditions_ugx": 2_000_000,
                    "chronic_pre_existing_ugx": 3_000_000,
                    "organ_transplant_ugx": 5_000_000,
                    "gynaecological_conditions_ugx": 1_000_000,
                    "ent_ugx": 500_000
                },
                "outpatient": {
                    "overall_limit_ugx": 1_000_000,
                    "chronic_pre_existing_ugx": 500_000,
                    "physiotherapy_sessions": 10,
                    "optical_limit_ugx": 150_000,
                    "dental_limit_ugx": 150_000,
                    "external_prosthesis_ugx": 200_000,
                    "wellness_checkup_ugx": 150_000
                },
                "maternity": {
                    "maternity_limit_ugx": 1_000_000,
                    "premature_delivery_ugx": 800_000
                },
                "funeral_ugx": 1_000_000
            },
            "MARBLE": {
                "provider_panel": "Standard Provider List",
                "geographical_scope": "Within Uganda only",
                "inpatient": {
                    "overall_limit_ugx": 5_000_000,
                    "daily_bed_limit_ugx": 100_000,
                    "accidents_and_emergency_ugx": 5_000_000,
                    "general_illness_ugx": 5_000_000,
                    "dental_inpatient_ugx": 750_000,
                    "ophthalmology_inpatient_ugx": 750_000,
                    "covid19_inpatient_ugx": 500_000,
                    "psychiatric_conditions_ugx": 1_000_000,
                    "chronic_pre_existing_ugx": 1_500_000,
                    "organ_transplant_ugx": 2_500_000,
                    "gynaecological_conditions_ugx": 500_000,
                    "ent_ugx": 250_000
                },
                "outpatient": {
                    "overall_limit_ugx": 800_000,
                    "chronic_pre_existing_ugx": 0,
                    "physiotherapy_sessions": 10,
                    "optical_limit_ugx": 100_000,
                    "dental_limit_ugx": 100_000,
                    "external_prosthesis_ugx": 160_000,
                    "wellness_checkup_ugx": 100_000
                },
                "maternity": {
                    "maternity_limit_ugx": 800_000,
                    "premature_delivery_ugx": 640_000
                },
                "funeral_ugx": 500_000
            },
            "SENIOR_CITIZEN": {
                "provider_panel": "Standard Provider List",
                "geographical_scope": "Uganda + referral outside Uganda",
                "inpatient": {
                    "overall_limit_ugx": 10_000_000,
                    "daily_bed_limit_ugx": 100_000,
                    "accidents_and_emergency_ugx": 10_000_000,
                    "general_illness_ugx": 10_000_000,
                    "dental_inpatient_ugx": 1_500_000,
                    "ophthalmology_inpatient_ugx": 1_500_000,
                    "covid19_inpatient_ugx": 3_000_000,
                    "psychiatric_conditions_ugx": 2_000_000,
                    "chronic_pre_existing_ugx": 3_000_000,
                    "organ_transplant_ugx": 4_000_000,
                    "gynaecological_conditions_ugx": 2_000_000
                },
                "outpatient": {
                    "overall_limit_ugx": 3_000_000,
                    "chronic_pre_existing_ugx": 1_500_000,
                    "optical_limit_ugx": 200_000,
                    "dental_limit_ugx": 200_000,
                    "external_prosthesis_ugx": 600_000,
                    "wellness_checkup_ugx": 300_000
                },
                "maternity": None,
                "funeral_ugx": 1_000_000
            }
        }
    }
    with open(DATA_DIR / "benefit_schedules.json", "w") as f:
        json.dump(schedules, f, indent=2)

def build_policy_rules():
    rules = {
        "waiting_periods_months": {
            "outpatient": 0,
            "inpatient": 3,
            "maternity": 8,
            "pre_existing_and_chronic": 12,
            "elective_surgery": 12,
            "organ_transplant": 24
        },
        "pre_authorization_required": [
            "All Inpatient and Daycare treatments and services",
            "All Surgical operations",
            "Computerized tomography (CT scan) and magnetic resonance imaging (MRI)",
            "Long term medications (more than one month)",
            "Maternity treatments (inpatient only)"
        ],
        "timelines": {
            "pre_auth_validity_days": 14,
            "emergency_notification_hours": 48,
            "claim_submission_max_days": 60,
            "reimbursement_non_panel_submission_max_days": 30,
            "reimbursement_processing_days": 14,
            "claim_denial_appeal_window_days": 60
        },
        "age_limits": {
            "new_members_standard_max_entry_age": 70,
            "new_members_senior_citizen_entry_age": 80,
            "continuing_members_max_age": 85,
            "dependents_child_max_age": 18,
            "dependents_student_child_max_age": 25
        }
    }
    with open(DATA_DIR / "policy_rules.json", "w") as f:
        json.dump(rules, f, indent=2)

if __name__ == "__main__":
    build_benefit_schedules()
    build_policy_rules()
    print("Policy knowledge layers generated successfully in data/processed/")