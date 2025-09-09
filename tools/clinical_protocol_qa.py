"""
Clinical Protocol Q&A Tool
AI-powered question answering system for clinical protocol documents
"""

from typing import Dict, List, Any
import re
from datetime import datetime

def run(input_data: Dict) -> Dict:
    """
    Answer questions about clinical protocol content using AI-powered analysis
    
    Args:
        input_data: Dictionary containing:
            - question: The question to be answered
            - protocol_sections: Dict of protocol sections (title, content)
            - context_window: Optional context window size (default 1000)
            - include_references: Include section references in answers
    
    Returns:
        Dictionary with answer, confidence score, and source references
    """
    try:
        question = input_data.get('question', '').strip()
        protocol_sections = input_data.get('protocol_sections', {})
        context_window = input_data.get('context_window', 1000)
        include_references = input_data.get('include_references', True)
        
        if not question:
            return {
                'success': False,
                'error': 'No question provided'
            }
        
        if not protocol_sections:
            return {
                'success': False,
                'error': 'No protocol sections provided'
            }
        
        # Preprocess question for better matching
        question_lower = question.lower()
        question_keywords = extract_keywords(question_lower)
        
        # Search for relevant sections
        relevant_sections = []
        section_scores = {}
        
        for section_title, section_content in protocol_sections.items():
            if not section_content:
                continue
                
            content_lower = section_content.lower()
            section_score = calculate_relevance_score(
                question_keywords, 
                content_lower, 
                section_title.lower()
            )
            
            if section_score > 0.1:  # Minimum relevance threshold
                relevant_sections.append({
                    'title': section_title,
                    'content': section_content,
                    'score': section_score
                })
                section_scores[section_title] = section_score
        
        # Sort by relevance score
        relevant_sections.sort(key=lambda x: x['score'], reverse=True)
        
        if not relevant_sections:
            question_type = classify_question_type(question_lower)
            return {
                'success': True,
                'answer': "I couldn't find relevant information in the protocol to answer this question.",
                'confidence_score': 0.0,
                'source_sections': [],
                'question_classification': question_type,
                'suggested_sections': suggest_sections_for_question(question_lower),
                'follow_up_questions': generate_follow_up_questions(question_type, "I couldn't find relevant information in the protocol to answer this question."),
                'context_analysis': analyze_context(question_type, []),
                'complexity_level': input_data.get('complexity_level', 'basic')
            }
        
        # Generate answer based on question type and relevant content
        question_type = classify_question_type(question_lower)
        answer_data = generate_answer(
            question, 
            question_type, 
            relevant_sections[:5],  # Top 5 most relevant sections
            context_window
        )
        
        # Calculate confidence based on relevance scores and answer quality
        max_score = relevant_sections[0]['score']
        avg_score = sum(s['score'] for s in relevant_sections[:3]) / min(3, len(relevant_sections))
        confidence_score = min(0.95, (max_score * 0.6 + avg_score * 0.4))
        
        source_sections = [s['title'] for s in relevant_sections[:5]]
        
        return {
            'success': True,
            'answer': answer_data['answer'],
            'confidence_score': round(confidence_score, 2),
            'source_sections': source_sections if include_references else [],
            'question_classification': question_type,
            'answer_metadata': {
                'sections_searched': len(protocol_sections),
                'relevant_sections_found': len(relevant_sections),
                'primary_source': relevant_sections[0]['title'],
                'answer_length': len(answer_data['answer']),
                'generated_at': datetime.now().isoformat()
            },
            'follow_up_questions': generate_follow_up_questions(question_type, answer_data['answer']),
            'context_analysis': analyze_context(question_type, relevant_sections[:5]),
            'complexity_level': input_data.get('complexity_level', 'basic')
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error processing protocol Q&A: {str(e)}'
        }

def extract_keywords(text: str) -> List[str]:
    """Extract meaningful keywords from question text."""
    # Remove common question words and extract meaningful terms
    stop_words = {
        'what', 'when', 'where', 'who', 'why', 'how', 'is', 'are', 'was', 'were',
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'be', 'been', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
        'can', 'must'
    }
    
    # Extract words and filter
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    keywords = [word for word in words if word not in stop_words]
    
    # Add medical/clinical term patterns
    medical_patterns = [
        r'\b(?:dose|dosage|dosing)\b',
        r'\b(?:adverse|event|events|ae|sae)\b',
        r'\b(?:inclusion|exclusion|criteria)\b',
        r'\b(?:primary|secondary|endpoint)\b',
        r'\b(?:randomization|randomized|blinded)\b',
        r'\b(?:safety|efficacy|outcome)\b',
        r'\b(?:visit|visits|follow.?up)\b',
        r'\b(?:consent|informed)\b',
        r'\b(?:protocol|deviation|amendment)\b'
    ]
    
    for pattern in medical_patterns:
        matches = re.findall(pattern, text)
        keywords.extend(matches)
    
    return list(set(keywords))  # Remove duplicates

def calculate_relevance_score(keywords: List[str], content: str, section_title: str) -> float:
    """Calculate relevance score between question keywords and content."""
    if not keywords:
        return 0.0
    
    total_score = 0.0
    keyword_matches = 0
    
    # Title matching gets higher weight (including synonyms)
    title_score = 0
    eligibility_synonyms = {
        'eligible': ['inclusion', 'criteria', 'qualify', 'requirements'],
        'criteria': ['inclusion', 'exclusion', 'eligible', 'requirements'],
        'study': ['trial', 'protocol', 'research'],
        'efficacy': ['endpoints', 'objectives', 'outcomes', 'survival'],
        'endpoints': ['objectives', 'outcomes', 'efficacy', 'survival'],
        'primary': ['main', 'principal', 'primary'],
        'secondary': ['additional', 'secondary'],
        'survival': ['endpoints', 'efficacy', 'outcomes']
    }
    
    for keyword in keywords:
        if keyword in section_title.lower():
            title_score += 2.0
            keyword_matches += 1
        # Check synonyms
        elif keyword in eligibility_synonyms:
            for synonym in eligibility_synonyms[keyword]:
                if synonym in section_title.lower():
                    title_score += 1.5  # Slightly lower score for synonyms
                    keyword_matches += 1
                    break
    
    # Content matching
    content_score = 0
    for keyword in keywords:
        # Exact matches
        if keyword in content:
            content_score += 1.0
            keyword_matches += 1
        # Partial matches (substring)
        elif any(keyword in word for word in content.split()):
            content_score += 0.5
            keyword_matches += 0.5
    
    # Calculate final score
    if keyword_matches > 0:
        total_score = (title_score + content_score) / len(keywords)
        # Bonus for multiple keyword matches
        coverage_bonus = keyword_matches / len(keywords)
        total_score *= (0.5 + coverage_bonus * 0.5)
    
    return min(1.0, total_score)

def classify_question_type(question: str) -> str:
    """Classify the type of question being asked."""
    question = question.lower()
    
    if any(word in question for word in ['what is', 'define', 'definition', 'explain']):
        return 'definition'
    elif any(word in question for word in ['how many', 'how much', 'duration', 'number']):
        return 'quantitative'
    elif any(word in question for word in ['when', 'schedule', 'timing', 'time']):
        return 'temporal'
    elif any(word in question for word in ['how', 'procedure', 'process', 'method']):
        return 'procedural'
    elif any(word in question for word in ['who', 'eligibility', 'criteria', 'qualify']):
        return 'eligibility'
    elif any(word in question for word in ['where', 'location', 'site']):
        return 'location'
    elif any(word in question for word in ['dose', 'dosing', 'medication', 'treatment']):
        return 'treatment'
    elif any(word in question for word in ['safety', 'adverse', 'risk', 'side effect']):
        return 'safety'
    elif any(word in question for word in ['endpoint', 'outcome', 'efficacy', 'measure']):
        return 'endpoint'
    else:
        return 'general'

def generate_answer(question: str, question_type: str, relevant_sections: List[Dict], context_window: int) -> Dict:
    """Generate an answer based on question type and relevant content."""
    
    # Combine relevant content
    combined_content = ""
    for section in relevant_sections:
        section_text = f"\n[From {section['title']}]:\n{section['content'][:context_window]}\n"
        combined_content += section_text
    
    # Generate answer based on question type
    if question_type == 'definition':
        answer = generate_definition_answer(question, combined_content)
    elif question_type == 'quantitative':
        answer = generate_quantitative_answer(question, combined_content)
    elif question_type == 'temporal':
        answer = generate_temporal_answer(question, combined_content)
    elif question_type == 'procedural':
        answer = generate_procedural_answer(question, combined_content)
    elif question_type == 'eligibility':
        answer = generate_eligibility_answer(question, combined_content)
    elif question_type == 'treatment':
        answer = generate_treatment_answer(question, combined_content)
    elif question_type == 'safety':
        answer = generate_safety_answer(question, combined_content)
    elif question_type == 'endpoint':
        answer = generate_endpoint_answer(question, combined_content)
    else:
        answer = generate_general_answer(question, combined_content)
    
    return {'answer': answer}

def generate_definition_answer(question: str, content: str) -> str:
    """Generate answer for definition-type questions."""
    # Look for definitions or explanatory text
    lines = content.split('\n')
    relevant_lines = []
    
    question_terms = extract_keywords(question.lower())
    for line in lines:
        if any(term in line.lower() for term in question_terms):
            relevant_lines.append(line.strip())
    
    if relevant_lines:
        return f"Based on the protocol: {' '.join(relevant_lines[:3])}"
    else:
        return "The protocol contains relevant information, but a specific definition is not clearly stated in the available sections."

def generate_quantitative_answer(question: str, content: str) -> str:
    """Generate answer for quantitative questions."""
    # Look for numbers, percentages, durations
    import re
    numbers = re.findall(r'\b\d+(?:\.\d+)?(?:%|mg|days?|weeks?|months?|years?|subjects?|patients?)?\b', content)
    
    if numbers:
        return f"According to the protocol, relevant quantitative information includes: {', '.join(set(numbers[:5]))}. Please refer to the specific protocol sections for complete context."
    else:
        return "The protocol sections contain relevant information, but specific quantitative details may require review of additional sections."

def generate_temporal_answer(question: str, content: str) -> str:
    """Generate answer for timing/schedule questions."""
    # Look for time-related information
    time_phrases = re.findall(r'\b(?:day|week|month|year|visit|screening|baseline|follow.?up)\s+\d+\b', content, re.IGNORECASE)
    schedule_info = re.findall(r'\b(?:daily|weekly|monthly|quarterly|annually|at|during|after|before)\b[^.]*', content, re.IGNORECASE)
    
    relevant_info = time_phrases + schedule_info
    if relevant_info:
        return f"Regarding timing and schedule: {' '.join(set(relevant_info[:3]))}. Please review the complete protocol schedule for full details."
    else:
        return "The protocol contains schedule information, but specific timing details may be found in dedicated schedule sections."

def generate_procedural_answer(question: str, content: str) -> str:
    """Generate answer for procedural questions."""
    # Look for procedural language
    procedure_lines = []
    lines = content.split('.')
    
    for line in lines:
        if any(word in line.lower() for word in ['will', 'shall', 'must', 'should', 'procedure', 'process', 'method', 'performed']):
            procedure_lines.append(line.strip())
    
    if procedure_lines:
        return f"Regarding procedures: {'. '.join(procedure_lines[:2])}."
    else:
        return "The protocol contains procedural information. Please refer to the methodology or procedures sections for detailed steps."

def generate_eligibility_answer(question: str, content: str) -> str:
    """Generate answer for eligibility questions."""
    # Look for inclusion/exclusion criteria
    criteria_text = []
    lines = content.split('\n')
    
    for line in lines:
        if any(word in line.lower() for word in ['inclusion', 'exclusion', 'eligible', 'criteria', 'must', 'required']):
            criteria_text.append(line.strip())
    
    if criteria_text:
        return f"Eligibility criteria include: {' '.join(criteria_text[:3])}. Please refer to the complete inclusion/exclusion criteria sections."
    else:
        return "The protocol contains eligibility information. Please review the inclusion and exclusion criteria sections for complete requirements."

def generate_treatment_answer(question: str, content: str) -> str:
    """Generate answer for treatment-related questions."""
    # Look for treatment/dosing information
    treatment_info = []
    lines = content.split('.')
    
    for line in lines:
        if any(word in line.lower() for word in ['dose', 'dosing', 'treatment', 'medication', 'drug', 'therapy', 'administered']):
            treatment_info.append(line.strip())
    
    if treatment_info:
        return f"Treatment information: {'. '.join(treatment_info[:2])}. Please consult the complete treatment protocol for full dosing details."
    else:
        return "The protocol contains treatment information. Please refer to the treatment or investigational product sections for specific details."

def generate_safety_answer(question: str, content: str) -> str:
    """Generate answer for safety questions."""
    # Look for safety information
    safety_info = []
    lines = content.split('.')
    
    for line in lines:
        if any(word in line.lower() for word in ['safety', 'adverse', 'risk', 'monitoring', 'assessment', 'toxicity']):
            safety_info.append(line.strip())
    
    if safety_info:
        return f"Safety considerations: {'. '.join(safety_info[:2])}. Please review the complete safety monitoring plan."
    else:
        return "The protocol contains safety information. Please refer to the safety monitoring and adverse event sections."

def generate_endpoint_answer(question: str, content: str) -> str:
    """Generate answer for endpoint questions."""
    # Look for endpoint information
    endpoint_info = []
    lines = content.split('.')
    
    for line in lines:
        if any(word in line.lower() for word in ['endpoint', 'outcome', 'efficacy', 'objective', 'measure', 'assessment']):
            endpoint_info.append(line.strip())
    
    if endpoint_info:
        return f"Study endpoints: {'. '.join(endpoint_info[:2])}. Please refer to the objectives and endpoints sections for complete details."
    else:
        return "The protocol contains endpoint information. Please review the study objectives and endpoints sections."

def generate_general_answer(question: str, content: str) -> str:
    """Generate general answer when question type is unclear."""
    # Extract most relevant sentences
    sentences = content.split('.')
    question_keywords = extract_keywords(question.lower())
    
    scored_sentences = []
    for sentence in sentences:
        score = sum(1 for keyword in question_keywords if keyword in sentence.lower())
        if score > 0:
            scored_sentences.append((sentence.strip(), score))
    
    scored_sentences.sort(key=lambda x: x[1], reverse=True)
    
    if scored_sentences:
        top_sentences = [s[0] for s in scored_sentences[:2]]
        return f"Based on the protocol: {'. '.join(top_sentences)}."
    else:
        return "The protocol contains information related to your question. Please review the relevant sections for detailed information."

def suggest_sections_for_question(question: str) -> List[str]:
    """Suggest protocol sections that might contain the answer."""
    question = question.lower()
    suggestions = []
    
    section_mappings = {
        'inclusion|exclusion|eligibility|criteria': ['Inclusion Criteria', 'Exclusion Criteria', 'Subject Selection'],
        'dose|dosing|treatment|medication': ['Treatment Protocol', 'Investigational Product', 'Dosing Schedule'],
        'safety|adverse|risk|monitoring': ['Safety Monitoring', 'Adverse Event Reporting', 'Risk Assessment'],
        'endpoint|outcome|efficacy|objective': ['Study Objectives', 'Endpoints', 'Efficacy Assessments'],
        'schedule|visit|timing|follow': ['Study Schedule', 'Visit Schedule', 'Follow-up Procedures'],
        'consent|informed': ['Informed Consent', 'Consent Process'],
        'randomization|blinding': ['Randomization', 'Blinding Procedures'],
        'statistics|analysis|power': ['Statistical Analysis Plan', 'Data Analysis', 'Sample Size']
    }
    
    for pattern, sections in section_mappings.items():
        if re.search(pattern, question):
            suggestions.extend(sections)
    
    return list(set(suggestions)) if suggestions else ['Background', 'Study Design', 'Methodology']

def generate_follow_up_questions(question_type: str, answer: str) -> List[str]:
    """Generate relevant follow-up questions based on the answer provided."""
    follow_ups = []
    
    type_based_questions = {
        'definition': [
            "Are there any related terms I should understand?",
            "How does this definition apply in practice?"
        ],
        'quantitative': [
            "What is the rationale for these specific values?",
            "Are there any safety considerations related to these numbers?"
        ],
        'temporal': [
            "What happens if the schedule cannot be followed?",
            "Are there any flexibility provisions in the timing?"
        ],
        'procedural': [
            "Who is responsible for performing these procedures?",
            "What training is required for these procedures?"
        ],
        'eligibility': [
            "Are there any exceptions to these criteria?",
            "How are borderline cases handled?"
        ],
        'treatment': [
            "How should dose modifications be handled?",
            "What are the safety monitoring requirements?"
        ],
        'safety': [
            "What is the reporting timeline for these events?",
            "Who should be contacted in case of safety concerns?"
        ],
        'endpoint': [
            "How will these endpoints be measured?",
            "What is the analysis plan for these endpoints?"
        ]
    }
    
    if question_type in type_based_questions:
        follow_ups = type_based_questions[question_type]
    else:
        follow_ups = [
            "Could you provide more specific details?",
            "Are there related sections I should review?"
        ]
    
    return follow_ups[:2]  # Return top 2 follow-up questions


def analyze_context(question_type: str, relevant_sections: List[Dict]) -> Dict[str, Any]:
    """Analyze the context and relevance of the protocol sections for the question."""
    if not relevant_sections:
        return {
            'sections_analyzed': 0,
            'relevance_distribution': {},
            'coverage_assessment': 'insufficient',
            'recommendations': ['More protocol sections needed to answer this question']
        }
    
    # Analyze relevance distribution
    relevance_scores = [section.get('score', 0) for section in relevant_sections]
    avg_relevance = sum(relevance_scores) / len(relevance_scores)
    
    coverage_assessment = 'excellent' if avg_relevance > 0.8 else 'good' if avg_relevance > 0.6 else 'moderate'
    
    return {
        'sections_analyzed': len(relevant_sections),
        'relevance_distribution': {
            'high_relevance': len([s for s in relevance_scores if s > 0.7]),
            'medium_relevance': len([s for s in relevance_scores if 0.4 <= s <= 0.7]),
            'low_relevance': len([s for s in relevance_scores if s < 0.4])
        },
        'coverage_assessment': coverage_assessment,
        'recommendations': [
            f'Answer based on {len(relevant_sections)} relevant sections',
            f'Average relevance score: {avg_relevance:.2f}'
        ]
    }