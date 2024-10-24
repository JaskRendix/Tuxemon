# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2024 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from tuxemon import prepare
from tuxemon.monster import decode_monsters, encode_monsters
from tuxemon.states.pc_kennel import HIDDEN_LIST

if TYPE_CHECKING:
    from tuxemon.monster import Monster
    from tuxemon.npc import NPCState


class MonsterBoxes:
    def __init__(self) -> None:
        self.boxes: dict[str, list[Monster]] = {}

    def add_monster(self, box_id: str, monster: Monster) -> None:
        if box_id not in self.boxes:
            self.create_box(box_id)
        self.boxes[box_id].append(monster)

    def remove_monster(self, monster: Monster) -> None:
        for box in self.boxes.values():
            if monster in box:
                box.remove(monster)
                return

    def remove_monster_from(self, box_id: str, monster: Monster) -> None:
        if box_id in self.boxes:
            self.boxes[box_id].remove(monster)

    def get_monsters_by_iid(self, instance_id: uuid.UUID) -> Optional[Monster]:
        return next(
            (
                m
                for box in self.boxes.values()
                for m in box
                if m.instance_id == instance_id
            ),
            None,
        )

    def get_monsters(self, box_id: str) -> list[Monster]:
        return self.boxes.get(box_id, [])

    def has_box(self, box_id: str) -> bool:
        return box_id in self.boxes

    def get_box_ids(self) -> list[str]:
        return list(self.boxes.keys())

    def get_box_size(self, box_id: str) -> int:
        return len(self.get_monsters(box_id))

    def get_box_name(self, instance_id: uuid.UUID) -> Optional[str]:
        return next(
            (
                box
                for box, monsters in self.boxes.items()
                for m in monsters
                if m.instance_id == instance_id
            ),
            None,
        )

    def get_all_monsters(self) -> list[Monster]:
        return [monster for box in self.boxes.values() for monster in box]

    def get_all_monsters_hidden(self) -> list[Monster]:
        return [
            monster
            for key, box in self.boxes.items()
            if key in HIDDEN_LIST
            for monster in box
        ]

    def get_all_monsters_visible(self) -> list[Monster]:
        return [
            monster
            for key, box in self.boxes.items()
            if key not in HIDDEN_LIST
            for monster in box
        ]

    def is_box_full(
        self, box_id: str, max_capacity: int = prepare.MAX_KENNEL
    ) -> bool:
        return box_id in self.boxes and len(self.boxes[box_id]) >= max_capacity

    def move_monster(
        self, source_box_id: str, target_box_id: str, monster: Monster
    ) -> None:
        if (
            source_box_id in self.boxes
            and monster in self.boxes[source_box_id]
        ):
            self.remove_monster_from(source_box_id, monster)
            self.add_monster(target_box_id, monster)

    def move_monsters(self, source_box_id: str, target_box_id: str) -> None:
        if target_box_id not in self.boxes:
            self.create_box(target_box_id)
        monsters = self.get_monsters(source_box_id)
        for monster in monsters:
            self.add_monster(target_box_id, monster)
        self.boxes[source_box_id] = []

    def swap_monsters(
        self, box_id1: str, box_id2: str, monster1: Monster, monster2: Monster
    ) -> None:
        if (
            box_id1 in self.boxes
            and monster1 in self.boxes[box_id1]
            and box_id2 in self.boxes
            and monster2 in self.boxes[box_id2]
        ):
            self.remove_monster_from(box_id1, monster1)
            self.remove_monster_from(box_id2, monster2)
            self.add_monster(box_id1, monster2)
            self.add_monster(box_id2, monster1)

    def swap_with_external_monster(
        self, box_id: str, monster_in_box: Monster, external_monster: Monster
    ) -> Monster:
        if box_id in self.boxes:
            self.remove_monster_from(box_id, monster_in_box)
            self.add_monster(box_id, external_monster)
            return monster_in_box
        else:
            raise ValueError("Monster not found in box.")

    def swap_with_external_monster_by_iid(
        self, instance_id: uuid.UUID, external_monster: Monster
    ) -> Monster:
        monster = self.get_monsters_by_iid(instance_id)
        box_id = self.get_box_name(instance_id)
        if monster is not None and box_id is not None:
            return self.swap_with_external_monster(
                box_id, monster, external_monster
            )
        else:
            raise ValueError("Monster not found in box.")

    def create_box(self, box_id: str) -> None:
        self.boxes[box_id] = []

    def remove_box(self, box_id: str) -> None:
        if box_id in self.boxes:
            del self.boxes[box_id]

    def save(self, state: NPCState) -> None:
        state["monster_boxes"] = {}
        for box_id, monsters in self.boxes.items():
            state["monster_boxes"][box_id] = encode_monsters(monsters)

    def load(self, save_data: NPCState) -> None:
        self.boxes = {}
        for box_id, encoded_monsters in save_data["monster_boxes"].items():
            self.boxes[box_id] = decode_monsters(encoded_monsters)
