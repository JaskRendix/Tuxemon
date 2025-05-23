# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

from tuxemon.core.core_condition import CoreCondition

if TYPE_CHECKING:
    from tuxemon.monster import Monster
    from tuxemon.session import Session


@dataclass
class VariableCondition(CoreCondition):
    """Checks against the variables of the context.
    Accepts two parameters; variable name and expected value.
    """

    name = "variable"
    var_name: str
    expected: Union[str, int, None] = None

    def test_with_monster(self, session: Session, target: Monster) -> bool:
        var_name = self.var_name
        expect = self.expected

        player = session.player
        if type(expect) is str:
            return bool(player.game_variables[var_name] == expect)
        elif type(expect) is int:
            return bool(player.game_variables[var_name] >= expect)
        else:
            return not player.game_variables[var_name]
