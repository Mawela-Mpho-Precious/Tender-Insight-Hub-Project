import re
import logging
from typing import Dict, List, Any
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        return ""

def extract_text_from_zip(file_path: str, extract_dir: str) -> str:
    """Extract text from ZIP file containing documents"""
    try:
        import zipfile
        import os
        all_text = ""
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            for file_name in zip_ref.namelist():
                if file_name.lower().endswith('.pdf'):
                    pdf_path = os.path.join(extract_dir, file_name)
                    all_text += extract_text_from_pdf(pdf_path) + "\n\n"
        return all_text
    except Exception as e:
        logger.error(f"ZIP extraction error: {e}")
        return ""

def summarize_text(text: str) -> str:
    """
    Enhanced AI summarization focusing on key tender elements
    """
    try:
        # Extract key information first
        extracted_info = extract_tender_requirements(text)
        
        # Build comprehensive summary
        summary_parts = []
        
        # Objective
        if extracted_info['objective']:
            summary_parts.append(f"📋 **Objective**: {extracted_info['objective']}")
        
        # Scope
        if extracted_info['scope']:
            summary_parts.append(f"🎯 **Scope**: {extracted_info['scope']}")
        
        # Deadline
        if extracted_info['deadline']:
            summary_parts.append(f"⏰ **Submission Deadline**: {extracted_info['deadline']}")
        
        # Eligibility Criteria
        if extracted_info['eligibility_criteria']:
            summary_parts.append("✅ **Eligibility Criteria**:")
            for criteria in extracted_info['eligibility_criteria']:
                summary_parts.append(f"   • {criteria}")
        
        # Budget
        if extracted_info['budget']:
            summary_parts.append(f"💰 **Budget**: {extracted_info['budget']}")
        
        # Location
        if extracted_info['location']:
            summary_parts.append(f"📍 **Location**: {extracted_info['location']}")
        
        # Key Requirements
        if extracted_info['key_requirements']:
            summary_parts.append("🔧 **Key Requirements**:")
            for req in extracted_info['key_requirements'][:5]:  # Top 5 requirements
                summary_parts.append(f"   • {req}")
        
        # If no specific info found, create a general summary
        if not summary_parts:
            # Simple rule-based summary as fallback
            sentences = text.split('.')
            key_sentences = [s.strip() for s in sentences if any(word in s.lower() for word in 
                            ['tender', 'bid', 'submit', 'deadline', 'requirement', 'eligible', 'scope'])]
            summary = '. '.join(key_sentences[:5]) + '.'
            return summary if summary else "Summary not available from document content."
        
        return '\n\n'.join(summary_parts)
        
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        return "Unable to generate summary due to processing error."

def extract_tender_requirements(text: str) -> Dict[str, Any]:
    """
    Extract specific tender requirements using pattern matching and rules
    """
    text_lower = text.lower()
    requirements = {
        'objective': '',
        'scope': '',
        'deadline': '',
        'eligibility_criteria': [],
        'budget': '',
        'location': '',
        'key_requirements': []
    }
    
    try:
        # Extract Objective (look for purpose, objective, aim)
        objective_patterns = [
            r'objective[:\s]*([^.\n]+)',
            r'purpose[:\s]*([^.\n]+)',
            r'aim[:\s]*([^.\n]+)',
            r'introduction[:\s]*([^.\n]{50,200})'
        ]
        requirements['objective'] = extract_pattern(text, objective_patterns)
        
        # Extract Scope (look for scope, works, services)
        scope_patterns = [
            r'scope[:\s]*([^.\n]{50,300})',
            r'works[:\s]*([^.\n]{50,300})',
            r'services[:\s]*([^.\n]{50,300})',
            r'description[:\s]*([^.\n]{50,300})'
        ]
        requirements['scope'] = extract_pattern(text, scope_patterns)
        
        # Extract Deadline (look for date patterns)
        deadline_patterns = [
            r'deadline[:\s]*([^.\n]{10,50})',
            r'submission[^.\n]{0,50}?(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'closing[^.\n]{0,50}?(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2} (january|february|march|april|may|june|july|august|september|october|november|december) \d{4})'
        ]
        requirements['deadline'] = extract_pattern(text, deadline_patterns)
        
        # Extract Eligibility Criteria
        eligibility_keywords = ['eligible', 'qualification', 'requirement', 'must have', 'should have']
        sentences = text.split('.')
        eligibility_sentences = [s.strip() for s in sentences if any(word in s.lower() for word in eligibility_keywords)]
        requirements['eligibility_criteria'] = eligibility_sentences[:10]  # Top 10
        
        # Extract Budget
        budget_patterns = [
            r'budget[:\s]*([^.\n]{10,50})',
            r'amount[:\s]*([^.\n]{10,50})',
            r'value[:\s]*([^.\n]{10,50})',
            r'(\$|r|usd)\s*(\d[\d,\.]*)'
        ]
        requirements['budget'] = extract_pattern(text, budget_patterns)
        
        # Extract Location
        location_patterns = [
            r'location[:\s]*([^.\n]{10,50})',
            r'province[:\s]*([^.\n]{10,50})',
            r'city[:\s]*([^.\n]{10,50})',
            r'address[:\s]*([^.\n]{10,50})'
        ]
        requirements['location'] = extract_pattern(text, location_patterns)
        
        # Extract Key Requirements
        requirement_keywords = ['must', 'shall', 'required', 'requirement', 'specification']
        requirement_sentences = [s.strip() for s in sentences if any(word in s.lower() for word in requirement_keywords)]
        requirements['key_requirements'] = requirement_sentences[:15]  # Top 15
        
        # Clean up extracted data
        requirements = {k: v.strip() if isinstance(v, str) else v for k, v in requirements.items()}
        
    except Exception as e:
        logger.error(f"Requirement extraction error: {e}")
    
    return requirements

def extract_pattern(text: str, patterns: List[str]) -> str:
    """Extract text using regex patterns"""
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            # Handle different match formats
            match = matches[0]
            if isinstance(match, tuple):
                match = ' '.join([m for m in match if m])
            return match.strip()
    return ""

def highlight_key_points(text: str) -> List[str]:
    """
    Extract key points from tender text
    """
    key_points = []
    
    try:
        requirements = extract_tender_requirements(text)
        
        # Add objective if found
        if requirements['objective']:
            key_points.append(f"🎯 Objective: {requirements['objective']}")
        
        # Add scope if found
        if requirements['scope']:
            key_points.append(f"📋 Scope: {requirements['scope'][:100]}...")
        
        # Add deadline if found
        if requirements['deadline']:
            key_points.append(f"⏰ Deadline: {requirements['deadline']}")
        
        # Add budget if found
        if requirements['budget']:
            key_points.append(f"💰 Budget: {requirements['budget']}")
        
        # Add location if found
        if requirements['location']:
            key_points.append(f"📍 Location: {requirements['location']}")
        
        # Add top eligibility criteria
        for criteria in requirements['eligibility_criteria'][:3]:
            key_points.append(f"✅ {criteria[:80]}...")
        
        # Add key requirements
        for req in requirements['key_requirements'][:3]:
            key_points.append(f"🔧 {req[:80]}...")
        
        # If no specific points found, create generic ones
        if not key_points:
            key_points = [
                "Review tender documents for complete requirements",
                "Check submission deadline carefully",
                "Verify all eligibility criteria before bidding",
                "Ensure all required documents are prepared",
                "Confirm budget and scope alignment"
            ]
            
    except Exception as e:
        logger.error(f"Key points extraction error: {e}")
        key_points = ["Unable to extract key points from document"]
    
    return key_points

def readiness_scoring(tender_summary: str, company_profile: Dict) -> Dict:
    """
    Enhanced readiness scoring with detailed criteria matching
    """
    try:
        # Extract requirements from tender summary
        tender_reqs = extract_tender_requirements(tender_summary)
        
        # Initialize scoring
        total_points = 0
        earned_points = 0
        checklist = []
        
        # 1. Industry/Sector Match (20 points)
        total_points += 20
        industry_match = check_industry_match(tender_summary, company_profile)
        if industry_match['match']:
            earned_points += 20
            checklist.append("✅ Industry/Sector: MATCHED")
        else:
            checklist.append("❌ Industry/Sector: NOT MATCHED")
        
        # 2. Experience Match (20 points)
        total_points += 20
        exp_match = check_experience_match(tender_reqs, company_profile)
        earned_points += exp_match['score']
        checklist.append(exp_match['checklist'])
        
        # 3. Location Match (15 points)
        total_points += 15
        location_match = check_location_match(tender_reqs, company_profile)
        earned_points += location_match['score']
        checklist.append(location_match['checklist'])
        
        # 4. Certification Match (15 points)
        total_points += 15
        cert_match = check_certification_match(tender_reqs, company_profile)
        earned_points += cert_match['score']
        checklist.extend(cert_match['checklist'])
        
        # 5. Capacity Match (15 points)
        total_points += 15
        capacity_match = check_capacity_match(tender_reqs, company_profile)
        earned_points += capacity_match['score']
        checklist.extend(capacity_match['checklist'])
        
        # 6. BBBEE Match (15 points)
        total_points += 15
        bbbee_match = check_bbbee_match(tender_reqs, company_profile)
        earned_points += bbbee_match['score']
        checklist.append(bbbee_match['checklist'])
        
        # Calculate final score
        suitability_score = min(100, int((earned_points / total_points) * 100)) if total_points > 0 else 0
        
        # Generate recommendation
        recommendation = generate_recommendation(suitability_score, checklist)
        
        return {
            "suitability_score": suitability_score,
            "recommendation": recommendation,
            "checklist": checklist,
            "matched_criteria": len([c for c in checklist if '✅' in c]),
            "total_criteria": len(checklist),
            "tender_requirements": tender_reqs
        }
        
    except Exception as e:
        logger.error(f"Readiness scoring error: {e}")
        return {
            "suitability_score": 0,
            "recommendation": "Unable to calculate score due to processing error",
            "checklist": ["Error in scoring calculation"],
            "matched_criteria": 0,
            "total_criteria": 1
        }

def check_industry_match(tender_summary: str, company: Dict) -> Dict:
    """Check if company industry matches tender requirements"""
    company_industry = company.get('industry', '').lower()
    tender_text = tender_summary.lower()
    
    # Common industry keywords
    industry_keywords = {
        'construction': ['construction', 'building', 'civil', 'engineering', 'contractor'],
        'it': ['it', 'technology', 'software', 'hardware', 'digital'],
        'security': ['security', 'guard', 'surveillance', 'protection'],
        'cleaning': ['cleaning', 'maintenance', 'sanitation', 'hygiene']
    }
    
    for industry, keywords in industry_keywords.items():
        if any(keyword in company_industry for keyword in keywords):
            if any(keyword in tender_text for keyword in keywords):
                return {'match': True, 'industry': industry}
    
    return {'match': False, 'industry': 'unknown'}

def check_experience_match(tender_reqs: Dict, company: Dict) -> Dict:
    """Check experience requirements match"""
    exp_text = ' '.join(tender_reqs['eligibility_criteria'] + tender_reqs['key_requirements']).lower()
    
    # Look for experience requirements
    exp_patterns = [
        r'(\d+)\s*years',
        r'(\d+)\s*yr',
        r'minimum\s*(\d+)\s*experience',
        r'at least\s*(\d+)\s*years'
    ]
    
    required_exp = 0
    for pattern in exp_patterns:
        matches = re.findall(pattern, exp_text)
        if matches:
            required_exp = max(required_exp, int(matches[0]))
            break
    
    company_exp = company.get('years_of_experience', 0)
    
    if required_exp == 0:
        return {'score': 20, 'checklist': "✅ Experience: No specific requirement"}
    elif company_exp >= required_exp:
        return {'score': 20, 'checklist': f"✅ Experience: {company_exp} years (meets {required_exp}+ requirement)"}
    else:
        return {'score': 10, 'checklist': f"❌ Experience: {company_exp} years (needs {required_exp}+ years)"}

def check_location_match(tender_reqs: Dict, company: Dict) -> Dict:
    """Check location requirements match"""
    tender_location = tender_reqs.get('location', '').lower()
    company_locations = [loc.strip().lower() for loc in company.get('geographic_coverage', [])]
    
    if not tender_location:
        return {'score': 15, 'checklist': "✅ Location: No specific requirement"}
    
    # Check if company operates in required location
    location_match = any(loc in tender_location for loc in company_locations) or any(tender_location in loc for loc in company_locations)
    
    if location_match:
        return {'score': 15, 'checklist': f"✅ Location: Operates in {tender_location}"}
    else:
        return {'score': 0, 'checklist': f"❌ Location: Does not operate in {tender_location}"}

def check_certification_match(tender_reqs: Dict, company: Dict) -> Dict:
    """Check certification requirements match"""
    cert_text = ' '.join(tender_reqs['eligibility_criteria'] + tender_reqs['key_requirements']).lower()
    company_certs = [cert.lower() for cert in company.get('certifications', [])]
    
    checklist_items = []
    score = 0
    max_score = 15
    
    # Check for common certifications
    cert_checks = {
        'cidb': ['cidb'],
        'bbbee': ['bbbee', 'b-bbee'],
        'iso': ['iso 9001', 'iso 14001'],
        'sans': ['sans 10400']
    }
    
    for cert_type, keywords in cert_checks.items():
        if any(keyword in cert_text for keyword in keywords):
            if any(any(keyword in cert for keyword in keywords) for cert in company_certs):
                checklist_items.append(f"✅ {cert_type.upper()}: Certified")
                score += 5
            else:
                checklist_items.append(f"❌ {cert_type.upper()}: Not certified")
    
    if not checklist_items:
        checklist_items.append("✅ Certifications: No specific requirements")
        score = max_score
    
    return {'score': min(score, max_score), 'checklist': checklist_items}

def check_capacity_match(tender_reqs: Dict, company: Dict) -> Dict:
    """Check company capacity matches requirements"""
    capacity_text = ' '.join(tender_reqs['eligibility_criteria']).lower()
    company_employees = company.get('employee_count', 0)
    company_turnover = company.get('annual_turnover', 0)
    
    checklist_items = []
    score = 0
    
    # Check employee count requirements
    if 'employees' in capacity_text or 'staff' in capacity_text:
        if company_employees >= 10:
            checklist_items.append("✅ Capacity: Adequate workforce")
            score += 5
        else:
            checklist_items.append("❌ Capacity: Limited workforce")
    
    # Check turnover requirements
    if 'turnover' in capacity_text or 'revenue' in capacity_text:
        if company_turnover >= 1000000:  # 1 million
            checklist_items.append("✅ Financial: Adequate turnover")
            score += 5
        else:
            checklist_items.append("❌ Financial: Limited turnover")
    
    if not checklist_items:
        checklist_items.append("✅ Capacity: No specific requirements")
        score = 10
    
    return {'score': score, 'checklist': checklist_items}

def check_bbbee_match(tender_reqs: Dict, company: Dict) -> Dict:
    """Check BBBEE requirements"""
    bbeee_text = ' '.join(tender_reqs['eligibility_criteria']).lower()
    company_bbbee = company.get('black_owned', False)
    
    if 'bbbee' in bbeee_text or 'b-bbee' in bbeee_text:
        if company_bbbee:
            return {'score': 15, 'checklist': "✅ BBBEE: Compliant (Black-owned)"}
        else:
            return {'score': 5, 'checklist': "❌ BBBEE: Not compliant"}
    else:
        return {'score': 15, 'checklist': "✅ BBBEE: No specific requirement"}

def generate_recommendation(score: int, checklist: List[str]) -> str:
    """Generate recommendation based on score"""
    matched_count = len([c for c in checklist if '✅' in c])
    total_count = len(checklist)
    
    if score >= 80:
        return f"HIGHLY SUITABLE - Strong match ({matched_count}/{total_count} criteria). Recommended for bidding."
    elif score >= 60:
        return f"SUITABLE - Good match ({matched_count}/{total_count} criteria). Consider bidding with minor adjustments."
    elif score >= 40:
        return f"MODERATELY SUITABLE - Partial match ({matched_count}/{total_count} criteria). Review requirements carefully."
    else:
        return f"LOW SUITABILITY - Limited match ({matched_count}/{total_count} criteria). Not recommended unless gaps can be addressed."