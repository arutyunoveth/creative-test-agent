from fastapi import APIRouter

from src.modules.agent_registry.schemas import AgentRole, RegisterAgentRequest
from src.modules.agent_registry.service import list_agents, register_agent

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("", response_model=list[AgentRole])
def get_agents():
    return list_agents()


@router.post("/register", response_model=AgentRole)
def post_register_agent(body: RegisterAgentRequest):
    return register_agent(body)
