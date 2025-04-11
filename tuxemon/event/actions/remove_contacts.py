# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import final

from tuxemon.event import get_npc
from tuxemon.event.eventaction import EventAction

logger = logging.getLogger(__name__)


@final
@dataclass
class RemoveContactsAction(EventAction):
    """
    Remove contact from the app.

    Script usage:
        .. code-block::

            remove_contacts <character>,<slug>

    Script parameters:
        character: Either "player" or character slug name (e.g. "npc_maple").
        slug: slug name (e.g. "npc_maple").
    """

    name = "remove_contacts"
    character: str
    slug: str

    def start(self) -> None:
        character = get_npc(self.session, self.character)
        if character is None:
            logger.error(f"{self.character} not found")
            return

        relationships = character.relationships
        contact = relationships.get_connection(self.slug)
        if contact is None:
            logger.error("Nothing to remove")
            return
        else:
            relationships.remove_connection(self.slug)
