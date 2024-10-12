# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2024 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
"""This module contains the Options state"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from functools import partial
from typing import Any, Optional

import pygame_menu
from pygame_menu import locals
from pygame_menu.locals import POSITION_CENTER

from tuxemon import prepare, tools
from tuxemon.db import MissionStatus
from tuxemon.locale import T
from tuxemon.menu.menu import PygameMenuState
from tuxemon.menu.theme import get_theme
from tuxemon.mission import Mission
from tuxemon.npc import NPC
from tuxemon.session import local_session
from tuxemon.tools import open_choice_dialog, open_dialog


class MissionState(PygameMenuState):
    """
    This state is responsible for the mission menu.
    """

    def __init__(self, **kwargs: Any) -> None:
        """
        Used when initializing the state.
        """
        character: Optional[NPC] = None
        for element in kwargs.values():
            character = element["character"]
        if character is None:
            raise ValueError("No character found")
        self.character = character
        width, height = prepare.SCREEN_SIZE

        background = pygame_menu.BaseImage(
            image_path=tools.transform_resource_filename(prepare.BG_MISSIONS),
            drawing_position=POSITION_CENTER,
        )
        theme = get_theme()
        theme.scrollarea_position = locals.POSITION_EAST
        theme.background_color = background
        theme.widget_alignment = locals.ALIGN_CENTER

        width = int(0.8 * width)
        height = int(0.8 * height)
        super().__init__(height=height, width=width)
        self.initialize_items(self.menu)
        self.repristinate()

    def repristinate(self) -> None:
        """Repristinate original theme (color, alignment, etc.)"""
        theme = get_theme()
        theme.scrollarea_position = locals.SCROLLAREA_POSITION_NONE
        theme.background_color = self.background_color
        theme.widget_alignment = locals.ALIGN_LEFT

    def initialize_items(self, menu: pygame_menu.Menu) -> None:
        """Initialize the mission menu with the character's missions."""

        def handle_mission_choice(mission: Mission) -> None:
            """Handle the user's choice when interacting with a mission."""
            msg = T.translate("mission_question")
            open_dialog(local_session, [msg])
            _no = T.translate("no")
            _yes = T.translate("yes")
            choices: Sequence[tuple[str, str, Callable[[], None]]] = [
                ("no", _no, partial(_handle_no_choice, mission)),
                ("yes", _yes, partial(_handle_yes_choice, mission)),
            ]
            open_choice_dialog(local_session, choices)

        def _handle_yes_choice(mission: Mission) -> None:
            """Handle the user's choice to accept a mission."""
            mission.accept_mission()
            self.client.remove_state_by_name("ChoiceState")
            self.client.remove_state_by_name("DialogState")
            self.client.remove_state_by_name("MissionState")

        def _handle_no_choice(mission: Mission) -> None:
            """Handle the user's choice to decline a mission."""
            mission.refuse_mission()
            self.client.remove_state_by_name("ChoiceState")
            self.client.remove_state_by_name("DialogState")
            self.client.remove_state_by_name("MissionState")

        for status in MissionStatus:
            missions = [
                mission
                for mission in self.character.missions
                if mission.status == status and mission.enabled
            ]
            translated_status = T.translate(status)
            if missions:
                menu.add.label(f"{translated_status} ({len(missions)})")
                for key, mission in enumerate(missions, start=1):
                    label = f"{key}. {mission.name}"
                    if mission.status == MissionStatus.pending:
                        menu.add.button(
                            title=label,
                            action=partial(handle_mission_choice, mission),
                            font_size=self.font_size_small,
                        )
                    else:
                        menu.add.button(
                            title=label,
                            action=None,
                            font_size=self.font_size_small,
                        )
