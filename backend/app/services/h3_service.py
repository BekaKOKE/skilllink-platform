import h3
from typing import List

DEFAULT_RESOLUTION = 7


def _geo_to_h3(lat: float, lon: float, resolution: int) -> str:
    """Совместимость с h3 v3 и v4."""
    if hasattr(h3, "latlng_to_cell"):
        # h3 v4+
        return h3.latlng_to_cell(lat, lon, resolution)
    else:
        # h3 v3
        return h3.geo_to_h3(lat, lon, resolution)


def _k_ring(h3_index: str, k: int) -> List[str]:
    """Совместимость с h3 v3 и v4."""
    if hasattr(h3, "grid_disk"):
        # h3 v4+
        return list(h3.grid_disk(h3_index, k))
    else:
        # h3 v3
        return list(h3.k_ring(h3_index, k))


def _h3_is_valid(h3_index: str) -> bool:
    """Совместимость с h3 v3 и v4."""
    if hasattr(h3, "is_valid_cell"):
        # h3 v4+
        return h3.is_valid_cell(h3_index)
    else:
        # h3 v3
        return h3.h3_is_valid(h3_index)


class H3Service:

    @staticmethod
    def geo_to_h3(lat: float, lon: float, resolution: int = DEFAULT_RESOLUTION) -> str:
        """Конвертировать lat/lon в H3 индекс."""
        return _geo_to_h3(lat, lon, resolution)

    @staticmethod
    def get_neighbors(h3_index: str, k: int = 1) -> List[str]:
        """Получить k-ring соседей (включая центральную ячейку)."""
        return _k_ring(h3_index, k)

    @staticmethod
    def validate_h3(h3_index: str) -> bool:
        """Проверить валидность H3 индекса."""
        return _h3_is_valid(h3_index)