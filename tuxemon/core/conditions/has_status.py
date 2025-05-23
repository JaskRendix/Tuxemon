# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from tuxemon.core.core_condition import CoreCondition

if TYPE_CHECKING:
    from tuxemon.monster import Monster
    from tuxemon.session import Session


@dataclass
class HasStatusCondition(CoreCondition):
    """
    Checks if the creature has a status or not.

    """

    name = "has_status"

    def test_with_monster(self, session: Session, target: Monster) -> bool:
        return bool(target.status)
