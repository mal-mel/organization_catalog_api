from typing import List, Tuple
from sqlalchemy.orm import Session
from math import radians, cos, sin, sqrt, atan2
from app.models.building import Building
from app.schemas.building import BuildingCreate, BuildingUpdate
from app.crud.base import CRUDBase


class CRUDBuilding(CRUDBase[Building, BuildingCreate, BuildingUpdate]):
    def get_by_address(self, db: Session, address: str) -> Building:
        return db.query(Building).filter(Building.address == address).first()

    def get_in_radius(
            self, db: Session, *, lat: float, lon: float, radius_m: float
    ) -> List[Tuple[Building, float]]:
        """
        Получить здания в радиусе с расчетом расстояния
        Используем формулу гаверсинуса
        """
        buildings_with_distance = []

        for building in db.query(Building).all():
            R = 6371000

            lat1 = radians(lat)
            lon1 = radians(lon)
            lat2 = radians(building.latitude)
            lon2 = radians(building.longitude)

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = R * c

            if distance <= radius_m:
                buildings_with_distance.append((building, distance))

        return buildings_with_distance

    def get_in_rectangle(
            self, db: Session, *, min_lat: float, max_lat: float, min_lon: float, max_lon: float
    ) -> List[Building]:
        """Получить здания в прямоугольной области"""
        return db.query(Building).filter(
            Building.latitude.between(min_lat, max_lat),
            Building.longitude.between(min_lon, max_lon)
        ).all()


building = CRUDBuilding(Building)