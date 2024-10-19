# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2024 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tuxemon.technique.effects.step_up import _apply_step_effect
from tuxemon.technique.techeffect import TechEffect, TechEffectResult

if TYPE_CHECKING:
    from tuxemon.monster import Monster
    from tuxemon.technique.technique import Technique


class StepDownEffectResult(TechEffectResult):
    pass


@dataclass
class StepDownEffect(TechEffect):
    """
    This effect modifies the monster's statistics by a certain amount.
    """

    name = "step_down"
    objective: str
    statistics: str

    def apply(
        self, tech: Technique, user: Monster, target: Monster
    ) -> StepDownEffectResult:

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
            _apply_step_effect(
                user, target, statistics, self.objective, "down"
            )

        return {
            "success": True,
            "damage": 0,
            "element_multiplier": 0.0,
            "should_tackle": False,
            "extra": None,
        }
