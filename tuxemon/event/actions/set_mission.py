# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2024 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import final

from tuxemon.db import MissionStatus, db
from tuxemon.event import get_npc
from tuxemon.event.eventaction import EventAction
from tuxemon.mission import Mission, check_reqs, has_mission

logger = logging.getLogger(__name__)

lookup_cache: dict[str, Mission] = {}


@final
@dataclass
class SetMissionAction(EventAction):
    """
    Set mission.

    Script usage:
        .. code-block::

            set_mission <character>,<slug>

    Script parameters:
        character: Either "player" or npc slug name (e.g. "npc_maple").
        slug: slug mission

    """

    name = "set_mission"
    character: str

    def start(self) -> None:
        if not lookup_cache:
            _lookup_missions()
        character = get_npc(self.session, self.character)
        if character is None:
            logger.error(f"{self.character} not found")
            return

        for slug, mission in lookup_cache.items():
            if character.missions:
                if not has_mission(character, slug):
                    if check_reqs(mission.reqs, character):
                        mission.add_mission(character)
                else:
                    if mission.status == MissionStatus.accepted:
                        if mission.success_reqs and check_reqs(
                            mission.success_reqs, character
                        ):
                            mission.completed_mission()
                        elif mission.failure_reqs and check_reqs(
                            mission.failure_reqs, character
                        ):
                            mission.failed_mission()
            else:
                if check_reqs(mission.reqs, character):
                    mission.add_mission(character)


def _lookup_missions() -> None:
    missions = list(db.database["mission"])
    for mis in missions:
        results = db.lookup(mis, table="mission")
        mission = Mission()
        mission.load(results.slug)
        lookup_cache[mis] = mission
