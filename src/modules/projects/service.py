from src.shared.db.repository import db_session, json_dumps, json_loads

from .models import Project
from .schemas import CreateProjectRequest, ProjectResponse


def create_project(req: CreateProjectRequest) -> ProjectResponse:
    with db_session() as db:
        project = Project(
            client_id=req.client_id,
            name=req.name,
            description=req.description,
            status=req.status,
        )
        db.add(project)
        db.flush()
        db.refresh(project)
        return _to_response(project)


def list_projects(client_id: str | None = None) -> list[ProjectResponse]:
    with db_session() as db:
        q = db.query(Project)
        if client_id:
            q = q.filter(Project.client_id == client_id)
        projects = q.order_by(Project.created_at.desc()).all()
        return [_to_response(p) for p in projects]


def get_project(project_id: str) -> ProjectResponse | None:
    with db_session() as db:
        project = db.query(Project).filter(Project.id == project_id).first()
        return _to_response(project) if project else None


def _to_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=project.id,
        client_id=project.client_id,
        name=project.name,
        description=project.description,
        status=project.status,
        metadata=json_loads(project.metadata_json),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )
