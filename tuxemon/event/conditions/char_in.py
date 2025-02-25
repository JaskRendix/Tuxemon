# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging

from tuxemon.db import SurfaceKeys
from tuxemon.event import MapCondition, get_npc
from tuxemon.event.eventcondition import EventCondition
from tuxemon.session import Session
from tuxemon.states.world.worldstate import WorldState

logger = logging.getLogger(__name__)


from dataclasses import dataclass


@dataclass
class CharInCondition(EventCondition):
    """
    Check to see if the character is on a specific set of tiles.

    Script usage:
        .. code-block::

            is char_in <character>,<value>

    Script parameters:
        character: Either "player" or character slug name (e.g. "npc_maple")
        value: value (eg surfable) inside the tileset.

    """

    name = "char_in"
    character: str
    value: str

    def test(self, session: Session, condition: MapCondition) -> bool:
        character = get_npc(session, self.character)
        if character is None:
            logger.error(f"{self.character} not found")
            return False
        world = session.client.get_state_by_name(WorldState)

        tiles = []
        if self.value in SurfaceKeys:
            tiles = world.get_all_tile_properties(
                world.surface_map, self.value
            )
        else:
            tiles = world.check_collision_zones(
                world.collision_map, self.value
            )
        if tiles:
            return character.tile_pos in tiles
        return False
