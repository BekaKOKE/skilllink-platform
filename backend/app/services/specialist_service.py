from sqlalchemy.orm import Session
from backend.app.db.models.specialist import Specialist
from backend.app.services.h3_service import H3Service


class SpecialistService:

    @staticmethod
    def create_specialist(db: Session, user_id, data):
        h3_index = H3Service.geo_to_h3(data.lat, data.lon)

        specialist = Specialist(
            user_id=user_id,
            full_name=data.full_name,
            category=data.category,
            lat=data.lat,
            lon=data.lon,
            h3_index=h3_index,
            h3_resolution=7,
            license_number=data.license_number
        )

        db.add(specialist)
        db.commit()
        db.refresh(specialist)

        return specialist