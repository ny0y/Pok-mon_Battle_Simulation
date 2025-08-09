from fastapi import HTTPException
from ai.rl_agent import QLearningAgent
from typing import Optional

# This will hold the global Q-learning agent instance after startup
agent_instance: Optional[QLearningAgent] = None

def get_agent() -> QLearningAgent:
    """
    Dependency to retrieve the global AI agent.
    Raises 500 if the agent is not yet loaded.
    """
    if agent_instance is None:
        raise HTTPException(status_code=500, detail="AI agent not loaded.")
    return agent_instance

