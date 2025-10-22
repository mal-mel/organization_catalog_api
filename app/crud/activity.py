from typing import List, Set
from sqlalchemy.orm import Session, joinedload
from app.models.activity import Activity
from app.schemas.activity import ActivityCreate, ActivityUpdate
from app.crud.base import CRUDBase


class CRUDActivity(CRUDBase[Activity, ActivityCreate, ActivityUpdate]):
    def get_by_name(self, db: Session, name: str) -> Activity:
        return db.query(Activity).filter(Activity.name == name).first()

    def get_tree(self, db: Session) -> List[Activity]:
        return db.query(Activity).filter(Activity.parent_id.is_(None)).options(
            joinedload(Activity.children)
        ).all()

    def get_with_children(self, db: Session, activity_id: int) -> Activity:
        return db.query(Activity).filter(Activity.id == activity_id).options(
            joinedload(Activity.children)
        ).first()

    def get_all_descendants(self, db: Session, activity_id: int) -> Set[int]:
        """Получить всех потомков активности (включая саму активность)"""

        def get_children_ids(activity_id: int) -> Set[int]:
            activity = db.query(Activity).filter(Activity.id == activity_id).first()
            if not activity:
                return set()

            ids = {activity_id}
            for child in activity.children:
                ids.update(get_children_ids(child.id))
            return ids

        return get_children_ids(activity_id)

    def get_activity_depth(self, db: Session, activity_id: int) -> int:
        """Получить глубину активности в дереве"""

        def get_depth(activity_id: int, current_depth: int = 0) -> int:
            activity = db.query(Activity).filter(Activity.id == activity_id).first()
            if not activity or not activity.parent_id:
                return current_depth
            return get_depth(activity.parent_id, current_depth + 1)

        return get_depth(activity_id)


activity = CRUDActivity(Activity)