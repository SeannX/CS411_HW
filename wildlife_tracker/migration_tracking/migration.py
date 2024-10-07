from typing import Any, Optional

from wildlife_tracker.migration_tracking.migration_path import MigrationPath


class Migration:

    def __init__(self,
                start_date: str, 
                current_date: str,
                migration_path: MigrationPath,
                migration_id: int,
                status: str = "Scheduled") -> None:
        pass

    def get_migration_details(migration_id: int) -> dict[str, Any]:
        pass

    def update_migration_details(migration_id: int, **kwargs: Any) -> None:
        pass