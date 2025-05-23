# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

from tuxemon.core.core_effect import ItemEffect, ItemEffectResult
from tuxemon.db import db
from tuxemon.element import Element

if TYPE_CHECKING:
    from tuxemon.item.item import Item
    from tuxemon.monster import Monster
    from tuxemon.session import Session


@dataclass
class SwitchTypeEffect(ItemEffect):
    """
    Changes monster type.

    Parameters:
        element: type of element (wood, water, etc.)

    Examples:
        "switch wood" or "switch random"
        if "switch random" then the type is chosen randomly.

    """

    name = "switch_type"
    element: str

    def apply(
        self, session: Session, item: Item, target: Union[Monster, None]
    ) -> ItemEffectResult:
        elements = list(db.database["element"])
        if target:
            if self.element != "random":
                ele = Element(self.element)
                if ele not in target.types:
                    target.types = [ele]
            else:
                random_target_element = random.choice(elements)
                target.types = [Element(random_target_element)]
        return ItemEffectResult(name=item.name, success=target is not None)
