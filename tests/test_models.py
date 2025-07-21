"""Test suite for Pydantic models and validation."""

import pytest
from datetime import datetime
from typing import List

from agents.models import (
    SearchResult,
    ResearchSummary, 
    EmailDraft,
    SearchQuery
)


class TestSearchResult:
    """Test SearchResult model validation."""
    
    def test_valid_search_result(self):
        """Test creation of valid search result."""
        
        result = SearchResult(
            title="AI Agents Guide",
            url="https://example.com/guide",
            description="Comprehensive guide to AI agents",
            score=0.95
        )
        
        assert result.title == "AI Agents Guide"
        assert result.url == "https://example.com/guide"
        assert result.description == "Comprehensive guide to AI agents"
        assert result.score == 0.95
    
    def test_search_result_without_score(self):
        """Test search result without score (optional field)."""
        
        result = SearchResult(
            title="Test Title",
            url="https://example.com",
            description="Test description"
        )
        
        assert result.score is None
    
    def test_search_result_serialization(self):
        """Test JSON serialization of search result."""
        
        result = SearchResult(
            title="Test",
            url="https://example.com",
            description="Description",
            score=0.8
        )
        
        json_data = result.model_dump()
        
        assert json_data["title"] == "Test"
        assert json_data["url"] == "https://example.com"
        assert json_data["score"] == 0.8


class TestResearchSummary:
    """Test ResearchSummary model validation."""
    
    def test_valid_research_summary(self):
        """Test creation of valid research summary."""
        
        results = [
            SearchResult(
                title="AI Guide",
                url="https://example.com",
                description="AI information"
            )
        ]
        
        summary = ResearchSummary(
            query="AI agents",
            results=results,
            summary="This is a research summary",
            key_insights=["Insight 1", "Insight 2"]
        )
        
        assert summary.query == "AI agents"
        assert len(summary.results) == 1
        assert summary.summary == "This is a research summary"
        assert len(summary.key_insights) == 2
        assert isinstance(summary.timestamp, datetime)
    
    def test_research_summary_automatic_timestamp(self):
        """Test that timestamp is automatically set."""
        
        before = datetime.now()
        
        summary = ResearchSummary(
            query="test",
            results=[],
            summary="test summary",
            key_insights=[]
        )
        
        after = datetime.now()
        
        assert before <= summary.timestamp <= after
    
    def test_research_summary_with_empty_lists(self):
        """Test research summary with empty results and insights."""
        
        summary = ResearchSummary(
            query="empty test",
            results=[],
            summary="No results found",
            key_insights=[]
        )
        
        assert len(summary.results) == 0
        assert len(summary.key_insights) == 0


class TestEmailDraft:
    """Test EmailDraft model validation."""
    
    def test_valid_email_draft(self):
        """Test creation of valid email draft."""
        
        draft = EmailDraft(
            to=["recipient@example.com"],
            subject="Test Subject",
            body="This is the email body",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"]
        )
        
        assert draft.to == ["recipient@example.com"]
        assert draft.subject == "Test Subject"
        assert draft.body == "This is the email body"
        assert draft.cc == ["cc@example.com"]
        assert draft.bcc == ["bcc@example.com"]
    
    def test_email_draft_required_fields_only(self):
        """Test email draft with only required fields."""
        
        draft = EmailDraft(
            to=["recipient@example.com"],
            subject="Test Subject",
            body="Email body"
        )
        
        assert draft.to == ["recipient@example.com"]
        assert draft.cc is None
        assert draft.bcc is None
    
    def test_email_validation(self):
        """Test email address validation."""
        
        # Valid emails should work
        draft = EmailDraft(
            to=["test@example.com", "user@domain.org"],
            subject="Test",
            body="Body"
        )
        
        assert len(draft.to) == 2
    
    def test_empty_recipients_validation(self):
        """Test that empty recipients list is handled."""
        
        with pytest.raises(ValueError):
            EmailDraft(
                to=[],  # Empty list should fail
                subject="Test",
                body="Body"
            )

class TestSearchQuery:
    """Test SearchQuery model validation."""
    
    def test_valid_search_query(self):
        """Test creation of valid search query."""
        
        query = SearchQuery(
            query="AI agents research",
            max_results=15
        )
        
        assert query.query == "AI agents research"
        assert query.max_results == 15
    
    def test_search_query_default_max_results(self):
        """Test search query with default max_results."""
        
        query = SearchQuery(query="test query")
        
        assert query.max_results == 10  # Default value
    
    def test_search_query_validation_min_length(self):
        """Test query minimum length validation."""
        
        with pytest.raises(ValueError):
            SearchQuery(query="")  # Empty query should fail
    
    def test_search_query_validation_max_length(self):
        """Test query maximum length validation."""
        
        long_query = "a" * 501  # Exceeds 500 character limit
        
        with pytest.raises(ValueError):
            SearchQuery(query=long_query)
    
    def test_search_query_max_results_validation(self):
        """Test max_results validation."""
        
        # Test minimum bound
        with pytest.raises(ValueError):
            SearchQuery(query="test", max_results=0)
        
        # Test maximum bound
        with pytest.raises(ValueError):
            SearchQuery(query="test", max_results=51)
        
        # Test valid range
        query = SearchQuery(query="test", max_results=25)
        assert query.max_results == 25


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_search_result_round_trip(self):
        """Test SearchResult serialization round trip."""
        
        original = SearchResult(
            title="Test Title",
            url="https://example.com",
            description="Test description",
            score=0.85
        )
        
        # Serialize to dict
        data = original.model_dump()
        
        # Deserialize back
        restored = SearchResult(**data)
        
        assert restored.title == original.title
        assert restored.url == original.url
        assert restored.description == original.description
        assert restored.score == original.score
    
    def test_email_draft_round_trip(self):
        """Test EmailDraft serialization round trip."""
        
        original = EmailDraft(
            to=["test@example.com"],
            subject="Test Subject",
            body="Test body",
            cc=["cc@example.com"]
        )
        
        # Serialize to dict
        data = original.model_dump()
        
        # Deserialize back
        restored = EmailDraft(**data)
        
        assert restored.to == original.to
        assert restored.subject == original.subject
        assert restored.body == original.body
        assert restored.cc == original.cc
    
    def test_research_summary_json_serialization(self):
        """Test ResearchSummary JSON serialization."""
        
        results = [
            SearchResult(title="Test", url="https://example.com", description="Desc")
        ]
        
        summary = ResearchSummary(
            query="test query",
            results=results,
            summary="test summary",
            key_insights=["insight"]
        )
        
        # Convert to JSON string
        json_str = summary.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "test query" in json_str
        assert "https://example.com" in json_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])