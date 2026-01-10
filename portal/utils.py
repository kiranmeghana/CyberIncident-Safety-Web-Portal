import base64
import requests



def analyze_image_ai(image_file):
    """
    Sends the uploaded image to a Vision API to extract text 
    and detect cyber-threat markers.
    """
    # Simulate API call logic for image parsing
    # In production, you would send the base64 image to a Vision API
    return "DETECTED: Phishing URL (http://bank-secure-login.com), Keywords: 'Urgent', 'KYC Update'."
def analyze_cyber_risk(description):
    """
    Score-based risk classification logic.
    Calculates severity based on keyword weights.
    """
    score = 0
    desc_lower = description.lower()

    # [cite_start]Weight Mapping [cite: 52, 55]
    keywords = {
        'otp': 5, 'cvv': 5, 'password': 4, 'bank': 4, 'transaction': 4,
        'link': 3, 'whatsapp': 2, 'email': 2, 'unknown': 1, 'message': 1,
        'ransomware': 5, 'hacked': 5, 'urgent': 3, 'threat': 4
    }

    for word, weight in keywords.items():
        if word in desc_lower:
            score += weight

    # [cite_start]Determine Level [cite: 52]
    if score >= 10:
        return score, 'High', 'Immediate action required. Contact authorities.'
    elif score >= 5:
        return score, 'Medium', 'Potential threat detected. Proceed with caution.'
    else:
        return score, 'Low', 'Stay vigilant, but no immediate danger detected.'
    """
    Score-based risk classification logic.
    Calculates severity based on keyword weights.
    """
    score = 0
    desc_lower = description.lower()

    # [cite_start]Weight Mapping [cite: 52, 55]
    keywords = {
        'otp': 5, 'cvv': 5, 'password': 4, 'bank': 4, 'transaction': 4,
        'link': 3, 'whatsapp': 2, 'email': 2, 'unknown': 1, 'message': 1,
        'ransomware': 5, 'hacked': 5, 'urgent': 3, 'threat': 4
    }

    for word, weight in keywords.items():
        if word in desc_lower:
            score += weight

    # [cite_start]Determine Level [cite: 52]
    if score >= 10:
        return score, 'High', 'Immediate action required. Contact authorities.'
    elif score >= 5:
        return score, 'Medium', 'Potential threat detected. Proceed with caution.'
    else:
        return score, 'Low', 'Stay vigilant, but no immediate danger detected.'
    """
    Hybrid analysis using NLP on text + AI Image insights.
    Enhanced score-based logic that recognizes 'SECURE AI LOG' 
    as a high-confidence indicator.
    """
    score = 0
    desc_lower = description.lower()

    # Manual Scoring Keywords
    keywords = {
        'otp': 5, 'scam': 4, 'fake': 3, 'ransom': 6, 'link': 3,
        'ai log': 10, 'fraudulent': 4, 'bank': 5
    }

    for word, weight in keywords.items():
        if word in desc_lower:
            score += weight

    # Risk Level Determination
    if score >= 10:
        return score, 'HIGH', 'Mandatory: Disconnect and notify the cyber cell immediately.'
    elif score >= 5:
        return score, 'MEDIUM', 'Caution: Monitor your accounts for unauthorized activity.'
    
    return score, 'LOW', 'Info: No immediate threat found. Stay updated on safety tips.'