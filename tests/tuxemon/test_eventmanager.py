# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
import unittest
from typing import NamedTuple
from unittest.mock import MagicMock

from tuxemon.event.event_manager import EventManager


class TestEventManager(unittest.TestCase):

    class MockEvent(NamedTuple):
        data: str

    def test_init(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        self.assertEqual(event_manager._listeners, {})

    def test_subscribe(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        listener = MagicMock()
        event_manager.subscribe(TestEventManager.MockEvent, listener)
        self.assertIn(TestEventManager.MockEvent, event_manager._listeners)
        self.assertIn(
            listener, event_manager._listeners[TestEventManager.MockEvent]
        )

    def test_subscribe_same_event_type(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        listener1 = MagicMock()
        listener2 = MagicMock()
        event_manager.subscribe(TestEventManager.MockEvent, listener1)
        event_manager.subscribe(TestEventManager.MockEvent, listener2)
        self.assertEqual(
            len(event_manager._listeners[TestEventManager.MockEvent]), 2
        )

    def test_unsubscribe(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        listener = MagicMock()
        event_manager.subscribe(TestEventManager.MockEvent, listener)
        event_manager.unsubscribe(TestEventManager.MockEvent, listener)
        self.assertEqual(
            event_manager._listeners[TestEventManager.MockEvent], []
        )

    def test_unsubscribe_non_existent_listener(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        listener = MagicMock()
        event_manager.subscribe(TestEventManager.MockEvent, listener)
        event_manager.unsubscribe(TestEventManager.MockEvent, MagicMock())
        self.assertIn(
            listener, event_manager._listeners[TestEventManager.MockEvent]
        )

    def test_unsubscribe_non_existent_event_type(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        listener = MagicMock()
        event_manager.unsubscribe(TestEventManager.MockEvent, listener)
        self.assertEqual(event_manager._listeners, {})

    def test_emit(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        listener = MagicMock()
        event_manager.subscribe(TestEventManager.MockEvent, listener)
        event_manager.emit(TestEventManager.MockEvent(data="test"))
        listener.assert_called_once_with(
            TestEventManager.MockEvent(data="test")
        )

    def test_emit_with_data(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        listener = MagicMock()
        event_manager.subscribe(TestEventManager.MockEvent, listener)
        event_manager.emit(TestEventManager.MockEvent(data="data"))
        listener.assert_called_once_with(
            TestEventManager.MockEvent(data="data")
        )

    def test_emit_non_existent_event_type(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        # No error should occur, but no listener should be called.
        event_manager.emit(TestEventManager.MockEvent(data="test"))

    def test_get_listeners(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        listener1 = MagicMock()
        listener2 = MagicMock()
        event_manager.subscribe(TestEventManager.MockEvent, listener1)
        event_manager.subscribe(TestEventManager.MockEvent, listener2)
        listeners = event_manager.get_listeners(TestEventManager.MockEvent)
        self.assertIn(listener1, listeners)
        self.assertIn(listener2, listeners)

    def test_get_listeners_non_existent_event_type(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        listeners = event_manager.get_listeners(TestEventManager.MockEvent)
        self.assertEqual(listeners, [])

    def test_clear_listeners(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        listener = MagicMock()
        event_manager.subscribe(TestEventManager.MockEvent, listener)
        event_manager.clear_listeners(TestEventManager.MockEvent)
        self.assertEqual(
            event_manager._listeners[TestEventManager.MockEvent], []
        )

    def test_clear_listeners_non_existent_event_type(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        event_manager.clear_listeners(TestEventManager.MockEvent)
        self.assertEqual(event_manager._listeners, {})

    def test_clear_all_listeners(self):
        event_manager: EventManager[TestEventManager.MockEvent] = (
            EventManager()
        )
        listener1 = MagicMock()
        listener2 = MagicMock()
        event_manager.subscribe(TestEventManager.MockEvent, listener1)
        event_manager.subscribe(TestEventManager.MockEvent, listener2)
        event_manager.clear_listeners()
        self.assertEqual(event_manager._listeners, {})
