# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tuxemon.core.core_effect import StatusEffect, StatusEffectResult
from tuxemon.tools import ops_dict

if TYPE_CHECKING:
    from tuxemon.monster import Monster
    from tuxemon.session import Session
    from tuxemon.status.status import Status


@dataclass
class StatChangeEffect(StatusEffect):
    """
    Change combat stats.

    JSON SYNTAX:
        value: The number to change the stat by, default is add, use
            negative to subtract.
        dividing: Set this to True to divide instead of adding or
            subtracting the value.
        overridetofull: In most cases you won't need this. If ``True`` it
            will set the stat to its original value rather than the
            specified value, but due to the way the
            game is coded, it currently only works on hp.

    """

    name = "statchange"

    def apply(
        self, session: Session, status: Status, target: Monster
    ) -> StatusEffectResult:
        statsmaster = [
            status.statspeed,
            status.stathp,
            status.statarmour,
            status.statmelee,
            status.statranged,
            status.statdodge,
        ]
        statslugs = [
            "speed",
            "current_hp",
            "armour",
            "melee",
            "ranged",
            "dodge",
        ]
        newstatvalue = 0
        if status.phase == "perform_action_status":
            for stat, slugdata in zip(statsmaster, statslugs):
                if not stat:
                    continue
                value = stat.value
                max_deviation = stat.max_deviation
                operation = stat.operation
                override = stat.overridetofull
                basestatvalue = getattr(target, slugdata)
                min_value = value - max_deviation
                max_value = value + max_deviation
                if max_deviation:
                    value = random.randint(int(min_value), int(max_value))

                if value > 0 and not override:
                    newstatvalue = ops_dict[operation](basestatvalue, value)
                if slugdata == "current_hp" and override:
                    target.current_hp = target.hp
                if newstatvalue <= 0:
                    newstatvalue = 1
                setattr(target, slugdata, newstatvalue)
        return StatusEffectResult(name=status.name, success=bool(newstatvalue))
