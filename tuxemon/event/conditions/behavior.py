# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from tuxemon.event import MapCondition
from tuxemon.event.conditions.button_pressed import ButtonPressedCondition
from tuxemon.event.conditions.char_at import CharAtCondition
from tuxemon.event.conditions.char_facing import CharFacingCondition
from tuxemon.event.conditions.char_facing_char import CharFacingCharCondition
from tuxemon.event.eventcondition import EventCondition
from tuxemon.session import Session


@dataclass
class BehaviorCondition(EventCondition):
    """
    Check if the behavior's conditions are true.

    Behavior is a combination of actions and conditions.

    """

    name = "behav"
    value1: str
    value2: Optional[str] = None

    def test(self, session: Session, condition: MapCondition) -> bool:
        cond = condition
        if self.value1 == "talk":
            assert self.value2
            char_facing_char = CharFacingCharCondition(
                "player", self.value2
            ).test(
                session,
                MapCondition(
                    "char_facing_char",
                    ["player", self.value2],
                    cond.x,
                    cond.y,
                    cond.width,
                    cond.height,
                    "is",
                    "cond10",
                ),
            )
            button_pressed = ButtonPressedCondition("K_RETURN").test(
                session,
                MapCondition(
                    "button_pressed",
                    ["K_RETURN"],
                    cond.x,
                    cond.y,
                    cond.width,
                    cond.height,
                    "is",
                    "cond20",
                ),
            )
            return char_facing_char and button_pressed
        elif self.value1 == "door":
            assert self.value2
            char_at = CharAtCondition("player").test(
                session,
                MapCondition(
                    "char_at",
                    ["player"],
                    cond.x,
                    cond.y,
                    cond.width,
                    cond.height,
                    "is",
                    "cond10",
                ),
            )
            char_facing = CharFacingCondition("player", self.value2).test(
                session,
                MapCondition(
                    "char_facing",
                    ["player", self.value2],
                    cond.x,
                    cond.y,
                    cond.width,
                    cond.height,
                    "is",
                    "cond20",
                ),
            )
            return char_at and char_facing
        return False
