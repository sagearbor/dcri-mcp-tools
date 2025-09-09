"""
Meeting Summarizer Tool
AI-powered meeting transcript summarization for clinical trials
"""

from typing import Dict, List, Any
import re
from datetime import datetime, timedelta

def run(input_data: Dict) -> Dict:
    """
    Summarize meeting transcripts and extract key information for clinical trials
    
    Args:
        input_data: Dictionary containing:
            - transcript: Meeting transcript text
            - meeting_type: Type of meeting (investigator, dsmb, steering_committee, etc.)
            - meeting_date: Date of the meeting
            - attendees: List of attendee information
            - summary_style: Style of summary (brief, detailed, action_items)
            - extract_decisions: Whether to extract decisions made
    
    Returns:
        Dictionary with meeting summary, action items, decisions, and key topics
    """
    try:
        transcript = input_data.get('transcript', '').strip()
        meeting_type = input_data.get('meeting_type', 'general')
        meeting_date = input_data.get('meeting_date', datetime.now().isoformat())
        attendees = input_data.get('attendees', [])
        summary_style = input_data.get('summary_style', 'detailed')
        extract_decisions = input_data.get('extract_decisions', True)
        
        if not transcript:
            return {
                'success': False,
                'error': 'No meeting transcript provided'
            }
        
        # Clean and prepare transcript
        cleaned_transcript = clean_transcript(transcript)
        
        # Extract speakers and their contributions
        speaker_analysis = extract_speakers_and_contributions(cleaned_transcript)
        
        # Extract key topics discussed
        key_topics = extract_key_topics(cleaned_transcript, meeting_type)
        
        # Extract action items
        action_items = extract_action_items(cleaned_transcript)
        
        # Extract decisions if requested
        decisions = []
        if extract_decisions:
            decisions = extract_decisions_made(cleaned_transcript)
        
        # Generate summary based on style
        if summary_style == 'brief':
            summary = generate_brief_summary(cleaned_transcript, key_topics, meeting_type)
        elif summary_style == 'action_items':
            summary = generate_action_focused_summary(action_items, decisions)
        else:  # detailed
            summary = generate_detailed_summary(
                cleaned_transcript, key_topics, speaker_analysis, meeting_type
            )
        
        # Extract follow-up requirements
        follow_up_items = extract_follow_up_requirements(cleaned_transcript, action_items)
        
        # Identify risks and concerns raised
        risks_concerns = extract_risks_and_concerns(cleaned_transcript)
        
        # Generate meeting statistics
        meeting_stats = generate_meeting_statistics(
            cleaned_transcript, speaker_analysis, attendees
        )
        
        # Extract timeline and deadlines
        timelines = extract_timelines_and_deadlines(cleaned_transcript)
        
        return {
            'success': True,
            'meeting_summary': {
                'meeting_type': meeting_type,
                'meeting_date': meeting_date,
                'summary_style': summary_style,
                'executive_summary': summary,
                'key_topics': key_topics,
                'main_discussions': extract_main_discussions(cleaned_transcript),
                'generated_at': datetime.now().isoformat()
            },
            'action_items': action_items,
            'decisions_made': decisions,
            'follow_up_requirements': follow_up_items,
            'risks_and_concerns': risks_concerns,
            'timelines_and_deadlines': timelines,
            'attendee_analysis': {
                'speaker_contributions': speaker_analysis,
                'attendance_summary': generate_attendance_summary(attendees, speaker_analysis),
                'participation_metrics': calculate_participation_metrics(speaker_analysis)
            },
            'meeting_statistics': meeting_stats,
            'next_steps': generate_next_steps(action_items, follow_up_items, decisions),
            'meeting_effectiveness': assess_meeting_effectiveness(
                action_items, decisions, key_topics, meeting_stats
            )
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error summarizing meeting: {str(e)}'
        }

def clean_transcript(transcript: str) -> str:
    """Clean and normalize the transcript text."""
    # Remove excessive whitespace
    cleaned = re.sub(r'\n\s*\n', '\n\n', transcript)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Fix common transcription errors
    replacements = {
        r'\bum\b|\buh\b|\ber\b': '',  # Remove filler words
        r'\[inaudible\]|\[unclear\]|\[crosstalk\]': '[UNCLEAR]',
        r'\bthat that\b': 'that',  # Remove duplicate words
        r'\bthe the\b': 'the',
        r'\band and\b': 'and'
    }
    
    for pattern, replacement in replacements.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()

def extract_speakers_and_contributions(transcript: str) -> Dict:
    """Extract speakers and analyze their contributions."""
    # Look for speaker patterns
    speaker_patterns = [
        r'^([A-Z][a-z]+ [A-Z][a-z]+|[A-Z][a-zA-Z\s]+|Dr\.\s+\w+|\w+):',  # Name: format
        r'\[([A-Z][a-z]+ [A-Z][a-z]+|[A-Z][a-zA-Z\s]+)\]',  # [Name] format
        r'([A-Z]+[A-Z\s]*[A-Z]):',  # LASTNAME: format
    ]
    
    speakers = {}
    current_speaker = 'Unknown'
    
    lines = transcript.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check for speaker identification
        speaker_found = False
        for pattern in speaker_patterns:
            match = re.match(pattern, line)
            if match:
                speaker_name = match.group(1).strip()
                current_speaker = normalize_speaker_name(speaker_name)
                speaker_found = True
                
                # Initialize speaker data
                if current_speaker not in speakers:
                    speakers[current_speaker] = {
                        'total_words': 0,
                        'contributions': [],
                        'key_topics': [],
                        'question_count': 0,
                        'decision_statements': 0
                    }
                
                # Extract the content after speaker identification
                content = re.sub(pattern, '', line).strip()
                if content:
                    speakers[current_speaker]['contributions'].append(content)
                    speakers[current_speaker]['total_words'] += len(content.split())
                break
        
        # If no speaker pattern found, attribute to current speaker
        if not speaker_found and line:
            if current_speaker not in speakers:
                speakers[current_speaker] = {
                    'total_words': 0,
                    'contributions': [],
                    'key_topics': [],
                    'question_count': 0,
                    'decision_statements': 0
                }
            
            speakers[current_speaker]['contributions'].append(line)
            speakers[current_speaker]['total_words'] += len(line.split())
            
            # Count questions
            if '?' in line:
                speakers[current_speaker]['question_count'] += line.count('?')
            
            # Count decision statements
            if any(phrase in line.lower() for phrase in [
                'we decide', 'decided to', 'conclusion is', 'we agree', 'approved'
            ]):
                speakers[current_speaker]['decision_statements'] += 1
    
    return speakers

def normalize_speaker_name(name: str) -> str:
    """Normalize speaker names for consistency."""
    # Remove titles and clean up
    name = re.sub(r'^(Dr\.|Mr\.|Ms\.|Mrs\.|Prof\.)\s*', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Convert to title case
    return name.title()

def extract_key_topics(transcript: str, meeting_type: str) -> List[Dict]:
    """Extract key topics discussed in the meeting."""
    # Define topic patterns based on meeting type
    topic_patterns = {
        'investigator': [
            r'enrollment|recruitment|screening',
            r'adverse event|safety|tolerability',
            r'protocol deviation|amendment',
            r'data quality|monitoring',
            r'supply|drug accountability',
            r'training|certification'
        ],
        'dsmb': [
            r'safety review|safety data',
            r'efficacy|interim analysis',
            r'risk.?benefit|stopping',
            r'recommendation|continue',
            r'unblinding|emergency',
            r'statistical analysis'
        ],
        'steering_committee': [
            r'study design|protocol',
            r'operational|timeline',
            r'budget|resources',
            r'regulatory|submission',
            r'publication|dissemination',
            r'site management'
        ],
        'general': [
            r'action item|follow.?up',
            r'decision|approve|reject',
            r'timeline|deadline|schedule',
            r'issue|concern|problem',
            r'update|progress|status',
            r'next steps|future'
        ]
    }
    
    patterns = topic_patterns.get(meeting_type, topic_patterns['general'])
    patterns.extend(topic_patterns['general'])  # Always include general patterns
    
    topics = []
    transcript_lower = transcript.lower()
    
    # Extract sentences containing topic keywords
    sentences = re.split(r'[.!?]+', transcript)
    
    for pattern in patterns:
        topic_sentences = []
        for sentence in sentences:
            if re.search(pattern, sentence, re.IGNORECASE):
                topic_sentences.append(sentence.strip())
        
        if topic_sentences:
            # Determine topic name from pattern
            topic_name = pattern.replace('\\b', '').replace('|', ' or ').replace('\\', '').replace('?', '')
            topics.append({
                'topic': topic_name.title(),
                'frequency': len(topic_sentences),
                'key_points': topic_sentences[:3],  # Top 3 relevant sentences
                'relevance': 'high' if len(topic_sentences) > 2 else 'medium'
            })
    
    # Sort by frequency and return top topics
    topics.sort(key=lambda x: x['frequency'], reverse=True)
    return topics[:10]

def extract_action_items(transcript: str) -> List[Dict]:
    """Extract action items from the transcript."""
    action_indicators = [
        r'action item:?\s*(.+?)(?:\.|$)',
        r'(\w+)\s+will\s+(.+?)(?:\.|$)',
        r'(\w+)\s+to\s+(.+?)(?:by|before|$)',
        r'follow.?up:?\s*(.+?)(?:\.|$)',
        r'next step:?\s*(.+?)(?:\.|$)',
        r'assigned to\s+(\w+):?\s*(.+?)(?:\.|$)',
        r'todo:?\s*(.+?)(?:\.|$)',
        r'(\w+)\s+responsible for\s+(.+?)(?:\.|$)'
    ]
    
    action_items = []
    
    for pattern in action_indicators:
        matches = re.finditer(pattern, transcript, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            if len(match.groups()) == 1:
                # Single group - just the action
                action_text = match.group(1).strip()
                assignee = 'Unassigned'
            else:
                # Two groups - assignee and action
                assignee = match.group(1).strip()
                action_text = match.group(2).strip()
            
            if action_text and len(action_text) > 5:  # Filter out very short items
                # Extract deadline if present
                deadline = extract_deadline_from_text(action_text)
                
                # Determine priority
                priority = determine_action_priority(action_text)
                
                action_items.append({
                    'action': action_text,
                    'assignee': normalize_speaker_name(assignee),
                    'deadline': deadline,
                    'priority': priority,
                    'status': 'open',
                    'extracted_from': match.group(0)
                })
    
    # Remove duplicates
    seen_actions = set()
    unique_actions = []
    for item in action_items:
        action_key = item['action'].lower()
        if action_key not in seen_actions:
            seen_actions.add(action_key)
            unique_actions.append(item)
    
    return unique_actions

def extract_deadline_from_text(text: str) -> str:
    """Extract deadline information from action text."""
    deadline_patterns = [
        r'by\s+([A-Z][a-z]+\s+\d{1,2})',  # by January 15
        r'before\s+([A-Z][a-z]+\s+\d{1,2})',  # before March 20
        r'by\s+(next\s+week|next\s+month)',  # by next week
        r'within\s+(\d+\s+(?:days?|weeks?|months?))',  # within 2 weeks
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',  # 01/15/2024
        r'(end of\s+(?:week|month|quarter))'  # end of month
    ]
    
    for pattern in deadline_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def determine_action_priority(action_text: str) -> str:
    """Determine priority based on action text content."""
    action_lower = action_text.lower()
    
    high_priority_indicators = [
        'urgent', 'asap', 'immediately', 'critical', 'emergency',
        'safety', 'regulatory', 'compliance', 'deadline'
    ]
    
    medium_priority_indicators = [
        'important', 'needed', 'required', 'follow up', 'review'
    ]
    
    if any(indicator in action_lower for indicator in high_priority_indicators):
        return 'high'
    elif any(indicator in action_lower for indicator in medium_priority_indicators):
        return 'medium'
    else:
        return 'low'

def extract_decisions_made(transcript: str) -> List[Dict]:
    """Extract decisions made during the meeting."""
    decision_indicators = [
        r'decision:?\s*(.+?)(?:\.|$)',
        r'decided to\s+(.+?)(?:\.|$)',
        r'we agree to\s+(.+?)(?:\.|$)',
        r'approved:?\s*(.+?)(?:\.|$)',
        r'rejected:?\s*(.+?)(?:\.|$)',
        r'conclusion:?\s*(.+?)(?:\.|$)',
        r'resolution:?\s*(.+?)(?:\.|$)',
        r'it was decided that\s+(.+?)(?:\.|$)'
    ]
    
    decisions = []
    
    for pattern in decision_indicators:
        matches = re.finditer(pattern, transcript, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            decision_text = match.group(1).strip()
            
            if decision_text and len(decision_text) > 10:
                # Categorize decision
                decision_type = categorize_decision(decision_text)
                
                # Extract impact if mentioned
                impact = assess_decision_impact(decision_text)
                
                decisions.append({
                    'decision': decision_text,
                    'type': decision_type,
                    'impact': impact,
                    'timestamp': None,  # Could be extracted from context
                    'rationale': extract_rationale_from_context(decision_text, transcript)
                })
    
    return decisions

def categorize_decision(decision_text: str) -> str:
    """Categorize the type of decision made."""
    decision_lower = decision_text.lower()
    
    if any(word in decision_lower for word in ['protocol', 'amendment', 'design']):
        return 'protocol_related'
    elif any(word in decision_lower for word in ['safety', 'adverse', 'risk']):
        return 'safety_related'
    elif any(word in decision_lower for word in ['enrollment', 'recruitment', 'site']):
        return 'operational'
    elif any(word in decision_lower for word in ['budget', 'cost', 'resource']):
        return 'financial'
    elif any(word in decision_lower for word in ['regulatory', 'submission', 'approval']):
        return 'regulatory'
    elif any(word in decision_lower for word in ['timeline', 'schedule', 'deadline']):
        return 'timeline_related'
    else:
        return 'general'

def assess_decision_impact(decision_text: str) -> str:
    """Assess the potential impact of a decision."""
    decision_lower = decision_text.lower()
    
    high_impact_indicators = [
        'stop', 'terminate', 'halt', 'major', 'significant',
        'all sites', 'study design', 'primary endpoint'
    ]
    
    medium_impact_indicators = [
        'modify', 'change', 'update', 'revise', 'some sites'
    ]
    
    if any(indicator in decision_lower for indicator in high_impact_indicators):
        return 'high'
    elif any(indicator in decision_lower for indicator in medium_impact_indicators):
        return 'medium'
    else:
        return 'low'

def extract_rationale_from_context(decision_text: str, transcript: str) -> str:
    """Extract rationale for decisions from surrounding context."""
    # Find the decision in the transcript and look for surrounding context
    decision_index = transcript.lower().find(decision_text.lower())
    if decision_index == -1:
        return None
    
    # Look for rationale indicators before the decision
    context_before = transcript[max(0, decision_index-500):decision_index]
    rationale_indicators = [
        'because', 'due to', 'reason', 'rationale', 'based on',
        'given that', 'considering', 'since'
    ]
    
    for indicator in rationale_indicators:
        if indicator in context_before.lower():
            # Extract sentence containing the indicator
            sentences = re.split(r'[.!?]', context_before)
            for sentence in reversed(sentences):
                if indicator in sentence.lower():
                    return sentence.strip()
    
    return None

def extract_follow_up_requirements(transcript: str, action_items: List[Dict]) -> List[Dict]:
    """Extract follow-up requirements from the meeting."""
    follow_up_patterns = [
        r'follow up on\s+(.+?)(?:\.|$)',
        r'need to follow up\s+(.+?)(?:\.|$)',
        r'pending:?\s*(.+?)(?:\.|$)',
        r'waiting for\s+(.+?)(?:\.|$)',
        r'next meeting:?\s*(.+?)(?:\.|$)',
        r'recurring:?\s*(.+?)(?:\.|$)'
    ]
    
    follow_ups = []
    
    for pattern in follow_up_patterns:
        matches = re.finditer(pattern, transcript, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            follow_up_text = match.group(1).strip()
            
            if follow_up_text and len(follow_up_text) > 5:
                follow_ups.append({
                    'item': follow_up_text,
                    'type': 'follow_up',
                    'deadline': extract_deadline_from_text(follow_up_text),
                    'related_action_items': find_related_actions(follow_up_text, action_items)
                })
    
    return follow_ups

def find_related_actions(follow_up_text: str, action_items: List[Dict]) -> List[str]:
    """Find action items related to a follow-up requirement."""
    related = []
    follow_up_words = set(follow_up_text.lower().split())
    
    for action in action_items:
        action_words = set(action['action'].lower().split())
        # Check for word overlap
        if len(follow_up_words & action_words) > 2:
            related.append(action['action'])
    
    return related

def extract_risks_and_concerns(transcript: str) -> List[Dict]:
    """Extract risks and concerns raised during the meeting."""
    risk_indicators = [
        r'concern:?\s*(.+?)(?:\.|$)',
        r'risk:?\s*(.+?)(?:\.|$)',
        r'worried about\s+(.+?)(?:\.|$)',
        r'issue:?\s*(.+?)(?:\.|$)',
        r'problem:?\s*(.+?)(?:\.|$)',
        r'challenge:?\s*(.+?)(?:\.|$)',
        r'potential\s+(.+?)(?:\.|$)'
    ]
    
    risks_concerns = []
    
    for pattern in risk_indicators:
        matches = re.finditer(pattern, transcript, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            concern_text = match.group(1).strip()
            
            if concern_text and len(concern_text) > 10:
                # Categorize the concern
                category = categorize_concern(concern_text)
                
                # Assess severity
                severity = assess_concern_severity(concern_text)
                
                risks_concerns.append({
                    'concern': concern_text,
                    'category': category,
                    'severity': severity,
                    'type': 'risk' if 'risk' in match.group(0).lower() else 'concern'
                })
    
    return risks_concerns

def categorize_concern(concern_text: str) -> str:
    """Categorize the type of concern raised."""
    concern_lower = concern_text.lower()
    
    if any(word in concern_lower for word in ['safety', 'adverse', 'harm']):
        return 'safety'
    elif any(word in concern_lower for word in ['enrollment', 'recruitment']):
        return 'enrollment'
    elif any(word in concern_lower for word in ['data', 'quality', 'missing']):
        return 'data_quality'
    elif any(word in concern_lower for word in ['timeline', 'delay', 'schedule']):
        return 'timeline'
    elif any(word in concern_lower for word in ['budget', 'cost', 'funding']):
        return 'financial'
    elif any(word in concern_lower for word in ['regulatory', 'compliance']):
        return 'regulatory'
    else:
        return 'operational'

def assess_concern_severity(concern_text: str) -> str:
    """Assess the severity of a concern."""
    concern_lower = concern_text.lower()
    
    high_severity_indicators = [
        'critical', 'urgent', 'major', 'serious', 'significant',
        'halt', 'stop', 'emergency'
    ]
    
    if any(indicator in concern_lower for indicator in high_severity_indicators):
        return 'high'
    elif any(word in concern_lower for word in ['moderate', 'some', 'minor']):
        return 'low'
    else:
        return 'medium'

def generate_brief_summary(transcript: str, key_topics: List[Dict], meeting_type: str) -> str:
    """Generate a brief meeting summary."""
    summary_parts = []
    
    # Meeting overview
    summary_parts.append(f"This {meeting_type} meeting covered {len(key_topics)} main topics.")
    
    # Top 3 topics
    if key_topics:
        top_topics = [topic['topic'] for topic in key_topics[:3]]
        summary_parts.append(f"Key discussion areas included: {', '.join(top_topics)}.")
    
    # Word count and estimated duration
    word_count = len(transcript.split())
    estimated_duration = max(30, word_count // 150)  # Rough estimate: 150 words per minute
    summary_parts.append(f"The meeting transcript contains approximately {word_count} words, suggesting a {estimated_duration}-minute discussion.")
    
    return ' '.join(summary_parts)

def generate_action_focused_summary(action_items: List[Dict], decisions: List[Dict]) -> str:
    """Generate an action-focused summary."""
    summary_parts = []
    
    if action_items:
        summary_parts.append(f"Meeting resulted in {len(action_items)} action items.")
        
        # Group by priority
        high_priority = [a for a in action_items if a['priority'] == 'high']
        if high_priority:
            summary_parts.append(f"{len(high_priority)} items were marked as high priority.")
    
    if decisions:
        summary_parts.append(f"{len(decisions)} key decisions were made.")
        
        # Group by type
        decision_types = {}
        for decision in decisions:
            decision_type = decision['type']
            decision_types[decision_type] = decision_types.get(decision_type, 0) + 1
        
        if decision_types:
            type_summary = ', '.join([f"{count} {type}" for type, count in decision_types.items()])
            summary_parts.append(f"Decisions covered: {type_summary}.")
    
    if not summary_parts:
        summary_parts.append("Meeting focused on discussions without specific action items or decisions recorded.")
    
    return ' '.join(summary_parts)

def generate_detailed_summary(transcript: str, key_topics: List[Dict], 
                            speaker_analysis: Dict, meeting_type: str) -> str:
    """Generate a detailed meeting summary."""
    summary_parts = []
    
    # Meeting overview
    participant_count = len(speaker_analysis)
    word_count = len(transcript.split())
    
    summary_parts.append(
        f"This {meeting_type} meeting involved {participant_count} participants "
        f"in a comprehensive discussion covering multiple clinical trial aspects."
    )
    
    # Topic coverage
    if key_topics:
        high_relevance_topics = [t for t in key_topics if t['relevance'] == 'high']
        summary_parts.append(
            f"The discussion covered {len(key_topics)} main topics, "
            f"with {len(high_relevance_topics)} receiving extensive attention."
        )
        
        # Detail top topics
        for topic in key_topics[:3]:
            topic_detail = f"- {topic['topic']}: Discussed {topic['frequency']} times"
            if topic['key_points']:
                topic_detail += f" (key point: {topic['key_points'][0][:100]}...)"
            summary_parts.append(topic_detail)
    
    # Participation analysis
    if speaker_analysis:
        most_active = max(speaker_analysis.items(), key=lambda x: x[1]['total_words'])
        summary_parts.append(
            f"Most active participant was {most_active[0]} with {most_active[1]['total_words']} words."
        )
        
        # Question activity
        total_questions = sum(data['question_count'] for data in speaker_analysis.values())
        if total_questions > 0:
            summary_parts.append(f"A total of {total_questions} questions were raised during the meeting.")
    
    return ' '.join(summary_parts)

def extract_main_discussions(transcript: str) -> List[Dict]:
    """Extract main discussion threads from the transcript."""
    # Split transcript into discussion segments
    segments = []
    current_segment = []
    
    lines = transcript.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # If line starts with a speaker, it might be a new discussion point
        if re.match(r'^[A-Z][a-zA-Z\s]+:', line) and current_segment:
            # Save current segment if it has content
            if len(current_segment) > 1:
                segment_text = ' '.join(current_segment)
                topic = extract_topic_from_segment(segment_text)
                segments.append({
                    'topic': topic,
                    'content': segment_text[:300] + '...' if len(segment_text) > 300 else segment_text,
                    'word_count': len(segment_text.split()),
                    'participants': extract_participants_from_segment(' '.join(current_segment))
                })
            current_segment = [line]
        else:
            current_segment.append(line)
    
    # Don't forget the last segment
    if current_segment:
        segment_text = ' '.join(current_segment)
        if len(current_segment) > 1:
            topic = extract_topic_from_segment(segment_text)
            segments.append({
                'topic': topic,
                'content': segment_text[:300] + '...' if len(segment_text) > 300 else segment_text,
                'word_count': len(segment_text.split()),
                'participants': extract_participants_from_segment(segment_text)
            })
    
    # Sort by word count (longer discussions first)
    segments.sort(key=lambda x: x['word_count'], reverse=True)
    return segments[:5]  # Return top 5 main discussions

def extract_topic_from_segment(segment_text: str) -> str:
    """Extract the main topic from a discussion segment."""
    # Look for key clinical trial terms
    clinical_terms = [
        'enrollment', 'recruitment', 'adverse event', 'safety',
        'protocol', 'amendment', 'data', 'monitoring', 'site',
        'regulatory', 'timeline', 'budget', 'efficacy'
    ]
    
    segment_lower = segment_text.lower()
    found_terms = [term for term in clinical_terms if term in segment_lower]
    
    if found_terms:
        return f"Discussion on {', '.join(found_terms[:3])}"
    else:
        # Extract first meaningful phrase
        words = segment_text.split()[:10]
        return ' '.join(words) + '...' if len(words) >= 10 else ' '.join(words)

def extract_participants_from_segment(segment_text: str) -> List[str]:
    """Extract participant names from a discussion segment."""
    # Look for speaker patterns
    speaker_patterns = [
        r'^([A-Z][a-z]+ [A-Z][a-z]+|Dr\.\s+\w+):',
        r'\[([A-Z][a-z]+ [A-Z][a-z]+)\]'
    ]
    
    participants = set()
    for pattern in speaker_patterns:
        matches = re.findall(pattern, segment_text, re.MULTILINE)
        for match in matches:
            participants.add(normalize_speaker_name(match))
    
    return list(participants)

def extract_timelines_and_deadlines(transcript: str) -> List[Dict]:
    """Extract timeline and deadline information."""
    timeline_patterns = [
        r'deadline:?\s*(.+?)(?:\.|$)',
        r'due:?\s*(.+?)(?:\.|$)',
        r'by\s+([\w\s,]+?)(?:\.|$)',
        r'schedule:?\s*(.+?)(?:\.|$)',
        r'timeline:?\s*(.+?)(?:\.|$)',
        r'(\w+ \d{1,2},? \d{4})',  # Date patterns
        r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',  # Date patterns
        r'(next \w+|end of \w+|beginning of \w+)'  # Relative dates
    ]
    
    timelines = []
    
    for pattern in timeline_patterns:
        matches = re.finditer(pattern, transcript, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            timeline_text = match.group(1).strip()
            
            if timeline_text and len(timeline_text) > 3:
                # Categorize timeline
                category = categorize_timeline(timeline_text)
                
                # Extract associated task if possible
                context = extract_timeline_context(match.group(0), transcript)
                
                timelines.append({
                    'timeline': timeline_text,
                    'category': category,
                    'context': context,
                    'urgency': assess_timeline_urgency(timeline_text)
                })
    
    return timelines

def categorize_timeline(timeline_text: str) -> str:
    """Categorize timeline by type."""
    timeline_lower = timeline_text.lower()
    
    if any(word in timeline_lower for word in ['submission', 'regulatory', 'fda']):
        return 'regulatory'
    elif any(word in timeline_lower for word in ['enrollment', 'recruitment']):
        return 'enrollment'
    elif any(word in timeline_lower for word in ['analysis', 'data', 'report']):
        return 'analysis'
    elif any(word in timeline_lower for word in ['meeting', 'review', 'committee']):
        return 'meeting'
    else:
        return 'general'

def extract_timeline_context(timeline_match: str, transcript: str) -> str:
    """Extract context around timeline mentions."""
    timeline_index = transcript.find(timeline_match)
    if timeline_index == -1:
        return None
    
    # Get surrounding context
    context_start = max(0, timeline_index - 100)
    context_end = min(len(transcript), timeline_index + len(timeline_match) + 100)
    context = transcript[context_start:context_end]
    
    # Find the sentence containing the timeline
    sentences = re.split(r'[.!?]', context)
    for sentence in sentences:
        if timeline_match in sentence:
            return sentence.strip()
    
    return None

def assess_timeline_urgency(timeline_text: str) -> str:
    """Assess urgency of timeline items."""
    timeline_lower = timeline_text.lower()
    
    urgent_indicators = ['asap', 'immediately', 'urgent', 'critical', 'today', 'tomorrow']
    soon_indicators = ['next week', 'end of week', 'this month', 'soon']
    
    if any(indicator in timeline_lower for indicator in urgent_indicators):
        return 'urgent'
    elif any(indicator in timeline_lower for indicator in soon_indicators):
        return 'soon'
    else:
        return 'normal'

def generate_attendance_summary(attendees: List, speaker_analysis: Dict) -> Dict:
    """Generate attendance summary comparing expected vs actual."""
    return {
        'expected_attendees': len(attendees),
        'active_speakers': len(speaker_analysis),
        'silent_attendees': max(0, len(attendees) - len(speaker_analysis)),
        'speaker_list': list(speaker_analysis.keys())
    }

def calculate_participation_metrics(speaker_analysis: Dict) -> Dict:
    """Calculate participation metrics."""
    if not speaker_analysis:
        return {}
    
    total_words = sum(data['total_words'] for data in speaker_analysis.values())
    total_questions = sum(data['question_count'] for data in speaker_analysis.values())
    
    # Calculate distribution
    word_distribution = {}
    for speaker, data in speaker_analysis.items():
        if total_words > 0:
            word_distribution[speaker] = round((data['total_words'] / total_words) * 100, 1)
    
    return {
        'total_words': total_words,
        'total_questions': total_questions,
        'average_words_per_speaker': round(total_words / len(speaker_analysis), 1),
        'word_distribution': word_distribution,
        'most_active_speaker': max(speaker_analysis.items(), key=lambda x: x[1]['total_words'])[0],
        'most_inquisitive_speaker': max(speaker_analysis.items(), key=lambda x: x[1]['question_count'])[0] if total_questions > 0 else 'None'
    }

def generate_meeting_statistics(transcript: str, speaker_analysis: Dict, attendees: List) -> Dict:
    """Generate comprehensive meeting statistics."""
    words = transcript.split()
    
    return {
        'transcript_length': {
            'total_words': len(words),
            'total_characters': len(transcript),
            'estimated_duration_minutes': max(30, len(words) // 150)
        },
        'participation': {
            'total_speakers': len(speaker_analysis),
            'expected_attendees': len(attendees),
            'participation_rate': round((len(speaker_analysis) / max(len(attendees), 1)) * 100, 1)
        },
        'content_analysis': {
            'unique_words': len(set(word.lower().strip('.,!?') for word in words)),
            'average_words_per_sentence': len(words) // max(transcript.count('.') + transcript.count('!') + transcript.count('?'), 1),
            'question_density': round((transcript.count('?') / len(words)) * 100, 2)
        }
    }

def generate_next_steps(action_items: List[Dict], follow_up_items: List[Dict], 
                       decisions: List[Dict]) -> List[str]:
    """Generate next steps based on meeting outcomes."""
    next_steps = []
    
    # From action items
    urgent_actions = [item for item in action_items if item['priority'] == 'high']
    if urgent_actions:
        next_steps.append(f"Complete {len(urgent_actions)} high-priority action items")
    
    # From decisions
    implementation_decisions = [d for d in decisions if d['impact'] in ['high', 'medium']]
    if implementation_decisions:
        next_steps.append(f"Implement {len(implementation_decisions)} key decisions made")
    
    # From follow-ups
    if follow_up_items:
        next_steps.append(f"Address {len(follow_up_items)} follow-up requirements")
    
    # Schedule next meeting if needed
    if action_items or follow_up_items:
        next_steps.append("Schedule follow-up meeting to review progress")
    
    # Communication
    if decisions or urgent_actions:
        next_steps.append("Communicate outcomes to relevant stakeholders")
    
    return next_steps[:5]  # Return top 5 next steps

def assess_meeting_effectiveness(action_items: List[Dict], decisions: List[Dict], 
                               key_topics: List[Dict], meeting_stats: Dict) -> Dict:
    """Assess the effectiveness of the meeting."""
    effectiveness_score = 0
    assessment_notes = []
    
    # Productivity indicators
    if action_items:
        effectiveness_score += min(30, len(action_items) * 5)  # Cap at 30 points
        assessment_notes.append(f"{len(action_items)} action items identified")
    
    if decisions:
        effectiveness_score += min(25, len(decisions) * 8)  # Cap at 25 points
        assessment_notes.append(f"{len(decisions)} decisions made")
    
    # Topic coverage
    if key_topics:
        high_relevance_count = len([t for t in key_topics if t['relevance'] == 'high'])
        effectiveness_score += min(20, high_relevance_count * 4)
        assessment_notes.append(f"{len(key_topics)} topics covered comprehensively")
    
    # Participation
    participation_rate = meeting_stats.get('participation', {}).get('participation_rate', 0)
    effectiveness_score += min(25, participation_rate // 4)  # Convert percentage to score
    
    if participation_rate > 75:
        assessment_notes.append("High participation rate achieved")
    elif participation_rate < 50:
        assessment_notes.append("Low participation - consider engagement strategies")
    
    # Overall assessment
    if effectiveness_score >= 80:
        overall = 'highly_effective'
    elif effectiveness_score >= 60:
        overall = 'effective'
    elif effectiveness_score >= 40:
        overall = 'moderately_effective'
    else:
        overall = 'needs_improvement'
    
    return {
        'effectiveness_score': min(100, effectiveness_score),
        'overall_assessment': overall,
        'assessment_notes': assessment_notes,
        'improvement_suggestions': generate_improvement_suggestions(
            action_items, decisions, key_topics, meeting_stats
        )
    }

def generate_improvement_suggestions(action_items: List[Dict], decisions: List[Dict], 
                                   key_topics: List[Dict], meeting_stats: Dict) -> List[str]:
    """Generate suggestions for improving future meetings."""
    suggestions = []
    
    # Based on action items
    if not action_items:
        suggestions.append("Consider defining more specific action items with clear deliverables")
    elif len([a for a in action_items if a['assignee'] == 'Unassigned']) > len(action_items) // 2:
        suggestions.append("Assign specific owners to action items for better accountability")
    
    # Based on decisions
    if not decisions and len(key_topics) > 3:
        suggestions.append("Aim to reach more concrete decisions on key discussion points")
    
    # Based on participation
    participation_rate = meeting_stats.get('participation', {}).get('participation_rate', 100)
    if participation_rate < 70:
        suggestions.append("Encourage broader participation from all attendees")
    
    # Based on meeting length
    estimated_duration = meeting_stats.get('transcript_length', {}).get('estimated_duration_minutes', 60)
    if estimated_duration > 120:
        suggestions.append("Consider breaking long meetings into focused sessions")
    
    # Based on follow-up needs
    if not action_items and not decisions:
        suggestions.append("Ensure meetings result in concrete outcomes and next steps")
    
    return suggestions[:4]  # Return top 4 suggestions