from dataclasses import dataclass
from game.terrain.terrain_type import TerrainType
from game.util.assert_blob_has_key_of_type import assert_blob_has_key_of_type
from game.util.position import Position


@dataclass
class Terrain:
    """
    Represents a piece of terrain
    """

    id: str
    position: Position
    health: int
    can_attack_through: bool
    type: TerrainType

    def deserialize(blob: object) -> "Terrain":
        try:
            assert_blob_has_key_of_type(blob, "id", str)
            assert_blob_has_key_of_type(blob, "position", dict)
            assert_blob_has_key_of_type(blob, "health", int)
            assert_blob_has_key_of_type(blob, "canAttackThrough", bool)
            assert_blob_has_key_of_type(blob, "type", str)
            assert any(
                blob["type"] == item.value for item in TerrainType
            ), "Invalid attack action type"
            terrain = Terrain(
                blob["id"],
                Position.deserialize(blob["position"]),
                blob["health"],
                blob["canAttackThrough"],
                TerrainType[blob["type"]],
            )
        except:
            print("Failed to validate Terrain json")
            raise

        return terrain
