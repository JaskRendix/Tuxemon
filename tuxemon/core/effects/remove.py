# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING

from tuxemon.combat import get_target_monsters, has_status
from tuxemon.core.core_effect import TechEffect, TechEffectResult

if TYPE_CHECKING:
    from tuxemon.monster import Monster
    from tuxemon.session import Session
    from tuxemon.technique.technique import Technique


@dataclass
class RemoveEffect(TechEffect):
    """
    This effect has a chance to remove a status effect.

    Parameters:
        status: The Status slug (e.g. enraged).
        objectives: The targets (e.g. own_monster, enemy_monster, etc.), if
            single "enemy_monster" or "enemy_monster:own_monster"

    eg "remove xxx,own_monster" removes only xxx
    eg "remove all,own_monster" removes everything
    """

    name = "remove"
    status: str
    objectives: str

    def apply(
        self, session: Session, tech: Technique, user: Monster, target: Monster
    ) -> TechEffectResult:
        monsters: list[Monster] = []
        combat = tech.combat_state
        assert combat

        objectives = self.objectives.split(":")
        potency = random.random()
        value = combat._random_tech_hit.get(user, 0.0)
        success = tech.potency >= potency and tech.accuracy >= value

        if success:
            monsters = get_target_monsters(objectives, tech, user, target)
            if self.status == "all":
                for monster in monsters:
                    monster.status.clear()
            else:
                for monster in monsters:
                    if has_status(monster, self.status):
                        monster.status.clear()

        return TechEffectResult(name=tech.name, success=bool(monsters))
