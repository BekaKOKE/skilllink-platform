import uuid
from typing import Any

from backend.app.db.models import Order, OrderStatus, Specialist
from backend.app.exceptions.ValidationException import ValidationException

class OrderValidation:

    @staticmethod
    def update_validation(order: Order, update_data:dict[str, Any]) -> None:
        errors = []
        if order.status != OrderStatus.open:
            errors.append("Cannot update order that is already in progress or completed")
        if not update_data:
            errors.append("No fields to update")
        if errors:
            raise ValidationException(errors)

    @staticmethod
    def deactivate_validation(order: Order) -> None:
        errors = []
        if order.status == OrderStatus.in_progress:
            errors.append("Cannot deactivate order that is in progress")

        if errors:
            raise ValidationException(errors)

    @staticmethod
    def delete_validation(order: Order) -> None:
        errors = []
        if order.status == OrderStatus.in_progress:
            errors.append("Cannot delete order that is in progress")

        if errors:
            raise ValidationException(errors)

    @staticmethod
    def take_validation(order: Order, specialist: Specialist, specialist_order: Order) -> None:
        errors = []

        if specialist_order is not None:
            errors.append("Specialist has already taken order")
        if order.status != OrderStatus.open:
            errors.append("Order is no longer available")
        if not order.is_active:
            errors.append("Order is not active")

        if not specialist:
            errors.append("Specialist not found")
            raise ValidationException(errors)

        if not specialist.is_verified:
            errors.append("Only verified specialists can take orders")
        if not specialist.is_active:
            errors.append("Specialist profile is not active")

        if errors:
            raise ValidationException(errors)

    @staticmethod
    def complete_validation(order: Order, user_id: uuid.UUID) -> None:
        errors = []

        if order.user_id != user_id:
            errors.append("Only the client can complete the order")
        if order.status != OrderStatus.in_progress:
            errors.append("Order is not in progress")

        if errors:
            raise ValidationException(errors)

    @staticmethod
    def cancel_validation(order: Order, user_id: uuid.UUID) -> None:
        errors = []

        if order.user_id != user_id:
            errors.append("Only the client can cancel the order")
        if order.status in (OrderStatus.completed, OrderStatus.cancelled):
            errors.append("Cannot cancel a completed or already cancelled order")

        if errors:
            raise ValidationException(errors)