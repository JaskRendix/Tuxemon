# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2024 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import final

from tuxemon.event.eventaction import EventAction
from tuxemon.states.world.worldstate import WorldState

logger = logging.getLogger(__name__)


@final
@dataclass
class ChangeMapAction(EventAction):
    """
    Change map without player.

    Script usage:
        .. code-block::

            change_map <map_name>

    Script parameters:
        map_name: Name of the map to teleport to.

    """

    name = "change_map"
    map_name: str

    def start(self) -> None:
        world = self.session.client.get_state_by_name(WorldState)
        self.session.client.current_music.stop()
        world.teleporter.teleport(world, self.map_name)
