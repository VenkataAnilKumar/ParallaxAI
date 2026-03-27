"""Tests for the search service."""

from unittest.mock import MagicMock, patch

from app.services.search import (
    SearchResult,
    format_results_for_prompt,
    web_search,
)


def test_format_results_empty():
    result = format_results_for_prompt([])
    assert "No web search results" in result


def test_format_results_with_data():
    results = [
        SearchResult(
            title="AI Market Report 2025",
            url="https://example.com/report",
            content="The AI market is expected to reach $500B by 2030.",
            score=0.95,
            published_date="2025-01-15",
        )
    ]
    formatted = format_results_for_prompt(results)
    assert "AI Market Report 2025" in formatted
    assert "https://example.com/report" in formatted
    assert "$500B" in formatted
    assert "2025-01-15" in formatted


@patch("app.services.search.settings")
def test_web_search_skips_without_api_key(mock_settings):
    mock_settings.TAVILY_API_KEY = ""
    mock_settings.EXA_API_KEY = ""
    results = web_search("AI market size 2025")
    assert results == []


@patch("app.services.search.TavilyClient")
@patch("app.services.search.settings")
def test_web_search_tavily_success(mock_settings, mock_tavily_class):
    mock_settings.TAVILY_API_KEY = "tvly-test-key"
    mock_settings.EXA_API_KEY = ""
    mock_client = MagicMock()
    mock_client.search.return_value = {
        "results": [
            {
                "title": "Test Result",
                "url": "https://example.com",
                "content": "Test content about AI market",
                "score": 0.9,
                "published_date": "2025-01-01",
            }
        ]
    }
    mock_tavily_class.return_value = mock_client

    results = web_search("AI market size")
    assert len(results) == 1
    assert results[0].title == "Test Result"
    assert results[0].url == "https://example.com"
    assert results[0].score == 0.9


@patch("app.services.search.search_tavily")
@patch("app.services.search.settings")
def test_web_search_falls_back_to_exa(mock_settings, mock_tavily):
    mock_settings.TAVILY_API_KEY = "key"
    mock_settings.EXA_API_KEY = "exa-key"
    mock_tavily.return_value = []  # Tavily returns nothing

    with patch("app.services.search.search_exa") as mock_exa:
        mock_exa.return_value = [
            SearchResult(title="Exa Result", url="https://exa.com", content="content")
        ]
        results = web_search("query")
        assert len(results) == 1
        assert results[0].title == "Exa Result"
