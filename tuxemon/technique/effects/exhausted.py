from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

from tuxemon.monster import Monster
from tuxemon.technique.techeffect import TechEffect, TechEffectResult
from tuxemon.technique.technique import Technique


class ExhaustedEffectResult(TechEffectResult):
    damage: int
    should_tackle: bool
    status: Optional[Technique]


@dataclass
class ExhaustedEffect(TechEffect):
    """
    This effect has a chance to apply the exhausted status effect.
    """

    name = "exhausted"
    objective: str

    def apply(
        self, tech: Technique, user: Monster, target: Monster
    ) -> ExhaustedEffectResult:
        obj = self.objective
        success = tech.potency >= random.random()
        if success:
            tech = Technique("status_exhausted")
            if obj == "user":
                user.apply_status(tech)
            elif obj == "target":
                target.apply_status(tech)
            return {"status": tech}

        return {"damage": 0, "should_tackle": False, "success": False}