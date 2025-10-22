from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.organization import Organization
from app.models.phone_number import PhoneNumber
from app.models.activity import Activity
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.crud.base import CRUDBase


class CRUDOrganization(CRUDBase[Organization, OrganizationCreate, OrganizationUpdate]):
    def get_multi_with_details(
            self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Organization]:
        return db.query(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.phone_numbers),
            joinedload(Organization.activities)
        ).offset(skip).limit(limit).all()

    def get_with_details(self, db: Session, id: int) -> Optional[Organization]:
        return db.query(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.phone_numbers),
            joinedload(Organization.activities)
        ).filter(Organization.id == id).first()

    def get_by_building(self, db: Session, building_id: int) -> List[Organization]:
        return db.query(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.phone_numbers),
            joinedload(Organization.activities)
        ).filter(Organization.building_id == building_id).all()

    def get_by_activity(self, db: Session, activity_id: int) -> List[Organization]:
        return db.query(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.phone_numbers),
            joinedload(Organization.activities)
        ).filter(Organization.activities.any(id=activity_id)).all()

    def search_by_name(self, db: Session, name: str) -> List[Organization]:
        return db.query(Organization).options(
            joinedload(Organization.building),
            joinedload(Organization.phone_numbers)
        ).filter(Organization.name.ilike(f"%{name}%")).all()

    def create_with_phones_and_activities(
            self, db: Session, *, obj_in: OrganizationCreate
    ) -> Organization:
        org_data = obj_in.model_dump(exclude={"phone_numbers", "activity_ids"})
        db_obj = Organization(**org_data)
        db.add(db_obj)
        db.flush()

        for phone_data in obj_in.phone_numbers:
            phone = PhoneNumber(**phone_data.model_dump(), organization_id=db_obj.id)
            db.add(phone)

        if obj_in.activity_ids:
            activities = db.query(Activity).filter(Activity.id.in_(obj_in.activity_ids)).all()
            db_obj.activities.extend(activities)

        db.commit()
        db.refresh(db_obj)
        return db_obj


organization = CRUDOrganization(Organization)