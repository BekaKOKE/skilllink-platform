from sqlalchemy.orm import Session
from backend.app.db.models.order import Order
from backend.app.services.event_service import EventService
from backend.app.services.h3_service import H3Service
from backend.app.db.models.enums import OrderStatus


class OrderService:

    @staticmethod
    def create_order(db: Session, client_id, data):
        h3_index = None

        if data.lat and data.lon:
            h3_index = H3Service.geo_to_h3(data.lat, data.lon)

        order = Order(
            client_id=client_id,
            specialist_id=data.specialist_id,
            service_type=data.service_type,
            lat=data.lat,
            lon=data.lon,
            h3_index=h3_index,
            price=data.price,
            description=data.description,
            status=OrderStatus.pending
        )

        db.add(order)
        db.commit()
        EventService.publish_event(
            db,
            event_type="ORDER_CREATED",
            payload={
                "order_id": str(order.id),
                "h3_index": order.h3_index,
                "price": order.price
            }
        )
        db.refresh(order)

        return order