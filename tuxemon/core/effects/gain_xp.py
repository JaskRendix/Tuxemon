# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

from tuxemon.combat import set_var
from tuxemon.core.core_effect import ItemEffect, ItemEffectResult

if TYPE_CHECKING:
    from tuxemon.item.item import Item
    from tuxemon.monster import Monster
    from tuxemon.session import Session


@dataclass
class GainXpEffect(ItemEffect):
    """
    Add exp to the target by 'amount'.

    Parameters:
        amount: amount of experience

    """

    name = "gain_xp"
    amount: int

    def apply(
        self, session: Session, item: Item, target: Union[Monster, None]
    ) -> ItemEffectResult:
        assert target
        set_var(session, self.name, str(target.instance_id.hex))
        client = session.client.event_engine
        _params = [self.name, self.amount]
        client.execute_action("give_experience", _params, True)
        return ItemEffectResult(name=item.name, success=True)
