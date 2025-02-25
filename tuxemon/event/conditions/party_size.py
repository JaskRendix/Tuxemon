# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging

from tuxemon.event import MapCondition, get_npc
from tuxemon.event.eventcondition import EventCondition
from tuxemon.session import Session
from tuxemon.tools import compare

logger = logging.getLogger(__name__)


from dataclasses import dataclass


@dataclass
class PartySizeCondition(EventCondition):
    """
    Check the character's party size.

    Script usage:
        .. code-block::

            is party_size <character>,<operator>,<value>

    Script parameters:
        character: Either "player" or npc slug name (e.g. "npc_maple").
        operator: Numeric comparison operator. Accepted values are "less_than",
            "less_or_equal", "greater_than", "greater_or_equal", "equals"
            and "not_equals".
        value: The value to compare the party size with.

    """

    name = "party_size"
    character: str
    operator: str
    value: int

    def test(self, session: Session, condition: MapCondition) -> bool:
        character = get_npc(session, self.character)
        if character is None:
            logger.error(f"{self.character} not found")
            return False
        return compare(self.operator, len(character.monsters), self.value)
