# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

from tuxemon.core.core_effect import ItemEffect, ItemEffectResult

if TYPE_CHECKING:
    from tuxemon.item.item import Item
    from tuxemon.monster import Monster
    from tuxemon.session import Session


@dataclass
class LearnTmEffect(ItemEffect):
    """
    This effect teaches the technique in the parameters.

    Parameters:
        technique: technique's slug (eg. ram, etc.)

    """

    name = "learn_tm"
    technique: str

    def apply(
        self, session: Session, item: Item, target: Union[Monster, None]
    ) -> ItemEffectResult:

        target_moves = (
            {tech.slug for tech in target.moves} if target else set()
        )

        if target and self.technique not in target_moves:
            client = session.client
            var = f"{self.name}:{str(target.instance_id.hex)}"
            client.event_engine.execute_action("set_variable", [var], True)
            client.event_engine.execute_action(
                "add_tech", [self.name, self.technique], True
            )

            return ItemEffectResult(name=item.name, success=True)

        return ItemEffectResult(name=item.name)
