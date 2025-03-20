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


@dataclass
class Connection:
    relationship_type: str
    strength: int
    last_interaction: float  # Steps
    decay_rate: float  # Strength lost per threshold
    decay_threshold: int  # Steps before decay applies

    def update_last_interaction(self, npc: NPC) -> None:
        self.last_interaction = npc.steps

    def apply_decay(self, npc: NPC) -> None:
        steps_since_last = npc.steps - self.last_interaction
        if steps_since_last >= self.decay_threshold:
            decay_amount = (
                steps_since_last // self.decay_threshold
            ) * self.decay_rate
            self.strength = max(0, self.strength - round(decay_amount))
            self.last_interaction = npc.steps - (
                steps_since_last % self.decay_threshold
            )


class Relationships:
    def __init__(self) -> None:
        self.connections: dict[str, Connection] = {}

    def add_connection(
        self,
        slug: str,
        relationship_type: str,
        strength: int,
        last_interaction: float,
        decay_rate: float,
        decay_threshold: int,
    ) -> None:
        """
        Adds a new connection.
        """
        new_connection = Connection(
            relationship_type=relationship_type,
            strength=strength,
            last_interaction=last_interaction,
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
            self.connections[slug].strength = new_strength

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
            self.connections[slug].decay_rate = new_decay_rate

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
        slug: {
            "relationship_type": connection.relationship_type,
            "strength": connection.strength,
            "last_interaction": connection.last_interaction,
            "decay_rate": connection.decay_rate,
            "decay_threshold": connection.decay_threshold,
        }
        for slug, connection in relationships.connections.items()
    }


def decode_relationships(data: Mapping[str, Any]) -> Relationships:
    """Decodes a dictionary to a Relationships object."""
    relationships = Relationships()
    for slug, connection_data in data.items():
        relationships.add_connection(
            slug=connection_data["slug"],
            relationship_type=connection_data["relationship_type"],
            strength=connection_data["strength"],
            last_interaction=connection_data.get("last_interaction", 0),
            decay_rate=connection_data.get("decay_rate", 0.01),
            decay_threshold=connection_data.get("decay_threshold", 500),
        )
    return relationships
