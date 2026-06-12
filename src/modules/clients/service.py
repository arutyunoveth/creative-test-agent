from src.shared.db.repository import db_session, json_dumps, json_loads

from .models import Client
from .schemas import ClientResponse, CreateClientRequest


def create_client(req: CreateClientRequest) -> ClientResponse:
    with db_session() as db:
        client = Client(
            name=req.name,
            industry=req.industry,
            description=req.description,
            contact_name=req.contact_name,
            contact_email=req.contact_email,
        )
        db.add(client)
        db.flush()
        db.refresh(client)
        return _to_response(client)


def list_clients() -> list[ClientResponse]:
    with db_session() as db:
        clients = db.query(Client).order_by(Client.created_at.desc()).all()
        return [_to_response(c) for c in clients]


def get_client(client_id: str) -> ClientResponse | None:
    with db_session() as db:
        client = db.query(Client).filter(Client.id == client_id).first()
        return _to_response(client) if client else None


def _to_response(client: Client) -> ClientResponse:
    return ClientResponse(
        id=client.id,
        name=client.name,
        industry=client.industry,
        description=client.description,
        contact_name=client.contact_name,
        contact_email=client.contact_email,
        metadata=json_loads(client.metadata_json),
        created_at=client.created_at,
        updated_at=client.updated_at,
    )
