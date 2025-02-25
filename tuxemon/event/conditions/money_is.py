# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from tuxemon.event import MapCondition
from tuxemon.event.eventcondition import EventCondition
from tuxemon.session import Session
from tuxemon.tools import compare


@dataclass
class MoneyIsCondition(EventCondition):
    """
    Check to see if the character has a certain amount of money (pocket).

    Script usage:
        .. code-block::

            is money_is <character>,<operator>,<amount>

    Script parameters:
        character: Either "player" or npc slug name (e.g. "npc_maple").
        operator: Numeric comparison operator. Accepted values are "less_than",
            "less_or_equal", "greater_than", "greater_or_equal", "equals"
            and "not_equals".
        amount: Amount of money or value stored in variable

    eg. "is money_is player,equals,50"
    eg. "is money_is player,equals,name_variable" (name_variable:75)

    """

    name = "money_is"
    wallet: str
    operator: str
    amount: Union[str, int]

    def test(self, session: Session, condition: MapCondition) -> bool:
        player = session.player
        if isinstance(self.amount, str):
            amount = 0
            if self.amount in player.game_variables:
                amount = int(player.game_variables.get(self.amount, 0))
        else:
            amount = self.amount

        # Check if the condition is true
        if self.wallet in player.money:
            return compare(self.operator, player.money[self.wallet], amount)
        return False
