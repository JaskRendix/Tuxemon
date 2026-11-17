# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2026 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from unittest.mock import MagicMock, patch

import pytest

from tuxemon.db import State
from tuxemon.states.combat_menus import (
    MainCombatMenuState,
    TechniquePreviewOverlay,
)


@pytest.fixture
def menu():
    menu = MainCombatMenuState.__new__(MainCombatMenuState)

    menu.session = MagicMock()
    menu.monster = MagicMock()
    menu.monster.name = "Testmon"

    menu.character = MagicMock()
    menu.client = MagicMock()
    menu.combat = MagicMock()
    menu.combat_session = MagicMock()

    menu.event_bus = MagicMock()

    menu.opponents = [MagicMock()]
    menu.rect = MagicMock()

    menu.preview_overlay = MagicMock()

    return menu


def test_show_clears_before_rendering():
    overlay = TechniquePreviewOverlay.__new__(TechniquePreviewOverlay)

    overlay.clear = MagicMock()
    overlay._draw_types = MagicMock()
    overlay._draw_range = MagicMock()
    overlay._draw_speed = MagicMock()
    overlay._draw_stats = MagicMock()

    technique = MagicMock()

    overlay.show(technique)

    overlay.clear.assert_called_once()
    overlay._draw_types.assert_called_once_with(technique)
    overlay._draw_range.assert_called_once_with(technique)
    overlay._draw_speed.assert_called_once_with(technique)
    overlay._draw_stats.assert_called_once_with(technique)


def test_clear_kills_all_sprites():
    overlay = TechniquePreviewOverlay.__new__(TechniquePreviewOverlay)

    sprite1 = MagicMock()
    sprite2 = MagicMock()

    overlay.type_icons = [sprite1]
    overlay.text_sprites = {"x": sprite2}

    overlay.range_icon = MagicMock()
    overlay.speed_icon = MagicMock()

    overlay.clear()

    sprite1.kill.assert_called_once()
    sprite2.kill.assert_called_once()

    assert overlay.range_icon is None
    assert overlay.speed_icon is None
    assert overlay.type_icons == []
    assert overlay.text_sprites == {}


def test_show_technique_preview_no_selected_item(menu):
    menu_obj = MagicMock()
    menu_obj.get_selected_item.return_value = None

    menu._show_technique_preview(menu_obj)

    menu.preview_overlay.show.assert_not_called()


def test_validate_item_target(menu):
    item = MagicMock()
    monster = MagicMock()

    item.validate_monster.return_value = True

    assert menu._validate_item_target(
        item,
        monster,
    )

    item.validate_monster.assert_called_once_with(
        menu.session,
        monster,
    )


def test_choose_technique_target_multiple_opponents(menu):
    technique = MagicMock()
    technique.targets_enemy.return_value = True

    menu.opponents = [
        MagicMock(),
        MagicMock(),
    ]

    menu_item = MagicMock()
    menu_item.game_object = technique

    with patch(
        "tuxemon.states.combat_menus.CombatTargetMenuState"
    ) as target_menu:
        menu._choose_technique_target(menu_item)

    target_menu.assert_called_once()
    menu.client.push_state.assert_called_once()


def test_choose_item_target_throwable(menu):
    item = MagicMock()
    item.behaviors.throwable = True
    item.usable_in = [State["MainCombatMenuState"]]

    enemy = MagicMock()
    menu.opponents = [enemy]

    menu_item = MagicMock()
    menu_item.game_object = item

    menu._enqueue_item = MagicMock()

    menu._choose_item_target(menu_item)

    menu._enqueue_item.assert_called_once_with(
        item,
        enemy,
    )


@pytest.mark.parametrize(
    "fainted,active,can_swap,expected",
    [
        pytest.param(
            True,
            False,
            True,
            False,
            id="fainted",
        ),
        pytest.param(
            False,
            True,
            True,
            False,
            id="active",
        ),
        pytest.param(
            False,
            False,
            False,
            False,
            id="cannot-swap",
        ),
        pytest.param(
            False,
            False,
            True,
            True,
            id="valid",
        ),
    ],
)
def test_validate_swap_target(
    menu,
    fainted,
    active,
    can_swap,
    expected,
):
    monster = MagicMock()
    monster.is_fainted = fainted

    menu.combat_session.active_monsters = [monster] if active else []

    menu.combat_session.swap_tracker.can_swap.return_value = can_swap

    assert menu._validate_swap_target(monster) is expected


def test_validate_swap_target_none(menu):
    assert menu._validate_swap_target(None) is False


def test_validate_item_non_throwable(menu):
    item = MagicMock()
    item.behaviors.throwable = False

    assert menu._validate_item(item)


def test_validate_item_none(menu):
    assert menu._validate_item(None)


def test_validate_throwable_item(menu):
    opponent1 = MagicMock()
    opponent2 = MagicMock()

    menu.opponents = [opponent1, opponent2]

    item = MagicMock()
    item.behaviors.throwable = True

    item.validate_monster.return_value = True

    assert menu._validate_item(item)

    assert item.validate_monster.call_count == 2


def test_validate_throwable_item_invalid(menu):
    menu.opponents = [MagicMock()]

    item = MagicMock()
    item.behaviors.throwable = True

    item.validate_monster.return_value = False

    assert menu._validate_item(item) is False


def test_enqueue_item_from_menu(menu):
    item = MagicMock()
    monster = MagicMock()

    menu_item = MagicMock()
    menu_item.game_object = monster

    menu._enqueue_item = MagicMock()

    menu._enqueue_item_from_menu(
        item,
        menu_item,
    )

    menu._enqueue_item.assert_called_once_with(
        item,
        monster,
    )


def test_enqueue_technique_from_menu(menu):
    technique = MagicMock()
    monster = MagicMock()

    menu_item = MagicMock()
    menu_item.game_object = monster

    menu._enqueue_technique = MagicMock()

    menu._enqueue_technique_from_menu(
        technique,
        menu_item,
    )

    menu._enqueue_technique.assert_called_once_with(
        technique,
        monster,
    )


def test_choose_technique_target_self(menu):
    technique = MagicMock()
    technique.targets_enemy.return_value = False
    technique.target = {"own_monster": True}

    menu_item = MagicMock()
    menu_item.game_object = technique

    menu._enqueue_technique = MagicMock()

    menu._choose_technique_target(menu_item)

    menu._enqueue_technique.assert_called_once_with(
        technique,
        menu.monster,
    )


def test_choose_technique_target_enemy(menu):
    technique = MagicMock()
    technique.targets_enemy.return_value = False
    technique.target = {"own_monster": False}

    enemy = MagicMock()
    menu.opponents = [enemy]

    menu_item = MagicMock()
    menu_item.game_object = technique

    menu._enqueue_technique = MagicMock()

    menu._choose_technique_target(menu_item)

    menu._enqueue_technique.assert_called_once_with(
        technique,
        enemy,
    )


def test_hide_technique_preview(menu):
    menu.preview_overlay.clear = MagicMock()

    menu._hide_technique_preview()

    menu.preview_overlay.clear.assert_called_once()

    menu.event_bus.publish.assert_called_once_with(
        "combat_dialog",
        message=menu._combat_prompt(),
        dialog_speed="max",
    )


def test_show_technique_preview(menu):
    menu_obj = MagicMock()

    technique = MagicMock()

    item = MagicMock()
    item.game_object = technique

    menu_obj.get_selected_item.return_value = item

    menu._show_technique_preview(menu_obj)

    menu.event_bus.publish.assert_called_once_with(
        "combat_dialog",
        message="",
        dialog_speed="max",
    )

    menu.preview_overlay.show.assert_called_once_with(
        technique,
    )
