# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, final

from tuxemon.event.eventaction import EventAction
from tuxemon.graphics import ColorLike, string_to_colorlike
from tuxemon.prepare import BLACK_COLOR, TRANS_TIME
from tuxemon.session import Session
from tuxemon.states.world.worldstate import WorldState


@final
@dataclass
class ScreenTransitionAction(EventAction):
    """
    Initiate a screen transition.

    Script usage:
        .. code-block::

            screen_transition [trans_time][,rgb]

    Script parameters:
        trans_time: Transition time in seconds - default 0.3
        rgb: color (eg red > 255,0,0 > 255:0:0) - default rgb(0,0,0)

    eg: "screen_transition 3"
    eg: "screen_transition 3,255:0:0:50" (red)
    """

    name = "screen_transition"
    trans_time: Optional[float] = None
    rgb: Optional[str] = None

    def start(self, session: Session) -> None:
        pass

    def update(self, session: Session) -> None:
        world = session.client.get_state_by_name(WorldState)
        _time = TRANS_TIME if self.trans_time is None else self.trans_time
        rgb: ColorLike = BLACK_COLOR
        if self.rgb:
            rgb = string_to_colorlike(self.rgb)

        def fade_in() -> None:
            world.transition_manager.fade_in(_time, rgb)

        world.transition_manager.fade_out(_time, rgb)
        world.task(fade_in, _time)
        self.stop()
