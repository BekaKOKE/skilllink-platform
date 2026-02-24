from sqlalchemy.orm import Session
from backend.app.db.models.specialist import Specialist
from backend.app.services.h3_service import H3Service


class SearchService:

    @staticmethod
    def find_specialists_nearby(
        db: Session,
        lat: float,
        lon: float,
        k_ring: int = 1
    ):
        center_cell = H3Service.geo_to_h3(lat, lon)
        neighbor_cells = H3Service.get_neighbors(center_cell, k_ring)

        return (
            db.query(Specialist)
            .filter(Specialist.h3_index.in_(neighbor_cells))
            .filter(Specialist.is_verified == True)
            .all()
        )