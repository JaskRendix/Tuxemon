# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2024 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import uuid
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Optional

from tuxemon.db import MissionStatus, db
from tuxemon.locale import T

if TYPE_CHECKING:
    from tuxemon.npc import NPC

SIMPLE_PERSISTANCE_ATTRIBUTES = ("slug", "status", "enabled")


class Mission:
    """
    Tuxemon mission.
    """

    def __init__(self, save_data: Optional[Mapping[str, Any]] = None) -> None:
        save_data = save_data or {}

        self.slug: str = ""
        self.name: str = ""
        self.description: str = ""
        self.status: MissionStatus = MissionStatus.pending
        self.reqs: Sequence[str] = []
        self.failure_reqs: Sequence[str] = []
        self.success_reqs: Sequence[str] = []
        self.enabled = True

        self.set_state(save_data)

    def load(self, slug: str) -> None:
        """
        Loads and sets mission from the db.

        """
        try:
            results = db.lookup(slug, table="mission")
        except KeyError:
            raise RuntimeError(f"Mission {slug} not found")

        self.instance_id = uuid.uuid4()
        self.slug = results.slug
        self.name = T.translate(results.slug)
        self.status = self.status
        self.reqs = results.reqs
        self.failure_reqs = results.failure_reqs
        self.success_reqs = results.success_reqs
        self.dependencies = results.dependencies
        self.enabled = self.enabled

        combined = [*self.reqs, *self.failure_reqs, *self.success_reqs]
        _combined = unique_variables_across_sequences(combined)
        if _combined is not None:
            raise ValueError(
                f"The variable '{_combined}' appears in multiple sequences."
            )
        dependencies = [*self.dependencies, self.slug]
        _dependencies = unique_variables_across_sequences(dependencies)
        if _dependencies is not None:
            raise ValueError(
                f"The slug '{_dependencies}' appears in the dependencies sequence."
            )

    def get_state(self) -> Mapping[str, Any]:
        """
        Prepares a dictionary of the mission to be saved to a file.

        """
        save_data = {
            attr: getattr(self, attr)
            for attr in SIMPLE_PERSISTANCE_ATTRIBUTES
            if getattr(self, attr)
        }

        save_data["instance_id"] = str(self.instance_id.hex)

        return save_data

    def set_state(self, save_data: Mapping[str, Any]) -> None:
        """
        Loads information from saved data.

        """
        if not save_data:
            return

        self.load(save_data["slug"])

        for key, value in save_data.items():
            if key == "instance_id" and value:
                self.instance_id = uuid.UUID(value)
            elif key in SIMPLE_PERSISTANCE_ATTRIBUTES:
                setattr(self, key, value)

    def add_mission(self, character: NPC) -> None:
        """
        Adds a mission to the npc's missions.

        """
        character.missions.append(self)

    def completed_mission(self) -> None:
        """
        Sets completed status.

        """
        self.status = MissionStatus.completed

    def failed_mission(self) -> None:
        """
        Sets failed status.

        """
        self.status = MissionStatus.failed

    def accept_mission(self) -> None:
        """
        Sets accepted status.

        """
        self.status = MissionStatus.accepted

    def refuse_mission(self) -> None:
        """
        Sets refused status.

        """
        self.status = MissionStatus.refused


def has_mission(character: NPC, slug: str) -> bool:
    """
    Has a mission in the npc's missions.
    """
    return any(mission.slug == slug for mission in character.missions)


def find_mission(character: NPC, slug: str) -> Optional[Mission]:
    """
    Finds a mission in the npc's missions.
    """
    for mission in character.missions:
        if mission.slug == slug:
            return mission
    return None


def check_reqs(missions: Sequence[str], character: NPC) -> bool:
    """
    Checks if all the requisites are met.
    """
    if missions:
        for element in missions:
            part = element.split(":")
            if (
                part[0] in character.game_variables
                and character.game_variables[part[0]] == part[1]
            ):
                return True
    return False


def unique_variables_across_sequences(
    sequences: Sequence[str],
) -> Optional[str]:
    sequence_variables: dict[str, int] = {}
    for sequence in sequences:
        variables = sequence.split(",")
        for variable in variables:
            variable = variable.strip()
            sequence_variables[variable] = (
                sequence_variables.get(variable, 0) + 1
            )

    for variable, count in sequence_variables.items():
        if count > 1:
            return variable
    return None


def decode_mission(
    json_data: Optional[Sequence[Mapping[str, Any]]],
) -> list[Mission]:
    return [Mission(save_data=mission) for mission in json_data or {}]


def encode_mission(missions: Sequence[Mission]) -> Sequence[Mapping[str, Any]]:
    return [mission.get_state() for mission in missions]
