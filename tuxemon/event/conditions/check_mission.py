# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2024 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging

from tuxemon.event import MapCondition, get_npc
from tuxemon.event.eventcondition import EventCondition
from tuxemon.mission import find_mission
from tuxemon.session import Session

logger = logging.getLogger(__name__)


class CheckMissionCondition(EventCondition):
    """
    Check to see the character has failed or completed a mission.
    Check to see if a mission is still pending.

    Script usage:
        .. code-block::

            is check_mission <character>,<mission>

    Script parameters:
        character: Either "player" or npc slug name (e.g. "npc_maple").
        method: Slug of the mission.

    eg. "is check_mission player,mission1

    """

    name = "check_mission"

    def test(self, session: Session, condition: MapCondition) -> bool:
        _character, _mission = condition.parameters[:2]
        character = get_npc(session, _character)
        if character is None:
            logger.error(f"{_character} not found")
            return False
        if not character.missions:
            return False
        if find_mission(character, _mission):
            return True
        return False
