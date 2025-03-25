# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

logger = logging.getLogger(__name__)

from tuxemon import prepare

if TYPE_CHECKING:
    from tuxemon.npc import NPCState


@dataclass
class Location:
    name: str
    x: float
    y: float
    visited: bool = False
    visible: bool = True

    def get_state(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "visited": self.visited,
            "visible": self.visible,
        }


class TrackingData:
    def __init__(self, image_map: str = prepare.BG_PHONE_MAP) -> None:
        self.image_map = image_map
        self.locations: dict[str, Location] = {}

    def add_location(self, location_id: str, location: Location) -> None:
        if location_id in self.locations:
            logger.error(f"Location ID '{location_id}' already exists.")
        else:
            self.locations[location_id] = location

    def save(self) -> Mapping[str, Any]:
        return encode_tracking(self.locations)

    def load(self, save_data: NPCState) -> None:
        self.locations = decode_tracking(save_data["tracking"])


class Tracking:
    def __init__(self) -> None:
        self.maps: dict[str, TrackingData] = {}

    def add_map(self, map_id: str, map_data: TrackingData) -> None:
        self.maps[map_id] = map_data

    def get_map_data(self, map_id: str) -> Optional[TrackingData]:
        return self.maps.get(map_id)


def decode_tracking(json_data: Mapping[str, Any]) -> dict[str, Location]:
    tracking_data: dict[str, Location] = {}
    if json_data:
        tracking_data = {
            key: Location(**value)
            for key, value in json_data.get("tracking", {}).items()
        }
    return tracking_data


def encode_tracking(tracking_data: dict[str, Location]) -> Mapping[str, Any]:
    return {
        "tracking": {
            location: data.get_state()
            for location, data in tracking_data.items()
        }
    }
