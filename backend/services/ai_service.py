import re

DEPARTMENT_CUTOFFS = {
    "Computer Engineering": {"min_12th": 60.0, "min_entrance": 75.0},
    "Information Technology": {"min_12th": 55.0, "min_entrance": 70.0},
    "Artificial Intelligence & Data Science": {"min_12th": 60.0, "min_entrance": 75.0},
    "Electronics & Telecommunication": {"min_12th": 50.0, "min_entrance": 60.0},
    "Mechanical Engineering": {"min_12th": 45.0, "min_entrance": 50.0},
    "Civil Engineering": {"min_12th": 45.0, "min_entrance": 50.0}
}

FAQ_KNOWLEDGE_BASE = [
    (r"(fee|cost|tuition|payment)", "The annual tuition fee is approx ₹95,000 for Open category and ₹48,000 for Reserved categories. Online fee payment can be completed directly through your Student Portal."),
    (r"(cutoff|score|marks|percentage|eligibility)", "Minimum eligibility for Computer/AI&DS is 60% in 12th Board & 75+ Entrance Score. Other branches require 45%-50% in 12th."),
    (r"(document|upload|photo|marksheet)", "Mandatory documents: Passport Photo, 10th Marksheet, 12th Marksheet, and Leaving Certificate. Upload JPG/PNG/PDF files."),
    (r"(status|track|pending|approved)", "You can check your live admission status by logging into the Student Portal using your Application ID and Date of Birth."),
    (r"(department|branch|course|stream)", "Zeal College offers Computer Engineering, IT, AI & DS, E&TC, Mechanical, and Civil Engineering."),
    (r"(contact|help|support|desk)", "You can contact the admission office at admin@zeal.edu.in or submit a Support Ticket in your portal.")
]

class AIService:
    @staticmethod
    def chatbot_reply(query):
        """
        Process natural language admission queries and return smart AI assistant response.
        """
        if not query or not str(query).strip():
            return "Hello! I am your AI Admission Assistant. How can I help you today?"

        q_clean = str(query).lower().strip()

        for pattern, response in FAQ_KNOWLEDGE_BASE:
            if re.search(pattern, q_clean):
                return response

        return ("Thank you for your question! I can help you with admission eligibility, branch cutoffs, fees, "
                "required documents, and status tracking. Feel free to ask about any of these topics!")

    @staticmethod
    def check_eligibility(perc_10, perc_12, entrance_score, department):
        """
        AI Eligibility Engine evaluating academic scores against branch criteria.
        """
        dept_rules = DEPARTMENT_CUTOFFS.get(department, {"min_12th": 50.0, "min_entrance": 50.0})

        reasons = []
        is_eligible = True

        if perc_10 < 40.0:
            is_eligible = False
            reasons.append("10th percentage is below minimum requirement of 40%.")

        if perc_12 < dept_rules["min_12th"]:
            is_eligible = False
            reasons.append(f"12th percentage ({perc_12}%) is below {department} minimum requirement of {dept_rules['min_12th']}%.")

        if entrance_score < dept_rules["min_entrance"]:
            is_eligible = False
            reasons.append(f"Entrance score ({entrance_score}) is below {department} cutoff score of {dept_rules['min_entrance']}.")

        if is_eligible:
            reasons.append(f"Student satisfies all academic criteria for {department} admission!")

        return {
            "eligible": is_eligible,
            "department": department,
            "required_12th": dept_rules["min_12th"],
            "required_entrance": dept_rules["min_entrance"],
            "student_12th": perc_12,
            "student_entrance": entrance_score,
            "notes": reasons
        }

    @staticmethod
    def predict_admission_chances(perc_12, entrance_score, department):
        """
        AI Predictive Analytics estimating admission probability.
        """
        dept_rules = DEPARTMENT_CUTOFFS.get(department, {"min_12th": 50.0, "min_entrance": 50.0})
        req_score = dept_rules["min_entrance"]

        if entrance_score >= req_score + 10:
            chance = "High"
            probability = min(98, round(75 + (entrance_score - req_score) * 1.5, 1))
        elif entrance_score >= req_score:
            chance = "Medium"
            probability = round(60 + (entrance_score - req_score) * 2, 1)
        else:
            chance = "Low"
            probability = max(10, round(50 - (req_score - entrance_score) * 3, 1))

        return {
            "department": department,
            "chance_level": chance,
            "probability_percentage": probability,
            "entrance_score": entrance_score,
            "department_cutoff": req_score
        }

    @staticmethod
    def verify_documents(student_dict):
        """
        AI Document Verification detecting missing or unverified uploads.
        """
        mandatory_docs = {
            "photo": "Passport Photo",
            "marksheet10": "10th Marksheet",
            "marksheet12": "12th Marksheet",
            "leavingCertificate": "Leaving Certificate"
        }

        missing = []
        uploaded = []

        for field_name, label in mandatory_docs.items():
            fn = student_dict.get(field_name)
            if not fn:
                missing.append(label)
            else:
                uploaded.append({"document": label, "filename": fn})

        is_complete = len(missing) == 0
        return {
            "is_complete": is_complete,
            "uploaded_count": len(uploaded),
            "missing_count": len(missing),
            "uploaded": uploaded,
            "missing": missing,
            "verification_status": "Complete" if is_complete else "Incomplete"
        }
