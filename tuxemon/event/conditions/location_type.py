# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass

from tuxemon.db import MapType
from tuxemon.event import MapCondition
from tuxemon.event.eventcondition import EventCondition
from tuxemon.session import Session


@dataclass
class LocationTypeCondition(EventCondition):
    """
    Check to see if the player is in a certain location type.

    Script usage:
        .. code-block::

            is location_type <slug>

    Script parameters:
        slug: Slug name.
        Either all, notype, town, route, clinic, shop, dungeon

    eg. "is location_type clinic"
    eg. "is location_type town:shop"

    """

    name = "location_type"
    location: str

    def test(self, session: Session, condition: MapCondition) -> bool:
        client = session.client
        ret: bool = False
        locs: list[str] = []
        if self.location.find(":") > 1:
            locs = self.location.split(":")
        else:
            if self.location == "all":
                locs = list(MapType)
            else:
                locs.append(self.location)

        if client.map_type and client.map_type in locs:
            ret = True
        return ret
