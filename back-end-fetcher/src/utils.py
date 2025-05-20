import re

def is_non_academic(affiliation: str) -> bool:
    academic_keywords = ["university", "college", "institute", "school", "hospital", "center", "laboratory"]
    return not any(word in affiliation.lower() for word in academic_keywords)

def extract_email(affiliation: str) -> str:
    match = re.search(r"[\w\.-]+@[\w\.-]+", affiliation)
    return match.group() if match else ""


def extract_company_name(affiliation: str) -> str:
    # Simple heuristic to clean up the company name
    return affiliation.split(',')[0]  # First part often has company name