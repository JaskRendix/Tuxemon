# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2024 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import random
from typing import TYPE_CHECKING, Optional

from tuxemon.combat import pre_checking, recharging
from tuxemon.db import ItemCategory, NpcAIModel
from tuxemon.formula import simple_damage_multiplier
from tuxemon.technique.technique import Technique

if TYPE_CHECKING:
    from tuxemon.item.item import Item
    from tuxemon.monster import Monster
    from tuxemon.npc import NPC
    from tuxemon.states.combat.combat import CombatState


# Class definition for an AI model.
class AI:
    def __init__(
        self, combat: CombatState, monster: Monster, character: NPC
    ) -> None:
        super().__init__()
        self.combat = combat
        self.character = character
        self.monster = monster
        if character == combat.players[0]:
            self.opponents = combat.monsters_in_play[combat.players[1]]
        if character == combat.players[1]:
            self.opponents = combat.monsters_in_play[combat.players[0]]

        if self.combat.is_trainer_battle:
            self.make_decision_trainer()
        else:
            self.make_decision_wild()

    def make_decision_trainer(self) -> None:
        """
        Trainer battles.
        """
        if self.character.ai or self.character.items:
            itm = self.use_potion_if_needed()
            if itm:
                self.action_item(itm)
        technique, target = self.track_next_use()
        # send data
        self.action_tech(technique, target)

    def make_decision_wild(self) -> None:
        """
        Wild encounters.
        """
        technique, target = self.track_next_use()
        # send data
        self.action_tech(technique, target)

    def track_next_use(self) -> tuple[Technique, Monster]:
        """
        Tracks next_use and recharge, if both unusable, skip.
        """
        # Filter out recharging moves and validate techniques against opponents
        valid_actions = {
            (mov, opponent): self.effectiveness_score(mov, opponent)
            for mov in self.monster.moves[-self.monster.max_moves :]
            if not recharging(mov)
            for opponent in self.opponents
            if mov.validate(opponent)
        }
        for tech, number in valid_actions.items():
            print(tech[0].name, tech[1].name, number)

        # If no valid actions, return a skip technique and a random opponent
        if not valid_actions:
            skip = Technique()
            skip.load("skip")
            return skip, random.choice(self.opponents)

        # Otherwise, return a random valid action
        return random.choices(
            list(valid_actions.keys()), weights=list(valid_actions.values())
        )[0]

    def need_potion(self) -> bool:
        """
        It checks if the current_hp are less than the 15%.
        """
        if self.monster.current_hp > 1 and self.monster.current_hp <= round(
            self.monster.hp * 0.15
        ):
            return True
        else:
            return False

    def action_tech(self, technique: Technique, target: Monster) -> None:
        """
        Send action tech.
        """
        self.character.game_variables["action_tech"] = technique.slug
        technique = pre_checking(self.monster, technique, target, self.combat)
        self.combat.enqueue_action(self.monster, technique, target)

    def action_item(self, item: Item) -> None:
        """
        Send action item.
        """
        self.combat.enqueue_action(self.character, item, self.monster)

    def use_potion_if_needed(self) -> Optional[Item]:
        """
        It checks if the current_hp are less than the 15%.
        """
        threshold = self.character.ai.get("critical_threshold_item", 0.0)
        health = self.monster.current_hp / self.monster.hp
        potions = [
            item
            for item in self.character.items
            if item.category == ItemCategory.potion
        ]
        if potions and health < threshold:
            return potions[0]
        else:
            return None

    def effectiveness_score(
        self, technique: Technique, opponent: Monster
    ) -> float:
        """Calculate the effectiveness score of a move based on situational factors."""
        score = 1.0
        if not self.character.ai:
            return score
        else:
            score += evaluate_monster(opponent, self.character.ai)
            score *= evaluate_type_advantage(technique, opponent)
            return score


def evaluate_type_advantage(tech: Technique, opponent: Monster) -> float:
    type_advantage = simple_damage_multiplier(tech.types, opponent.types)
    return type_advantage


def evaluate_monster(monster: Monster, ai: NpcAIModel) -> float:
    target_health = monster.current_hp / monster.hp
    low_threshold = ai.low_health_opponent_threshold
    high_threshold = ai.high_health_opponent_threshold

    low_threshold = ai.low_health_user_threshold
    high_threshold = ai.high_health_user_threshold

    if target_health < low_threshold:
        return -1
    elif target_health > high_threshold:
        return 1
    else:
        return 0
