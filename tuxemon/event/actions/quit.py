# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import final

from tuxemon.event.eventaction import EventAction
from tuxemon.session import Session


@final
@dataclass
class QuitAction(EventAction):
    """
    Completely quit the game.

    Script usage:
        .. code-block::

            quit
    """

    name = "quit"

    def start(self, session: Session) -> None:
        session.client.quit()
