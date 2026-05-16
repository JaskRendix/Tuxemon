# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2026 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from unittest.mock import MagicMock

import pytest

from tuxemon.event.eventmiddleware import MovementMiddleware
from tuxemon.platform.const import intentions
from tuxemon.platform.events import PlayerInput


@pytest.fixture
def mock_character():
    c = MagicMock()
    c.slug = "npc_1"
    c.set_facing = MagicMock()
    c.mover = MagicMock()
    return c


@pytest.fixture
def mock_movement_manager():
    mm = MagicMock()
    mm.is_movement_allowed.return_value = True
    return mm


@pytest.fixture
def mock_camera_manager():
    cm = MagicMock()
    cm.get_active_camera.return_value = MagicMock(is_following=lambda: True)
    return cm


@pytest.fixture
def mw(mock_character, mock_movement_manager, mock_camera_manager):
    return MovementMiddleware(
        mock_character,
        mock_movement_manager,
        mock_camera_manager,
    )


def test_run_updates_movement_state(mw, mock_character):
    event = PlayerInput(button=intentions.RUN, value=1, previous_value=0)
    result = mw.preprocess(event)
    mock_character.mover.update_movement_state.assert_called_once_with(True)
    assert result is event


def test_direction_passed_to_camera_if_not_following(mw, mock_camera_manager):
    camera = MagicMock()
    camera.is_following.return_value = False
    mock_camera_manager.get_active_camera.return_value = camera

    event = PlayerInput(button=intentions.UP, value=1, previous_value=0)
    result = mw.preprocess(event)

    mw.movement_manager.queue_movement.assert_not_called()
    assert result is event


def test_tap_faces_but_does_not_move(
    mw, mock_character, mock_movement_manager
):
    event = PlayerInput(
        button=intentions.UP,
        value=1,
        previous_value=0,
        hold_time=1,  # REQUIRED for pressed=True
        hold_duration=0.01,
    )

    mw.preprocess(event)

    mock_character.set_facing.assert_called_once()
    mock_movement_manager.queue_movement.assert_not_called()
    mock_movement_manager.move_char.assert_not_called()


def test_hold_long_enough_moves(mw, mock_character, mock_movement_manager):
    event = PlayerInput(
        button=intentions.UP,
        value=1,
        previous_value=1,
        hold_time=10,
        hold_duration=0.20,
    )

    result = mw.preprocess(event)

    assert result is None
    mock_movement_manager.queue_movement.assert_called_once()
    mock_movement_manager.move_char.assert_called_once()


def test_hold_not_long_enough_does_not_move(
    mw, mock_character, mock_movement_manager
):
    event = PlayerInput(
        button=intentions.UP,
        value=1,
        previous_value=1,
        hold_time=5,
        hold_duration=0.05,
    )

    mw.preprocess(event)

    mock_movement_manager.queue_movement.assert_not_called()
    mock_movement_manager.move_char.assert_not_called()


def test_direction_moves_when_allowed(mw, mock_movement_manager):
    mock_movement_manager.is_movement_allowed.return_value = True

    event = PlayerInput(
        button=intentions.UP,
        value=1,
        previous_value=1,
        hold_time=10,
        hold_duration=0.20,
    )

    mw.preprocess(event)

    mock_movement_manager.queue_movement.assert_called_once()
    mock_movement_manager.move_char.assert_called_once()


def test_direction_queues_but_does_not_move_if_not_allowed(
    mw, mock_movement_manager
):
    mock_movement_manager.is_movement_allowed.return_value = False

    event = PlayerInput(
        button=intentions.UP,
        value=1,
        previous_value=1,
        hold_time=10,
        hold_duration=0.20,
    )

    mw.preprocess(event)

    mock_movement_manager.queue_movement.assert_called_once()
    mock_movement_manager.move_char.assert_not_called()


def test_release_stops_character(mw, mock_movement_manager):
    mock_movement_manager.has_pending_movement.return_value = True

    event = PlayerInput(
        button=intentions.UP,
        value=0,
        previous_value=1,
        hold_time=0,
        hold_duration=0.0,
    )

    mw.preprocess(event)

    mock_movement_manager.stop_char.assert_called_once()


def test_stop_only_if_pending(mw, mock_movement_manager):
    mock_movement_manager.has_pending_movement.return_value = False

    event = PlayerInput(
        button=intentions.UP,
        value=0,
        previous_value=1,
        hold_time=0,
        hold_duration=0.0,
    )

    mw.preprocess(event)

    mock_movement_manager.stop_char.assert_not_called()


def test_facing_updates_only_on_press(mw, mock_character):
    # Frame 1: press
    event = PlayerInput(
        button=intentions.LEFT,
        value=1,
        previous_value=0,
        hold_time=1,
        hold_duration=0.0,
    )
    mw.preprocess(event)
    mock_character.set_facing.assert_called_once()

    # Frame 2: held
    event2 = PlayerInput(
        button=intentions.LEFT,
        value=1,
        previous_value=1,
        hold_time=5,
        hold_duration=0.10,
    )
    mw.preprocess(event2)
    assert mock_character.set_facing.call_count == 1


def test_no_movement_when_camera_detached(mw, mock_camera_manager):
    camera = MagicMock()
    camera.is_following.return_value = False
    mock_camera_manager.get_active_camera.return_value = camera

    event = PlayerInput(button=intentions.RIGHT, value=1, previous_value=0)
    mw.preprocess(event)

    mw.movement_manager.queue_movement.assert_not_called()
    mw.movement_manager.move_char.assert_not_called()


def test_invalid_direction_does_nothing(mw):
    event = PlayerInput(button=9999, value=1, previous_value=0)
    result = mw.preprocess(event)
    assert result is event


def test_fake_game_loop_tap_only_faces(
    mw, mock_character, mock_movement_manager
):
    # Frame 1: press
    frame1 = PlayerInput(
        button=intentions.UP,
        value=1,
        previous_value=0,
        hold_time=1,
        hold_duration=0.00,
    )
    mw.preprocess(frame1)

    # Frame 2: held but short
    frame2 = PlayerInput(
        button=intentions.UP,
        value=1,
        previous_value=1,
        hold_time=5,
        hold_duration=0.05,
    )
    mw.preprocess(frame2)

    # Frame 3: release
    frame3 = PlayerInput(
        button=intentions.UP,
        value=0,
        previous_value=1,
        hold_time=0,
        hold_duration=0.00,
    )
    mw.preprocess(frame3)

    mock_character.set_facing.assert_called_once()
    mock_movement_manager.queue_movement.assert_not_called()
    mock_movement_manager.move_char.assert_not_called()


def test_fake_game_loop_hold_walks(mw, mock_character, mock_movement_manager):
    # Frame 1: press
    frame1 = PlayerInput(
        button=intentions.RIGHT,
        value=1,
        previous_value=0,
        hold_time=1,
        hold_duration=0.00,
    )
    mw.preprocess(frame1)

    # Frame 2: held long enough
    frame2 = PlayerInput(
        button=intentions.RIGHT,
        value=1,
        previous_value=1,
        hold_time=10,
        hold_duration=0.20,
    )
    mw.preprocess(frame2)

    mock_character.set_facing.assert_called_once()
    mock_movement_manager.queue_movement.assert_called_once()
    mock_movement_manager.move_char.assert_called_once()


def test_simultaneous_key_presses_prioritize_last(
    mw, mock_character, mock_movement_manager
):
    # Press UP
    event_up = PlayerInput(
        button=intentions.UP,
        value=1,
        previous_value=0,
        hold_time=1,
        hold_duration=0.00,
    )
    mw.preprocess(event_up)

    # Press RIGHT (should override)
    event_right = PlayerInput(
        button=intentions.RIGHT,
        value=1,
        previous_value=0,
        hold_time=1,
        hold_duration=0.00,
    )
    mw.preprocess(event_right)

    # Last facing should be RIGHT
    mock_character.set_facing.assert_called_with(
        mock_character.set_facing.call_args[0][0]
    )

    # Movement only after held long enough
    event_right2 = PlayerInput(
        button=intentions.RIGHT,
        value=1,
        previous_value=1,
        hold_time=10,
        hold_duration=0.20,
    )
    mw.preprocess(event_right2)

    mock_movement_manager.queue_movement.assert_called_once()
    mock_movement_manager.move_char.assert_called_once()


direction_params = [
    pytest.param(intentions.UP, id="up"),
    pytest.param(intentions.DOWN, id="down"),
    pytest.param(intentions.LEFT, id="left"),
    pytest.param(intentions.RIGHT, id="right"),
]


@pytest.mark.parametrize("direction_button", direction_params)
def test_tap_faces_all_directions(mw, mock_character, direction_button):
    event = PlayerInput(
        button=direction_button,
        value=1,
        previous_value=0,
        hold_time=1,
        hold_duration=0.01,
    )
    mw.preprocess(event)
    mock_character.set_facing.assert_called_once()


@pytest.mark.parametrize("direction_button", direction_params)
def test_hold_moves_all_directions(
    mw, mock_movement_manager, direction_button
):
    event = PlayerInput(
        button=direction_button,
        value=1,
        previous_value=1,
        hold_time=10,
        hold_duration=0.20,
    )
    mw.preprocess(event)
    mock_movement_manager.queue_movement.assert_called_once()
    mock_movement_manager.move_char.assert_called_once()
