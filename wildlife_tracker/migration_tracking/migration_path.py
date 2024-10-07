from typing import Optional
from wildlife_tracker.habitat_management.habitat import Habitat

class MigrationPath:

    def __init__(self,
                path_id: int,
                species: str,
                destination: Habitat,
                start_location: Habitat,
                duration: Optional[int] = None
                ) -> None:
        pass

    def update_migration_path_details(path_id: int, **kwargs) -> None:
        pass

    def get_migration_path_details(path_id) -> dict:
        pass

