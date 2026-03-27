from app.agents.research.market import MarketAgent
from app.agents.research.competitor import CompetitorAgent
from app.agents.research.regulatory import RegulatoryAgent
from app.agents.research.news import NewsAgent
from app.agents.research.financial import FinancialAgent
from app.agents.research.sentiment import SentimentAgent
from app.agents.research.academic import AcademicAgent

ALL_AGENTS = {
    "market": MarketAgent,
    "competitor": CompetitorAgent,
    "regulatory": RegulatoryAgent,
    "news": NewsAgent,
    "financial": FinancialAgent,
    "sentiment": SentimentAgent,
    "academic": AcademicAgent,
}

__all__ = [
    "MarketAgent",
    "CompetitorAgent",
    "RegulatoryAgent",
    "NewsAgent",
    "FinancialAgent",
    "SentimentAgent",
    "AcademicAgent",
    "ALL_AGENTS",
]
