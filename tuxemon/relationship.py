# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from tuxemon.npc import NPC
logger = logging.getLogger(__name__)

RELATIONSHIP_STRENGTH: tuple[int, int] = (0, 100)


@dataclass
class Connection:
    relationship_type: str
    strength: int = 50
    steps: float = 0
    decay_rate: float = 0.01  # Strength lost per threshold
    decay_threshold: int = 500  # Steps before decay applies

    def update_steps(self, npc: NPC) -> None:
        self.steps = npc.steps

    def apply_decay(self, npc: NPC) -> None:
        steps_since_last = npc.steps - self.steps
        if steps_since_last >= self.decay_threshold:
            decay_amount = (
                steps_since_last // self.decay_threshold
            ) * self.decay_rate
            self.strength = max(
                RELATIONSHIP_STRENGTH[0],
                min(
                    self.strength - round(decay_amount),
                    RELATIONSHIP_STRENGTH[1],
                ),
            )
            self.steps = npc.steps - (steps_since_last % self.decay_threshold)

    def get_state(self) -> dict[str, Any]:
        """
        Returns a dictionary representing the state of the connection,
        including its status and appearance count.

        Returns:
            A dictionary representing the state of the connection.
        """
        return {
            "relationship_type": self.relationship_type,
            "strength": self.strength,
            "steps": self.steps,
            "decay_rate": self.decay_rate,
            "decay_threshold": self.decay_threshold,
        }


class Relationships:
    def __init__(self) -> None:
        self.connections: dict[str, Connection] = {}

    def add_connection(
        self,
        slug: str,
        relationship_type: str,
        strength: int,
        steps: float,
        decay_rate: float,
        decay_threshold: int,
    ) -> None:
        """
        Adds a new connection.
        """
        new_connection = Connection(
            relationship_type=relationship_type,
            strength=strength,
            steps=steps,
            decay_rate=decay_rate,
            decay_threshold=decay_threshold,
        )
        self.connections[slug] = new_connection

    def remove_connection(self, slug: str) -> None:
        """
        Removes a connection by slug.
        """
        if slug in self.connections:
            del self.connections[slug]

    def update_connection_strength(self, slug: str, new_strength: int) -> None:
        """
        Updates the strength of an existing connection.
        """
        if slug in self.connections:
            strength = max(0, min(new_strength, 100))
            self.connections[slug].strength = strength

    def get_connection(self, slug: str) -> Optional[Connection]:
        """
        Retrieves a connection by slug.
        """
        return self.connections.get(slug)

    def get_all_connections(self) -> dict[str, Connection]:
        """
        Returns all connections.
        """
        return self.connections

    def update_connection_decay_rate(
        self, slug: str, new_decay_rate: float
    ) -> None:
        """
        Updates the decay rate of an existing connection.
        """
        if slug in self.connections:
            decay_rate = max(0.0, min(new_decay_rate, 1.0))
            self.connections[slug].decay_rate = decay_rate

    def update_connection_decay_threshold(
        self, slug: str, new_decay_threshold: int
    ) -> None:
        """
        Updates the decay threshold of an existing connection.
        """
        if slug in self.connections:
            self.connections[slug].decay_threshold = new_decay_threshold


def encode_relationships(relationships: Relationships) -> Mapping[str, Any]:
    """Encodes a Relationships object to a dictionary."""
    return {
        slug: entry.get_state()
        for slug, entry in relationships.connections.items()
    }


def decode_relationships(json_data: Mapping[str, Any]) -> Relationships:
    """Decodes a dictionary to a Relationships object."""
    relationships = Relationships()
    if json_data:
        for slug, entry_data in json_data.items():
            connection = Connection(**entry_data)
            relationships.connections[slug] = connection
    return relationships
