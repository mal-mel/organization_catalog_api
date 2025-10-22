from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import verify_api_key
from app.crud import activity as crud_activity
from app.schemas.activity import ActivityTree, ActivityDetail, ActivityCreate, ActivityUpdate, ActivitySimple

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/", response_model=List[ActivityTree])
def get_activities_tree(
        db: Session = Depends(get_db),
        max_depth: int = Query(3, ge=1, le=3, description="Максимальная глубина вложенности (1-3)")
):
    """
    Получить дерево видов деятельности с ограничением вложенности
    """

    def build_tree_with_depth(activity, current_depth=0):
        if current_depth >= max_depth:
            return ActivityTree(
                id=activity.id,
                name=activity.name,
                parent_id=activity.parent_id,
                children=[]
            )

        children = [
            build_tree_with_depth(child, current_depth + 1)
            for child in activity.children
        ]

        return ActivityTree(
            id=activity.id,
            name=activity.name,
            parent_id=activity.parent_id,
            children=children
        )

    root_activities = crud_activity.activity.get_tree(db)
    return [build_tree_with_depth(activity) for activity in root_activities]


@router.get("/{activity_id}", response_model=ActivityDetail)
def get_activity(
        activity_id: int,
        db: Session = Depends(get_db)
):
    """Получить информацию о виде деятельности по ID"""
    activity = crud_activity.activity.get_with_children(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Подсчет организаций для этой активности
    organizations_count = len(activity.organizations) if activity.organizations else 0

    return ActivityDetail(
        id=activity.id,
        name=activity.name,
        parent_id=activity.parent_id,
        children=[ActivitySimple(id=child.id, name=child.name) for child in activity.children],
        organizations_count=organizations_count
    )


@router.post("/", response_model=ActivityDetail)
def create_activity(
        activity_in: ActivityCreate,
        db: Session = Depends(get_db)
):
    """Создать новый вид деятельности"""
    activity = crud_activity.activity.create_with_validation(db, obj_in=activity_in)
    return ActivityDetail(
        id=activity.id,
        name=activity.name,
        parent_id=activity.parent_id,
        children=[],
        organizations_count=0
    )


@router.put("/{activity_id}", response_model=ActivityDetail)
def update_activity(
        activity_id: int,
        activity_in: ActivityUpdate,
        db: Session = Depends(get_db)
):
    """Обновить вид деятельности"""
    activity = crud_activity.activity.get(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    updated_activity = crud_activity.activity.update_with_validation(
        db, db_obj=activity, obj_in=activity_in
    )

    return ActivityDetail(
        id=updated_activity.id,
        name=updated_activity.name,
        parent_id=updated_activity.parent_id,
        children=[ActivitySimple(id=child.id, name=child.name) for child in updated_activity.children],
        organizations_count=len(updated_activity.organizations) if updated_activity.organizations else 0
    )


@router.delete("/{activity_id}", status_code=204)
def delete_activity(
        activity_id: int,
        db: Session = Depends(get_db)
):
    """Удалить вид деятельности"""
    activity = crud_activity.activity.get(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Проверяем, что у активности нет потомков
    if activity.children:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete activity that has children. Delete children first."
        )

    # Проверяем, что активность не используется организациями
    if activity.organizations:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete activity that is used by organizations. Remove associations first."
        )

    crud_activity.activity.remove(db, id=activity_id)
    return None