from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from urllib.parse import unquote

from app.core.database import get_db
from app.api.deps import verify_api_key
from app.crud import organization as crud_organization
from app.crud import activity as crud_activity
from app.crud import building as crud_building
from app.schemas.organization import OrganizationSimple, OrganizationDetail, OrganizationCreate, OrganizationUpdate

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/", response_model=List[OrganizationSimple])
def get_organizations(
        db: Session = Depends(get_db),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        activity_id: Optional[int] = Query(None, description="Фильтр по виду деятельности (включая дочерние)"),
        name: Optional[str] = Query(None, description="Поиск по названию организации"),
        in_area: Optional[str] = Query(None,
                                       description="Поиск по области: circle:lat,lon,radius или rect:min_lat,min_lon,max_lat,max_lon")
):
    """Поиск и фильтрация организаций"""

    organizations = []

    if activity_id is not None:
        descendant_ids = crud_activity.activity.get_all_descendants(db, activity_id)
        if not descendant_ids:
            return []

        seen_orgs = set()
        for act_id in descendant_ids:
            orgs = crud_organization.organization.get_by_activity(db, act_id)
            for org in orgs:
                if org.id not in seen_orgs:
                    seen_orgs.add(org.id)
                    organizations.append(org)

    elif name is not None:
        organizations = crud_organization.organization.search_by_name(db, unquote(name))

    elif in_area is not None:
        if in_area.startswith('circle:'):
            try:
                _, params = in_area.split(':', 1)
                lat, lon, radius = map(float, params.split(','))

                buildings_with_distance = crud_building.building.get_in_radius(
                    db, lat=lat, lon=lon, radius_m=radius
                )
                building_ids = [b.id for b, _ in buildings_with_distance]

                seen_orgs = set()
                for building_id in building_ids:
                    orgs = crud_organization.organization.get_by_building(db, building_id)
                    for org in orgs:
                        if org.id not in seen_orgs:
                            seen_orgs.add(org.id)
                            organizations.append(org)

            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid circle format. Use: circle:lat,lon,radius")

        elif in_area.startswith('rect:'):
            try:
                _, params = in_area.split(':', 1)
                min_lat, min_lon, max_lat, max_lon = map(float, params.split(','))

                buildings = crud_building.building.get_in_rectangle(
                    db, min_lat=min_lat, max_lat=max_lat, min_lon=min_lon, max_lon=max_lon
                )
                building_ids = [b.id for b in buildings]

                seen_orgs = set()
                for building_id in building_ids:
                    orgs = crud_organization.organization.get_by_building(db, building_id)
                    for org in orgs:
                        if org.id not in seen_orgs:
                            seen_orgs.add(org.id)
                            organizations.append(org)

            except ValueError:
                raise HTTPException(status_code=400,
                                    detail="Invalid rectangle format. Use: rect:min_lat,min_lon,max_lat,max_lon")
        else:
            raise HTTPException(status_code=400, detail="Invalid area format. Use 'circle:' or 'rect:'")

    else:
        return crud_organization.organization.get_multi_with_details(db, skip=skip, limit=limit)

    if skip > 0 or limit < len(organizations):
        organizations = organizations[skip:skip + limit]

    return organizations


@router.get("/{organization_id}", response_model=OrganizationDetail)
def get_organization(
        organization_id: int,
        db: Session = Depends(get_db)
):
    """Получить информацию об организации по ID"""
    organization = crud_organization.organization.get_with_details(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.post("/", response_model=OrganizationDetail, status_code=201)
def create_organization(
        organization_in: OrganizationCreate,
        db: Session = Depends(get_db)
):
    """Создать новую организацию"""
    # Проверяем существование здания
    building = crud_building.building.get(db, organization_in.building_id)
    if not building:
        raise HTTPException(status_code=400, detail="Building not found")

    organization = crud_organization.organization.create_with_phones_and_activities(
        db, obj_in=organization_in
    )
    return crud_organization.organization.get_with_details(db, organization.id)


@router.put("/{organization_id}", response_model=OrganizationDetail)
def update_organization(
        organization_id: int,
        organization_in: OrganizationUpdate,
        db: Session = Depends(get_db)
):
    """Обновить организацию"""
    organization = crud_organization.organization.get(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Если меняется building_id, проверяем существование здания
    if organization_in.building_id is not None:
        building = crud_building.building.get(db, organization_in.building_id)
        if not building:
            raise HTTPException(status_code=400, detail="Building not found")

    updated_org = crud_organization.organization.update(db, db_obj=organization, obj_in=organization_in)
    return crud_organization.organization.get_with_details(db, updated_org.id)


@router.delete("/{organization_id}", status_code=204)
def delete_organization(
        organization_id: int,
        db: Session = Depends(get_db)
):
    """Удалить организацию"""
    organization = crud_organization.organization.get(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    crud_organization.organization.remove(db, id=organization_id)
    return None