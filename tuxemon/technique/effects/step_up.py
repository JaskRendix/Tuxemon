# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2024 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tuxemon import formula, prepare
from tuxemon.db import StatType
from tuxemon.shape import Shape
from tuxemon.technique.techeffect import TechEffect, TechEffectResult

if TYPE_CHECKING:
    from tuxemon.monster import Monster
    from tuxemon.technique.technique import Technique


class StepUpEffectResult(TechEffectResult):
    pass


@dataclass
class StepUpEffect(TechEffect):
    """
    This effect modifies the monster's statistics by a certain amount.
    """

    name = "step_up"
    objective: str
    statistics: str

    def apply(
        self, tech: Technique, user: Monster, target: Monster
    ) -> StepUpEffectResult:

        if self.objective not in ("user", "target", "both"):
            raise ValueError(
                f"{self.objective} must be 'user', 'target' or 'both'"
            )

        statistics = self.statistics.split(":")

        tech.hit = tech.accuracy >= (
            tech.combat_state._random_tech_hit.get(user, 0.0)
            if tech.combat_state
            else 0.0
        )

        if tech.hit:
            _apply_step_effect(user, target, statistics, self.objective, "up")

        return {
            "success": True,
            "damage": 0,
            "element_multiplier": 0.0,
            "should_tackle": False,
            "extra": None,
        }


def _apply_step_effect(
    user: Monster,
    target: Monster,
    statistics: list[str],
    objective: str,
    indicator: str,
) -> None:
    """
    Applies the effect to the specified monster(s) and statistic(s).
    """
    if objective == "both":
        for monster in (user, target):
            _apply_to_monster(monster, statistics, indicator)
    else:
        monster = user if objective == "user" else target
        _apply_to_monster(monster, statistics, indicator)


def _apply_to_monster(
    monster: Monster, statistics: list[str], indicator: str
) -> None:
    """
    Applies the effect to the specified monster(s) and statistic(s).
    """
    for statistic in statistics:
        _apply_statistic(monster, statistic, indicator)


def _apply_statistic(monster: Monster, statistic: str, indicator: str) -> None:
    """
    Applies the effect to the specified monster and statistic(s).
    """
    if statistic not in list(StatType):
        raise ValueError(f"{statistic} isn't among {list(StatType)}")

    amount = monster.return_stat(StatType(statistic))
    base = calculate_base_stat(monster, statistic)
    step = formula.calculate_step(base, amount)
    new_amount = formula.calculate_adjusted_stat(
        base, step + (1 if indicator == "up" else -1)
    )
    setattr(monster, statistic, new_amount)


def calculate_base_stat(monster: Monster, stat_name: str) -> int:
    """
    Calculate a single base stat of the monster.

    Parameters:
        stat_name: The name of the stat to calculate (e.g. 'armour', 'dodge', etc.).

    Returns:
        The calculated base stat.
    """
    level = monster.level
    multiplier = level + prepare.COEFF_STATS
    shape = Shape(monster.shape)
    if stat_name == "armour":
        shape_stat = shape.armour * multiplier
    elif stat_name == "dodge":
        shape_stat = shape.dodge * multiplier
    elif stat_name == "hp":
        shape_stat = shape.hp * multiplier
    elif stat_name == "melee":
        shape_stat = shape.melee * multiplier
    elif stat_name == "ranged":
        shape_stat = shape.ranged * multiplier
    elif stat_name == "speed":
        shape_stat = shape.speed * multiplier
    else:
        raise ValueError(f"Invalid stat name: {stat_name}")
    mod = getattr(monster, f"mod_{stat_name}")
    return shape_stat + int(mod)
