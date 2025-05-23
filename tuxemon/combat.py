# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
"""

Combat related code that can be independent of the combat state.

Code here might be shared by states, actions, conditions, etc.

"""

from __future__ import annotations

import logging
import random
from collections.abc import Generator, Sequence
from typing import TYPE_CHECKING, Optional

from tuxemon.db import (
    GenderType,
    OutputBattle,
    PlagueType,
    StatType,
    TargetType,
)
from tuxemon.locale import T
from tuxemon.technique.technique import Technique

if TYPE_CHECKING:
    from tuxemon.monster import Monster
    from tuxemon.npc import NPC
    from tuxemon.session import Session
    from tuxemon.states.combat.combat import CombatState


logger = logging.getLogger()


def check_battle_legal(character: NPC) -> bool:
    """
    Checks to see if the character has any monsters fit for battle.

    Parameters:
        character: Character object.

    Returns:
        Whether the character has monsters that can fight.

    """
    if not character.monsters:
        logger.error(f"Cannot start battle, {character.name} has no monsters!")
        return False
    else:
        if fainted_party(character.monsters):
            logger.error(
                f"Cannot start battle, {character.name}'s monsters are all DEAD."
            )
            return False
        else:
            if party_no_tech(character.monsters):
                no_tech = party_no_tech(character.monsters)
                logger.error(
                    f"Cannot start battle, {no_tech} has/have no techniques."
                )
                return False
            else:
                return True


def pre_checking(
    session: Session,
    monster: Monster,
    technique: Technique,
    target: Monster,
    combat: CombatState,
) -> Technique:
    """
    Pre checking allows to check if there are statuses
    or other conditions that change the chosen technique.
    """
    if monster.status:
        monster.status[0].combat_state = combat
        monster.status[0].phase = "pre_checking"
        result_status = monster.status[0].use(session, target)
        if result_status.techniques:
            technique = random.choice(result_status.techniques)

    infected_slugs = [
        slug
        for slug, plague in monster.plague.items()
        if plague == PlagueType.infected
    ]
    if infected_slugs and any(
        technique.target.get(target_type, False)
        for target_type in ["enemy_monster", "enemy_team", "enemy_trainer"]
    ):
        slug = random.choice(infected_slugs)
        method = Technique.create(slug)
        result_method = method.use(session, monster, target)
        if result_method.success:
            technique = method
    return technique


def has_status(monster: Monster, status_name: str) -> bool:
    """
    Checks to see if the monster has a specific status.
    """
    return any(t for t in monster.status if t.slug == status_name)


def has_effect(technique: Technique, effect_name: str) -> bool:
    """
    Checks to see if the technique has a specific effect (eg ram -> damage).
    """
    return any(t for t in technique.effects if t.name == effect_name)


def party_no_tech(party: list[Monster]) -> list[str]:
    """
    Return list of monsters without techniques.
    """
    return [p.name for p in party if not p.moves]


def has_effect_param(
    tech: Technique, effect_name: str, attribute: str, name: str
) -> bool:
    """
    Checks whether a specific effect contains the specified attribute with a
    matching value.

    Parameters:
        tech: The technique object containing a list of effects.
        effect_name: The name of the effect to look for (e.g., 'give').
        attribute: The attribute within the effect to check (e.g., 'condition'
            in the 'give' effect).
        name: The expected value of the attribute (e.g., 'diehard', which is
            assigned by the 'give' effect).

    Returns:
        bool: True if an effect with the given name and attribute value is
            found, otherwise False.
    """
    return any(
        ele.name == effect_name and getattr(ele, attribute, None) == name
        for ele in tech.effects
    )


def fainted(monster: Monster) -> bool:
    """
    Checks to see if the monster is fainted.
    """
    return has_status(monster, "faint") or monster.current_hp <= 0


def recharging(technique: Technique) -> bool:
    """
    Checks to see if a technique is recharging.
    """
    return technique.next_use > 0


def get_awake_monsters(
    character: NPC,
    monsters: list[Monster],
    turn: int,
    method: Optional[str] = None,
) -> Generator[Monster, None, None]:
    """
    Iterate all non-fainted monsters in party.

    Parameters:
        character: The character.
        monsters: List of monsters on the battlefield.
        turn: Current turn of the battle.
        method: Method to use when selecting a monster (default: None).

    Yields:
        Non-fainted monsters.

    """
    awake_monsters = [
        monster
        for monster in character.monsters
        if not fainted(monster) and monster not in monsters
    ]

    if awake_monsters:
        if len(awake_monsters) == 1:
            yield awake_monsters[0]
        else:
            if turn == 1 or method is None:
                yield from awake_monsters
            else:
                yield retrieve_from_party(awake_monsters, method)


def alive_party(character: NPC) -> list[Monster]:
    """
    Returns a list with all the monsters alive in the character's party.
    """
    return [monster for monster in character.monsters if not fainted(monster)]


def fainted_party(party: Sequence[Monster]) -> bool:
    """
    Whether the party is fainted or not.
    """
    return all(map(fainted, party))


def defeated(character: NPC) -> bool:
    """
    Whether all the character's party is fainted.
    """
    return fainted_party(character.monsters)


def get_target_monsters(
    targets: list[str], technique: Technique, user: Monster, target: Monster
) -> list[Monster]:
    """
    Retrieves a list of monsters based on the provided targets and combat state.

    Parameters:
        targets: A list of targets to retrieve monsters for (own_monster, etc.).
        technique: The technique object containing the combat state.
        user: The monster initiating the combat.
        target: The target monster in the combat.

    Returns:
        A list of monsters matching the provided targets.

    Raises:
        ValueError: If an objective is not a valid TargetType.
    """
    combat = technique.combat_state
    assert combat
    monsters = []
    for objective in targets:
        if objective not in list(TargetType):
            raise ValueError(f"{objective} isn't among {list(TargetType)}")
        monsters.extend(combat.get_targets_from_map(objective, user, target))
    return monsters


def battlefield(session: Session, monster: Monster) -> None:
    """
    Record the useful properties of the last monster fought.

    Parameters:
        session: Session
        monster: The monster on the ground.
        players: All the remaining players.

    """
    set_var(session, "battle_last_monster_name", monster.name)
    set_var(session, "battle_last_monster_level", str(monster.level))
    set_var(session, "battle_last_monster_type", monster.types[0].slug)
    set_var(session, "battle_last_monster_category", monster.category)
    set_var(session, "battle_last_monster_shape", monster.shape)


def track_battles(
    session: Session,
    output: str,
    player: NPC,
    players: Sequence[NPC],
    prize: int = 0,
    trainer_battle: bool = False,
) -> str:
    """
    Tracks battles, fills variables and returns the message.

    Parameters:
        session: Session
        output: Output of the battle: won, lost, draw
        player: The human player.
        players: All the players (eg if player is winner, players are losers)
        prize: Amount of money (prize) after fighting.
        trainer_battle: Whether a trainer or wild encounter.

    Returns:
        Message to display.
    """
    battle_outcomes = {
        "won": OutputBattle.won.value,
        "lost": OutputBattle.lost.value,
        "draw": OutputBattle.draw.value,
    }

    if output not in battle_outcomes:
        raise ValueError("Invalid battle output")

    if output == "won":
        return _handle_win(session, player, players, prize, trainer_battle)
    elif output == "lost":
        return _handle_loss(session, player, players, trainer_battle)
    else:
        return _handle_draw(session, player, players, trainer_battle)


def _handle_win(
    session: Session,
    winner: NPC,
    losers: Sequence[NPC],
    prize: int,
    trainer_battle: bool,
) -> str:
    """
    Handles the case where the human player won the battle.

    Parameters:
        session: Session
        winner: The human player.
        losers: All the players that lost.
        prize: Amount of money (prize) after fighting.
        trainer_battle: Whether a trainer or wild encounter.

    Returns:
        Message to display.
    """
    info = {"name": winner.name.upper()}

    if trainer_battle:
        for loser in losers:
            set_battle(session, OutputBattle.won, winner, loser)

        if winner.isplayer:
            set_var(session, "battle_last_result", OutputBattle.won.value)
            set_var(session, "battle_last_winner", "player")
            client = session.client.event_engine
            var = ["player", prize]
            client.execute_action("modify_money", var, True)

            if prize > 0:
                set_var(session, "battle_last_prize", str(prize))
                info["prize"] = str(prize)
                info["currency"] = "$"
                return T.format("combat_victory_trainer", info)
            else:
                return T.format("combat_victory", info)
        else:
            set_var(session, "battle_last_winner", winner.slug)
            set_var(session, "battle_last_trainer", winner.slug)
            return T.format("combat_victory", info)
    else:
        if winner.monsters[0].wild:
            info["name"] = winner.monsters[0].name.upper()
        return T.format("combat_victory", info)


def _handle_loss(
    session: Session,
    loser: NPC,
    winners: Sequence[NPC],
    trainer_battle: bool,
) -> str:
    """
    Handles the case where the human player lost the battle.

    Parameters:
        session: Session
        loser: The human player.
        winners: All the players that won.
        trainer_battle: Whether a trainer or wild encounter.

    Returns:
        Message to display.
    """
    info = {"name": loser.name.upper()}
    set_var(session, "teleport_clinic", OutputBattle.lost.value)

    if trainer_battle:
        if loser.isplayer:
            set_var(session, "battle_last_result", OutputBattle.lost.value)
            set_var(session, "battle_last_loser", "player")
        else:
            set_var(session, "battle_last_loser", loser.slug)
            set_var(session, "battle_last_trainer", loser.slug)

        for winner in winners:
            set_battle(session, OutputBattle.lost, loser, winner)
        return T.format("combat_defeat", info)
    return ""


def _handle_draw(
    session: Session,
    player: NPC,
    players: Sequence[NPC],
    trainer_battle: bool,
) -> str:
    """
    Handles the case where the battle was a draw.

    Parameters:
        session: Session
        player: The human player.
        players: All the players.
        trainer_battle: Whether a trainer or wild encounter.

    Returns:
        Message to display.
    """
    defeat = list(players)
    defeat.remove(player)
    set_var(session, "teleport_clinic", OutputBattle.draw.value)

    if trainer_battle:
        set_var(session, "battle_last_result", OutputBattle.draw.value)
        for player_defeated in defeat:
            set_var(session, "battle_last_trainer", player_defeated.slug)
            set_battle(session, OutputBattle.draw, player, player_defeated)
    return T.translate("combat_draw")


def set_var(session: Session, key: str, value: str) -> None:
    """
    Registers variable in game_variables.

    Parameters:
        session: Session
        key: The key game variable.
        value: The value game variable.

    """
    client = session.client.event_engine
    var = f"{key}:{value}"
    client.execute_action("set_variable", [var], True)


def set_battle(
    session: Session, output: OutputBattle, player: NPC, enemy: NPC
) -> None:
    """
    Registers battles in Battle()

    Parameters:
        session: Session
        output: Output of the battle: won, lost, draw
        player: The human player.
        enemy: The enemy player.

    """
    fighter = "player" if player.isplayer else player.slug
    opponent = "player" if enemy.isplayer else enemy.slug
    client = session.client.event_engine
    client.execute_action("set_battle", [fighter, output, opponent], True)


def build_hud_text(
    menu: str,
    monster: Monster,
    is_right: bool,
    is_trainer: bool,
    is_status: bool,
) -> str:
    """
    Returns the text image for use on the callout of the monster.

    Parameters:
        menu: Combat menu (eg. MainCombatMenuState).
        monster: The monster fighting.
        is_right: Boolean side (true: right side, false: left side).
            right side (player), left side (opponent)
        is_trainer: Boolean battle (trainer: true, wild: false).

    Returns:
        A string representing the HUD text for the monster.

    """
    if menu == "MainParkMenuState" and monster.owner and is_right:
        # Special case for MainParkMenuState
        ball = T.translate("tuxeball_park")
        item = monster.owner.find_item("tuxeball_park")
        if item is None:
            return f"{ball.upper()}: 0"
        return f"{ball.upper()}: {item.quantity}"

    icon = ""
    if monster.gender == GenderType.male:
        icon = "♂"
    elif monster.gender == GenderType.female:
        icon = "♀"

    symbol = ""
    if not is_trainer and is_status and not is_right:
        symbol = "◉"

    return f"{monster.name}{icon} Lv.{monster.level}{symbol}"


def retrieve_from_party(party: list[Monster], method: str) -> Monster:
    """
    Retrieves a monster from the party based on the specified method.

    Parameters:
        party: List of monsters in the party.
        method: Method to use when selecting a monster
            (e.g., 'lv_highest', 'healthiest', etc.).

    Returns:
        Monster: The selected monster.

    Notes:
        If the method is not recognized, a random monster from
        the party will be returned.

    """
    methods = {
        "lv_highest": ("level", max),
        "lv_lowest": ("level", min),
        "healthiest": ("current_hp", max),
        "weakest": ("current_hp", min),
        "oldest": ("steps", max),
        "newest": ("steps", min),
    }

    # eg. speed_max, armour_max, etc.
    methods.update(
        {f"{stat.value}_max": (stat.value, max) for stat in StatType}
    )
    # eg. speed_min, armour_min, etc.
    methods.update(
        {f"{stat.value}_min": (stat.value, min) for stat in StatType}
    )

    if method not in methods:
        return random.choice(party)

    attr, func = methods[method]
    return func(party, key=lambda m: getattr(m, attr))
