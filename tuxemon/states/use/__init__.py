# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

import pygame_menu
from pygame_menu import locals

from tuxemon import prepare
from tuxemon.menu.menu import PygameMenuState
from tuxemon.menu.theme import get_theme
from tuxemon.session import local_session
from tuxemon.tools import show_result_as_dialog

if TYPE_CHECKING:
    from tuxemon.animation import Animation
    from tuxemon.item.item import Item
    from tuxemon.npc import NPC
    from tuxemon.technique.technique import Technique


class UseState(PygameMenuState):
    """
    This state is responsible for the use menu.

    Using items or techs in the WorldState
    """

    def use_item(self, item: Item) -> None:
        result = item.use(self.session, self.char, None)
        if (item.behaviors.show_dialog_on_failure and not result.success) or (
            item.behaviors.show_dialog_on_success and result.success
        ):
            show_result_as_dialog(self.session, item, result.success)
        self.client.remove_state_by_name("UseState")
        self.client.remove_state_by_name("WorldMenuState")

    def use_tech(self, tech: Technique) -> None:
        result = tech.use(self.session, None, None)
        show_result_as_dialog(self.session, tech, result.success)
        self.client.remove_state_by_name("UseState")
        self.client.remove_state_by_name("WorldMenuState")

    def add_menu_items(self, menu: pygame_menu.Menu) -> None:
        if self.items:
            for item in self.items:
                if not any(
                    item.validate_monster(local_session, m)
                    for m in self.char.monsters
                ):
                    menu.add.label(title=item.name)
                else:
                    menu.add.button(
                        title=item.name, action=partial(self.use_item, item)
                    )

        if self.techs:
            for tech in self.techs:
                if not any(
                    tech.validate_monster(local_session, m)
                    for m in self.char.monsters
                ):
                    menu.add.label(title=tech.name)
                else:
                    menu.add.button(
                        title=tech.name, action=partial(self.use_tech, tech)
                    )

    def __init__(
        self, character: NPC, items: list[Item], techs: list[Technique]
    ) -> None:
        self.session = local_session
        self.char = character
        self.items = items
        self.techs = techs

        theme = get_theme()
        theme.scrollarea_position = locals.POSITION_EAST
        theme.widget_alignment = locals.ALIGN_CENTER

        super().__init__()

        self.add_menu_items(self.menu)
        self.reset_theme()

    def update_animation_size(self) -> None:
        width, height = prepare.SCREEN_SIZE
        widgets_size = self.menu.get_size(widget=True)
        _width, _height = widgets_size
        # block width if more than screen width
        _width = width if _width >= width else _width
        _height = height if _height >= height else _height

        self.menu.resize(
            max(1, int(_width * self.animation_size)),
            max(1, int(_height * self.animation_size)),
        )

    def animate_open(self) -> Animation:
        self.animation_size = 0.0
        ani = self.animate(self, animation_size=1.0, duration=0.2)
        ani.update_callback = self.update_animation_size
        return ani
