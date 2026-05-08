"""Shared LegalAgent instance — imported by routers to avoid re-instantiation."""
from backend.services.legal_agent import LegalAgent

agent = LegalAgent()
