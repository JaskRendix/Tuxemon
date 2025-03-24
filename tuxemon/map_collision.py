# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Mapping, MutableMapping
from typing import TYPE_CHECKING, DefaultDict, Optional, Union

from tuxemon.map import RegionProperties

if TYPE_CHECKING:
    from tuxemon.npc import NPC
    from tuxemon.states.world.worldstate import WorldState

logger = logging.getLogger(__name__)

CollisionDict = dict[
    tuple[int, int],
    Optional[RegionProperties],
]

CollisionMap = Mapping[
    tuple[int, int],
    Optional[RegionProperties],
]


class CollisionManager:
    def __init__(self, world_state: WorldState):
        self.world_state = world_state

    def get_collision_map(self) -> CollisionMap:
        """
        Return dictionary for collision testing.

        Returns a dictionary where keys are (x, y) tile tuples
        and the values are tiles or NPCs.

        # NOTE:
        This will not respect map changes to collisions
        after the map has been loaded!

        Returns:
            A dictionary of collision tiles.

        """
        collision_dict: DefaultDict[
            tuple[int, int], Optional[RegionProperties]
        ] = defaultdict(lambda: RegionProperties([], [], [], None, None))

        # Get all the NPCs' tile positions
        for npc in self.world_state.get_all_entities():
            collision_dict[npc.tile_pos] = self._create_collision_region(
                npc.tile_pos, npc
            )

        # Add surface map entries to the collision dictionary
        for coords, surface in self.world_state.surface_map.items():
            for label, value in surface.items():
                if float(value) == 0:
                    collision_dict[coords] = self._create_collision_region(
                        coords, label
                    )

        collision_dict.update(
            {k: v for k, v in self.world_state.collision_map.items()}
        )

        return dict(collision_dict)

    def check_collision_zones(
        self,
        collision_map: MutableMapping[
            tuple[int, int], Optional[RegionProperties]
        ],
        label: str,
    ) -> list[tuple[int, int]]:
        """
        Returns coordinates of specific collision zones.

        Parameters:
            collision_map: The collision map.
            label: The label to filter collision zones by.

        Returns:
            A list of coordinates of collision zones with the specific label.

        """
        return [
            coords
            for coords, props in collision_map.items()
            if props and props.key == label
        ]

    def _create_collision_region(
        self, coords: tuple[int, int], entity_or_label: Union[NPC, str]
    ) -> RegionProperties:
        region = self.world_state.collision_map.get(coords)
        if region:
            return RegionProperties(
                region.enter_from,
                region.exit_from,
                region.endure,
                (
                    entity_or_label
                    if not isinstance(entity_or_label, str)
                    else None
                ),
                (
                    entity_or_label
                    if isinstance(entity_or_label, str)
                    else region.key
                ),
            )
        else:
            return RegionProperties(
                [],
                [],
                [],
                (
                    entity_or_label
                    if not isinstance(entity_or_label, str)
                    else None
                ),
                entity_or_label if isinstance(entity_or_label, str) else None,
            )
