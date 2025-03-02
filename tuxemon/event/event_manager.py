# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, Generic, Optional, TypeVar

logger = logging.getLogger(__name__)


class BaseEvent:
    pass


# Define your specific events
# class Examplevent(BaseEvent):
#    example: str

T = TypeVar("T", bound=BaseEvent)


class EventManager(Generic[T]):
    """A general-purpose event manager for publishing and subscribing to events."""

    def __init__(self) -> None:
        """Initializes the event manager."""
        self._listeners: dict[type[T], list[Callable[[T], None]]] = {}

    def subscribe(
        self, event_type: type[T], listener: Callable[[T], None]
    ) -> None:
        """
        Subscribes a listener to an event type.

        Parameters:
            event_type: The type of event to subscribe to.
            listener: The function to call when the event is emitted.
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)
        logger.debug(f"Listener subscribed to event: {event_type}")

    def unsubscribe(
        self, event_type: type[T], listener: Callable[[Any], None]
    ) -> None:
        """
        Unsubscribes a listener from an event type.

        Parameters:
            event_type: The type of event to unsubscribe from.
            listener: The function to unsubscribe.
        """
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(listener)
                logger.debug(f"Listener unsubscribed from event: {event_type}")
            except ValueError:
                logger.warning(f"Listener not found for event: {event_type}")

    def emit(self, event_data: T) -> None:
        """
        Emits an event, calling all subscribed listeners.

        Parameters:
            event_type: The type of event to emit.
            event_data: Optional data to pass to the listeners.
        """
        event_type = type(event_data)
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                try:
                    listener(event_data)
                except Exception as e:
                    logger.error(
                        f"Error calling listener for event {event_type}: {e}"
                    )
        else:
            logger.debug(f"No listeners for event: {event_type}")

    def get_listeners(
        self, event_type: type[T]
    ) -> list[Callable[[Any], None]]:
        """
        Returns a list of listeners for a given event type.

        Parameters:
            event_type: The type of event.

        Returns:
            A list of listener functions.
        """
        return self._listeners.get(event_type, [])

    def clear_listeners(self, event_type: Optional[type[T]] = None) -> None:
        """
        Clears all listeners for a specific event type, or all listeners if no type is provided.

        Parameters:
            event_type: The type of event to clear listeners for. If None, clears all listeners.
        """
        if event_type:
            if event_type in self._listeners:
                self._listeners[event_type].clear()
                logger.debug(f"Cleared listeners for event: {event_type}")
        else:
            self._listeners.clear()
            logger.debug("Cleared all listeners.")
