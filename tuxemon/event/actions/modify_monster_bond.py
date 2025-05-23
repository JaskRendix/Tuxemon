# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging
import random as rd
import uuid
from dataclasses import dataclass
from typing import Optional, Union, final

from tuxemon.event import get_monster_by_iid
from tuxemon.event.eventaction import EventAction
from tuxemon.formula import change_bond
from tuxemon.session import Session

logger = logging.getLogger(__name__)


@final
@dataclass
class ModifyMonsterBondAction(EventAction):
    """
    Change the bond of a monster in the current player's party.

    Script usage:
        .. code-block::

            modify_monster_bond [variable][,amount]

    Script parameters:
        variable: Name of the variable where to store the monster id. If no
            variable is specified, all monsters are touched.
        amount: An int or float value, if no amount, then default 1 (int).
        lower_bound: Lower bound of range to return an integer between (inclusive)
        upper_bound: Upper bound of range to return an integer between (inclusive)

    eg. "modify_monster_bond"
    eg. "modify_monster_bond name_variable,25"
    eg. "modify_monster_bond name_variable,-0.5"
    eg. "modify_monster_bond name_variable,,1,5" (random between 1 and 5)
    eg. "modify_monster_bond name_variable,,-5,-1" (random between -5 and -1)
    """

    name = "modify_monster_bond"
    variable: Optional[str] = None
    amount: Optional[Union[int, float]] = None
    lower_bound: Optional[int] = None
    upper_bound: Optional[int] = None

    def start(self, session: Session) -> None:
        player = session.player
        if not player.monsters:
            return

        amount_bond = self.amount if self.amount else 1
        if (
            amount_bond == 1
            and self.lower_bound is not None
            and self.upper_bound is not None
        ):
            amount_bond = rd.randint(self.lower_bound, self.upper_bound)

        if self.variable is None:
            for mon in player.monsters:
                change_bond(mon, amount_bond)
        else:
            if self.variable not in player.game_variables:
                logger.error(f"Game variable {self.variable} not found")
                return
            monster_id = uuid.UUID(player.game_variables[self.variable])
            monster = get_monster_by_iid(session, monster_id)
            if monster is None:
                logger.error("Monster not found")
                return
            else:
                change_bond(monster, amount_bond)
