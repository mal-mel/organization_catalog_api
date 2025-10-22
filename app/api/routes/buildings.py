from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.api.deps import verify_api_key
from app.crud import building as crud_building
from app.crud import organization as crud_organization
from app.schemas.building import BuildingSimple, BuildingWithDistance, BuildingDetail
from app.schemas.organization import OrganizationSimple

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/", response_model=List[BuildingSimple])
def get_buildings(
        db: Session = Depends(get_db),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
):
    """Получить список всех зданий"""
    return crud_building.building.get_multi(db, skip=skip, limit=limit)


@router.get("/nearby", response_model=List[BuildingWithDistance])
def get_nearby_buildings(
        db: Session = Depends(get_db),
        # Вариант для радиуса
        lat: Optional[float] = Query(None, description="Широта центра"),
        lon: Optional[float] = Query(None, description="Долгота центра"),
        radius: Optional[float] = Query(None, ge=1, description="Радиус в метрах"),
        # Вариант для прямоугольника
        min_lat: Optional[float] = Query(None, description="Нижняя граница широты"),
        max_lat: Optional[float] = Query(None, description="Верхняя граница широты"),
        min_lon: Optional[float] = Query(None, description="Левая граница долготы"),
        max_lon: Optional[float] = Query(None, description="Правая граница долготы"),
):
    """Получить здания в заданной области"""
    buildings = []

    if lat is not None and lon is not None and radius is not None:
        # Поиск по радиусу
        buildings_with_distance = crud_building.building.get_in_radius(
            db, lat=lat, lon=lon, radius_m=radius
        )
        buildings = [
            BuildingWithDistance(
                id=building.id,
                address=building.address,
                latitude=building.latitude,
                longitude=building.longitude,
                distance=distance
            )
            for building, distance in buildings_with_distance
        ]
    elif all([min_lat, max_lat, min_lon, max_lon]):
        # Поиск по прямоугольнику
        buildings_list = crud_building.building.get_in_rectangle(
            db, min_lat=min_lat, max_lat=max_lat, min_lon=min_lon, max_lon=max_lon
        )
        buildings = [
            BuildingWithDistance(
                id=building.id,
                address=building.address,
                latitude=building.latitude,
                longitude=building.longitude,
                distance=None
            )
            for building in buildings_list
        ]
    else:
        raise HTTPException(
            status_code=400,
            detail="Either provide (lat, lon, radius) for circle search or (min_lat, max_lat, min_lon, max_lon) for rectangle search"
        )

    return buildings


@router.get("/{building_id}", response_model=BuildingDetail)
def get_building(
        building_id: int,
        db: Session = Depends(get_db)
):
    """Получить информацию о здании по ID"""
    building = crud_building.building.get(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    organizations = crud_organization.organization.get_by_building(db, building_id)

    return BuildingDetail(
        id=building.id,
        address=building.address,
        latitude=building.latitude,
        longitude=building.longitude,
        organizations=organizations
    )


@router.get("/{building_id}/organizations", response_model=List[OrganizationSimple])
def get_building_organizations(
        building_id: int,
        db: Session = Depends(get_db)
):
    """Получить организации в конкретном здании"""
    # Проверяем существование здания
    building = crud_building.building.get(db, building_id)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    return crud_organization.organization.get_by_building(db, building_id)