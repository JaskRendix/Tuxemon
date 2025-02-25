# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging

from tuxemon.db import OutputBattle
from tuxemon.event import MapCondition
from tuxemon.event.eventcondition import EventCondition
from tuxemon.session import Session

logger = logging.getLogger(__name__)


from dataclasses import dataclass


@dataclass
class BattleIsCondition(EventCondition):
    """
    Check to see if a character has fought against another one
    and won, lost or draw.

    Script usage:
        .. code-block::

            is battle_is <fighter>,<outcome>,<opponent>

    Script parameters:
        fighter: Npc slug name (e.g. "npc_maple").
        outcome: One among "won", "lost" and "draw".
        opponent: Npc slug name (e.g. "npc_maple").

    eg. "is battle_is player,won,npc_maple"
        -> has player won against npc_maple in the last fight?

    """

    name = "battle_is"
    fighter: str
    outcome: str
    opponent: str

    def test(self, session: Session, condition: MapCondition) -> bool:
        player = session.player

        # no battles
        if not player.battles:
            return False
        if self.outcome not in list(OutputBattle):
            logger.error(f"{self.outcome} isn't among {list(OutputBattle)}")
            return False

        battles = [
            battle
            for battle in player.battles
            if battle.fighter == self.fighter
            and battle.opponent == self.opponent
            and battle.outcome == self.outcome
        ]
        # look for last battle
        if len(battles) > 1:
            last_one = sorted(battles, key=lambda x: x.steps, reverse=True)
            return last_one[0].outcome == self.outcome
        return bool(battles)
