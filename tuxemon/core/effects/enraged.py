# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tuxemon.core.core_effect import StatusEffect, StatusEffectResult

if TYPE_CHECKING:
    from tuxemon.monster import Monster
    from tuxemon.status.status import Status


@dataclass
class EnragedEffect(StatusEffect):
    """
    Enraged status

    """

    name = "enraged"

    def apply(self, status: Status, target: Monster) -> StatusEffectResult:
        if status.phase == "perform_action_tech":
            target.status.clear()
        return StatusEffectResult(name=status.name, success=True)
