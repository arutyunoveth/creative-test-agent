from pydantic import BaseModel


class AgentRole(BaseModel):
    name: str
    description: str


class RegisterAgentRequest(BaseModel):
    name: str
    description: str
