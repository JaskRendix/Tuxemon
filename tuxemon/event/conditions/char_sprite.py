# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging

from tuxemon.event import MapCondition, get_npc
from tuxemon.event.eventcondition import EventCondition
from tuxemon.session import Session

logger = logging.getLogger(__name__)


from dataclasses import dataclass


@dataclass
class CharSpriteCondition(EventCondition):
    """
    Check the character's sprite

    Script usage:
        .. code-block::

            is char_sprite <character>,<sprite>

    Script parameters:
        character: Either "player" or character slug name (e.g. "npc_maple")
        sprite: NPC's sprite (eg maniac, florist, etc.)

    """

    name = "char_sprite"
    character: str
    sprite: str

    def test(self, session: Session, condition: MapCondition) -> bool:
        character = get_npc(session, self.character)
        if character is None:
            logger.error(f"{self.character} not found")
            return False
        if character.template.sprite_name == self.sprite:
            return True
        return False
