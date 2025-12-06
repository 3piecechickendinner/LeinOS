"""Agent implementations using Google Agent Development Kit."""

# Export the root agent and app for ADK to find
from agents.agent import root_agent, app

# Needed for manual imports in main.py
from agents.probate_tracker.agent import ProbateTrackerAgent
from agents.mineral_tracker.agent import MineralTrackerAgent
from agents.surplus_tracker.agent import SurplusTrackerAgent

__all__ = ["root_agent", "app", "ProbateTrackerAgent", "MineralTrackerAgent", "SurplusTrackerAgent"]
