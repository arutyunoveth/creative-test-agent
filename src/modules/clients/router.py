from fastapi import APIRouter, HTTPException

from src.modules.audit_log.service import write_audit_event

from .schemas import ClientResponse, CreateClientRequest
from .service import create_client, get_client, list_clients

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("", response_model=ClientResponse, status_code=201)
def post_create_client(body: CreateClientRequest):
    client = create_client(body)
    write_audit_event("client_created", "client", client.id, {"name": client.name})
    return client


@router.get("", response_model=list[ClientResponse])
def get_clients():
    return list_clients()


@router.get("/{client_id}", response_model=ClientResponse)
def get_client_by_id(client_id: str):
    client = get_client(client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return client
