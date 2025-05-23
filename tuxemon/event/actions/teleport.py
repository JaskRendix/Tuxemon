# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import final

from tuxemon.event import get_npc
from tuxemon.event.eventaction import EventAction
from tuxemon.session import Session
from tuxemon.states.world.worldstate import WorldState

logger = logging.getLogger(__name__)


@final
@dataclass
class TeleportAction(EventAction):
    """
    Teleport the player to a particular map and tile coordinates.

    Script usage:
        .. code-block::

            teleport <map_name>,<x>,<y>

    Script parameters:
        map_name: Name of the map to teleport to.
        x: X coordinate of the map to teleport to.
        y: Y coordinate of the map to teleport to.

    """

    name = "teleport"
    character: str
    map_name: str
    x: int
    y: int

    def start(self, session: Session) -> None:
        world = session.client.get_state_by_name(WorldState)
        delayed_teleport = world.teleporter.delayed_teleport

        char = get_npc(session, self.character)
        if char is None:
            logger.error(f"{self.character} not found")
            return

        session.client.current_music.stop()

        # Check to see if we're also performing a transition. If we are, wait
        # to perform the teleport at the apex of the transition
        if world.transition_manager.in_transition:
            if not delayed_teleport.is_active:
                delayed_teleport.char = char
                delayed_teleport.is_active = True
                delayed_teleport.mapname = self.map_name
                delayed_teleport.x = self.x
                delayed_teleport.y = self.y
        else:
            # Teleport the character immediately
            world.teleporter.teleport_character(
                char, self.map_name, self.x, self.y
            )
