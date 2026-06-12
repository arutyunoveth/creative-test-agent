from fastapi import APIRouter, HTTPException, Query

from src.modules.audit_log.service import write_audit_event

from .schemas import CreateProjectRequest, ProjectResponse
from .service import create_project, get_project, list_projects

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
def post_create_project(body: CreateProjectRequest):
    project = create_project(body)
    write_audit_event("project_created", "project", project.id, {"name": project.name})
    return project


@router.get("", response_model=list[ProjectResponse])
def get_projects(client_id: str | None = Query(None)):
    return list_projects(client_id=client_id)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project_by_id(project_id: str):
    project = get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
