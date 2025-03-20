# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, final

from tuxemon.event import get_npc
from tuxemon.event.eventaction import EventAction
from tuxemon.locale import T

logger = logging.getLogger(__name__)


@final
@dataclass
class AddContactsAction(EventAction):
    """
    Add contact to the app.

    slug must have the msgid inside the PO.

    Script usage:
        .. code-block::

            add_contacts <character>,<npc_slug>,[relation],[strength],
                        [],[decay_rate],[decay_threshold]

    Script parameters:
        character: Either "player" or character slug name (e.g. "npc_maple").
        npc_slug: slug name (e.g. "npc_maple").
        relation: type of relation
        strength: amount of strength (higher, better), default 50
        steps: amount of steps, default character steps
        decay_rate: decay rate of the relationship, default 0.01
        decay_threshold: threshold of steps after which the decay triggers,
            default 500
    """

    name = "add_contacts"
    character: str
    npc_slug: str
    relation: str
    strength: Optional[int] = None
    last_interaction: Optional[float] = None
    decay_rate: Optional[float] = None
    decay_threshold: Optional[int] = None

    def start(self) -> None:
        character = get_npc(self.session, self.character)
        if character is None:
            logger.error(f"{self.character} not found")
            return

        if not T.has_translation("en_US", self.relation):
            logger.error(f"Add msgid {self.relation} in the 'en_US' base.po")
            return

        relationships = character.relationships
        contact = relationships.get_connection(self.npc_slug)
        if contact is None:
            relationships.add_connection(
                slug=self.npc_slug,
                relationship_type=self.relation,
                strength=self.strength or 50,
                last_interaction=self.last_interaction or character.steps,
                decay_rate=self.decay_rate or 0.01,
                decay_threshold=self.decay_threshold or 500,
            )
        else:
            logger.error(f"{self.npc_slug} already exist")
            return
