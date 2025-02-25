# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
import logging
from typing import Optional

from tuxemon.event import MapCondition, get_npc
from tuxemon.event.eventcondition import EventCondition
from tuxemon.session import Session
from tuxemon.tools import compare

logger = logging.getLogger(__name__)


from dataclasses import dataclass


@dataclass
class HasItemCondition(EventCondition):
    """
    Check to see if a character inventory contains something.

    Script usage:
        .. code-block::

            is has_item <character>,<item>[,operator][,quantity]

    Script parameters:
        character: Either "player" or npc slug name (e.g. "npc_maple").
        item: The item slug name (e.g. "item_cherry").
        operator: Numeric comparison operator. Accepted values are "less_than",
            "less_or_equal", "greater_than", "greater_or_equal", "equals"
            and "not_equals".
        quantity: Quantity to compare with.

    """

    name = "has_item"
    character: str
    item_slug: str
    operator: Optional[str] = None
    quantity: Optional[int] = None

    def test(self, session: Session, condition: MapCondition) -> bool:
        def op(itm_qty: int, op: str, qty: int) -> bool:
            return compare(op, itm_qty, qty)

        npc = get_npc(session, self.character)
        if npc is None:
            logger.error(f"{self.character} doesn't exist.")
            return False
        itm = npc.find_item(self.item_slug)
        if itm is None:
            return False
        else:
            if self.operator is not None and self.quantity is not None:
                operator = self.operator.lower()
                return op(itm.quantity, operator, self.quantity)
            else:
                return True
