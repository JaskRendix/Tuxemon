# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass

from tuxemon.event import MapCondition
from tuxemon.event.eventcondition import EventCondition
from tuxemon.session import Session


@dataclass
class MonsterFlairCondition(EventCondition):
    """
    Check to see if the given monster flair matches the expected value.

    Script usage:
        .. code-block::

            is monster_flair <slot>,<category>,<flair>

    Script parameters:
        slot: Position of the monster in the player monster list.
        category: Category of the flair.
        flair: Name of the flair.

    """

    name = "monster_flair"
    slot: int
    category: str
    flair: str

    def test(self, session: Session, condition: MapCondition) -> bool:
        monster = session.player.monsters[self.slot]
        try:
            return monster.flairs[self.category].name == self.name
        except KeyError:
            return False
