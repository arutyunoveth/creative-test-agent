from src.modules.agent_registry.schemas import AgentRole, RegisterAgentRequest

_DEFAULT_ROLES = [
    AgentRole(
        name="creative_intake_agent",
        description="Ingests and classifies incoming creative materials.",
    ),
    AgentRole(
        name="audience_simulation_agent",
        description="Simulates synthetic audience responses.",
    ),
    AgentRole(
        name="brand_safety_agent",
        description="Checks creative against brand constraints and risks.",
    ),
    AgentRole(
        name="rubric_scoring_agent",
        description="Scores creative against a configured rubric.",
    ),
    AgentRole(
        name="report_agent",
        description="Generates structured reports from test findings.",
    ),
]

_registry: dict[str, AgentRole] = {r.name: r for r in _DEFAULT_ROLES}


def list_agents() -> list[AgentRole]:
    return list(_registry.values())


def register_agent(req: RegisterAgentRequest) -> AgentRole:
    role = AgentRole(name=req.name, description=req.description)
    _registry[role.name] = role
    return role
