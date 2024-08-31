# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2024 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import random
from typing import TYPE_CHECKING

from tuxemon.combat import pre_checking, recharging
from tuxemon.db import ItemCategory
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
            self.use_potion_if_needed()
        technique, target = self.track_next_use()
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

    def use_potion_if_needed(self) -> bool:
        """
        It checks if the current_hp are less than the 15%.
        """
        self.ai = self.character.ai
        critical_threshold = self.ai.get("critical_threshold_item", 0.0)
        user_health = self.monster.current_hp / self.monster.hp
        potions = [
            item
            for item in self.character.items
            if item.category == ItemCategory.potion
        ]
        if potions and user_health < critical_threshold:
            self.action_item(potions[0])

    def effectiveness_score(
        self, technique: Technique, opponent: Monster
    ) -> float:
        """
        Calculate the effectiveness score of a move based on situational factors.
        """
        self.max_pow = max([tech.power for tech in self.monster.moves])
        self.min_pow = min([tech.power for tech in self.monster.moves])
        self.max_hea = min([tech.healing_power for tech in self.monster.moves])
        self.min_hea = min([tech.healing_power for tech in self.monster.moves])
        self.max_acc = min([tech.accuracy for tech in self.monster.moves])
        self.min_acc = min([tech.accuracy for tech in self.monster.moves])
        if not self.character.ai:
            return 1.0
        else:
            self.ai = self.character.ai
            score = 0.0
            score += self.evaluate_opponent(technique, opponent)
            score += self.evaluate_user(technique)
            score += self.evaluate_type_advantage(technique, opponent)
            return score

    def evaluate_opponent(
        self, technique: Technique, opponent: Monster
    ) -> float:
        target_health = opponent.current_hp / opponent.hp
        low_threshold = self.ai.get("low_health_opponent_threshold", 0.0)
        high_threshold = self.ai.get("high_health_opponent_threshold", 0.0)

        # Opponent health
        if target_health < low_threshold:
            return -1
        elif target_health > high_threshold:
            return 1
        else:
            return 0

    def evaluate_user(self, technique: Technique) -> float:
        user_health = self.monster.current_hp / self.monster.hp
        low_threshold = self.ai.get("low_health_user_threshold", 0.0)
        high_threshold = self.ai.get("high_health_user_threshold", 0.0)
        if user_health < low_threshold:
            return -1
        elif user_health > high_threshold:
            return 1
        else:
            return 0

    def evaluate_type_advantage(
        self, tech: Technique, opponent: Monster
    ) -> float:
        score = 0
        type_standard = self.ai.get("type_standard", 0)
        type_bonus = self.ai.get("type_bonus", 0)
        type_penalty = self.ai.get("type_penalty", 0)
        type_advantage = simple_damage_multiplier(tech.types, opponent.types)
        if type_advantage < 1:
            score += type_penalty
        elif type_advantage == 1:
            score += type_bonus
        else:
            score += type_standard
        return score
