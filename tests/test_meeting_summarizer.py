import pytest
from tools.meeting_summarizer import run


def test_meeting_summarizer_basic():
    """Test basic meeting summarization."""
    input_data = {
        "transcript": """
Dr. Smith: Welcome everyone to today's investigator meeting. We need to discuss enrollment progress.
Dr. Jones: Our site has enrolled 15 patients so far this quarter.
Study Coordinator: We're seeing some challenges with patient retention.
Dr. Smith: Action item: Dr. Jones will review retention strategies by next week.
        """,
        "meeting_type": "investigator",
        "attendees": [
            {"name": "Dr. Smith", "role": "Principal Investigator"},
            {"name": "Dr. Jones", "role": "Site Investigator"},
            {"name": "Study Coordinator", "role": "Coordinator"}
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["meeting_summary"]["meeting_type"] == "investigator"
    assert len(result["action_items"]) > 0
    assert "retention strategies" in result["action_items"][0]["action"]
    assert result["attendee_analysis"]["speaker_contributions"]


def test_meeting_summarizer_action_items_extraction():
    """Test action item extraction."""
    input_data = {
        "transcript": """
Chair: We need to address the following items.
Dr. A: Action item: I will review the safety data by Friday.
Dr. B: John will update the protocol by next month.
Coordinator: Follow-up needed on patient enrollment numbers.
Dr. A: Sarah to prepare the interim report before the board meeting.
        """
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["action_items"]) >= 3
    
    # Check for specific action items
    actions = [item["action"] for item in result["action_items"]]
    assert any("safety data" in action for action in actions)
    assert any("protocol" in action for action in actions)
    assert any("enrollment" in action for action in actions)


def test_meeting_summarizer_decisions_extraction():
    """Test decision extraction."""
    input_data = {
        "transcript": """
Chair: We need to make a decision on the protocol amendment.
Dr. Smith: I propose we move forward with the dosing change.
Dr. Jones: I agree with that approach.
Chair: Decision: We will proceed with the protocol amendment as discussed.
Medical Monitor: It was decided that safety monitoring will increase to weekly.
        """,
        "extract_decisions": True
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["decisions_made"]) >= 2
    
    decisions = [decision["decision"] for decision in result["decisions_made"]]
    assert any("protocol amendment" in decision for decision in decisions)
    assert any("safety monitoring" in decision for decision in decisions)


def test_meeting_summarizer_dsmb_meeting():
    """Test DSMB-specific meeting analysis."""
    input_data = {
        "transcript": """
DSMB Chair: Welcome to the Data Safety Monitoring Board meeting.
Biostatistician: The interim analysis shows no safety concerns at this time.
Medical Monitor: We've reviewed all serious adverse events.
DSMB Chair: Recommendation: The study should continue as planned.
Member: The risk-benefit profile remains acceptable.
        """,
        "meeting_type": "dsmb"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert result["meeting_summary"]["meeting_type"] == "dsmb"
    assert len(result["key_topics"]) > 0
    
    # Should identify safety-related topics
    topics = [topic["topic"] for topic in result["key_topics"]]
    assert any("safety" in topic.lower() for topic in topics)


def test_meeting_summarizer_brief_summary():
    """Test brief summary generation."""
    input_data = {
        "transcript": """
PI: Today we're discussing study progress and challenges.
CRA: Enrollment is at 75% of target.
Data Manager: We have some data quality issues to address.
PI: Let's schedule follow-up meetings for next month.
        """,
        "summary_style": "brief"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    summary = result["meeting_summary"]["executive_summary"]
    assert len(summary) < 500  # Brief summary should be concise
    assert "progress" in summary or "enrollment" in summary


def test_meeting_summarizer_action_focused_summary():
    """Test action-focused summary."""
    input_data = {
        "transcript": """
Manager: We have three action items today.
Dr. A: I'll complete the safety review by Friday.
Dr. B: Data analysis will be done next week.
Coordinator: Patient recruitment plan needs updating.
Manager: Decision: We'll implement the new screening process.
        """,
        "summary_style": "action_items"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["action_items"]) >= 3
    summary = result["meeting_summary"]["executive_summary"]
    assert "action items" in summary or "decisions" in summary


def test_meeting_summarizer_speaker_analysis():
    """Test speaker contribution analysis."""
    input_data = {
        "transcript": """
Dr. Smith: Welcome everyone. We have a full agenda today.
Dr. Smith: First, let's review enrollment numbers from each site.
Dr. Jones: Our site enrolled 10 patients this month.
Dr. Brown: We had some challenges but managed 8 enrollments.
Dr. Smith: Thank you both. Any questions about the data?
Dr. Jones: What's our target for next quarter?
        """,
        "attendees": [
            {"name": "Dr. Smith", "role": "PI"},
            {"name": "Dr. Jones", "role": "Investigator"},
            {"name": "Dr. Brown", "role": "Investigator"}
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    speaker_analysis = result["attendee_analysis"]["speaker_contributions"]
    
    assert "Dr. Smith" in speaker_analysis
    assert "Dr. Jones" in speaker_analysis
    assert speaker_analysis["Dr. Smith"]["total_words"] > speaker_analysis["Dr. Jones"]["total_words"]
    assert speaker_analysis["Dr. Jones"]["question_count"] >= 1


def test_meeting_summarizer_risks_and_concerns():
    """Test extraction of risks and concerns."""
    input_data = {
        "transcript": """
PI: I'm concerned about the slow enrollment rate.
CRA: There's a risk we won't meet our timeline.
Safety Monitor: We need to be worried about the recent AE reports.
Data Manager: The main issue is data quality at some sites.
PI: This could be a problem for the study completion.
        """
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["risks_and_concerns"]) > 0
    
    concerns = [item["concern"] for item in result["risks_and_concerns"]]
    assert any("enrollment" in concern for concern in concerns)
    assert any("timeline" in concern or "data quality" in concern for concern in concerns)


def test_meeting_summarizer_follow_up_requirements():
    """Test follow-up requirements extraction."""
    input_data = {
        "transcript": """
Chair: We need to follow up on the protocol deviation reports.
Manager: Pending approval from the IRB for the amendment.
Coordinator: Waiting for updated forms from the sponsor.
PI: Next meeting scheduled for two weeks from today.
        """
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["follow_up_requirements"]) > 0
    
    follow_ups = [item["item"] for item in result["follow_up_requirements"]]
    assert any("protocol deviation" in follow_up for follow_up in follow_ups)


def test_meeting_summarizer_empty_transcript():
    """Test handling of empty transcript."""
    input_data = {
        "transcript": "",
        "meeting_type": "investigator"
    }
    
    result = run(input_data)
    
    assert result["success"] == False
    assert "No meeting transcript provided" in result["error"]


def test_meeting_summarizer_temporal_analysis():
    """Test temporal pattern analysis."""
    input_data = {
        "transcript": """
[10:00] Dr. Smith: Meeting starts now.
[10:15] Dr. Jones: Let me present the enrollment data.
[10:30] Coordinator: We should discuss retention strategies.
[10:45] Dr. Brown: Any questions about the safety data?
[11:00] Dr. Smith: Let's wrap up with action items.
        """
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    # Should have meeting statistics
    assert "meeting_statistics" in result
    assert "estimated_duration_minutes" in result["meeting_statistics"]["transcript_length"]


def test_meeting_summarizer_key_topics():
    """Test key topics identification."""
    input_data = {
        "transcript": """
PI: Today we'll discuss enrollment, safety, and data quality.
CRA: Enrollment is behind target at most sites.
Safety Monitor: We've had three serious adverse events reported.
Data Manager: Data quality issues are affecting 20% of records.
Biostatistician: The interim analysis is planned for next month.
        """,
        "meeting_type": "investigator"
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["key_topics"]) > 0
    
    # Check for expected topics
    topics = [topic["topic"].lower() for topic in result["key_topics"]]
    expected_topics = ["enrollment", "safety", "data"]
    assert any(expected in topic for topic in topics for expected in expected_topics)


def test_meeting_summarizer_meeting_effectiveness():
    """Test meeting effectiveness assessment."""
    input_data = {
        "transcript": """
Chair: Welcome to today's steering committee meeting.
Dr. A: Action item: I will review the budget by Friday.
Dr. B: Decision: We approve the protocol amendment.
Dr. C: We need to follow up on site activation.
Chair: Great, we covered all agenda items today.
        """,
        "attendees": [
            {"name": "Chair", "role": "Chair"},
            {"name": "Dr. A", "role": "Investigator"},
            {"name": "Dr. B", "role": "Sponsor"},
            {"name": "Dr. C", "role": "CRO"}
        ]
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "meeting_effectiveness" in result
    effectiveness = result["meeting_effectiveness"]
    
    assert "effectiveness_score" in effectiveness
    assert "overall_assessment" in effectiveness
    assert effectiveness["effectiveness_score"] > 0


def test_meeting_summarizer_timelines_and_deadlines():
    """Test timeline and deadline extraction."""
    input_data = {
        "transcript": """
PM: The database lock is scheduled for December 15th.
Statistician: Final analysis due by January 30, 2024.
Regulatory: Submission deadline is end of next quarter.
PI: Patient follow-up continues until March 2024.
        """
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert len(result["timelines_and_deadlines"]) > 0
    
    timelines = [item["timeline"] for item in result["timelines_and_deadlines"]]
    assert any("december" in timeline.lower() or "january" in timeline.lower() for timeline in timelines)


def test_meeting_summarizer_main_discussions():
    """Test main discussion threads extraction."""
    input_data = {
        "transcript": """
PI: Let's start with enrollment discussion.
Coordinator: Site 1 enrolled 5 patients, Site 2 enrolled 8 patients.
CRA: Site 3 is behind target with only 2 enrollments.
PI: Now let's move to safety review.
Safety Monitor: We have two new AEs to discuss.
Medical Monitor: Both events were assessed as unrelated to study drug.
PI: Finally, let's discuss data management issues.
        """
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    main_discussions = result["meeting_summary"]["main_discussions"]
    
    assert len(main_discussions) > 0
    # Should identify discussions about enrollment, safety, and data
    topics = [disc["topic"].lower() for disc in main_discussions]
    assert any("enrollment" in topic for topic in topics)


def test_meeting_summarizer_next_steps_generation():
    """Test next steps generation."""
    input_data = {
        "transcript": """
Chair: We have several action items from today.
Dr. A: I'll complete the safety review by next Friday.
Dr. B: Protocol update will be done in two weeks.
Coordinator: Need to schedule follow-up meeting.
Chair: We also decided to increase monitoring frequency.
        """
    }
    
    result = run(input_data)
    
    assert result["success"] == True
    assert "next_steps" in result
    assert len(result["next_steps"]) > 0
    
    # Next steps should be related to action items and decisions
    next_steps = result["next_steps"]
    assert any("action" in step.lower() for step in next_steps)