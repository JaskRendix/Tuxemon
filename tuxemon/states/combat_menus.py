# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2026 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable, Generator
from functools import partial
from typing import TYPE_CHECKING, Any, ClassVar

from pygame import SRCALPHA
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.transform import scale as pg_scale

from tuxemon.combat.menu_visibility import MenuProfiles
from tuxemon.db import EffectPhase, SpeedLabel, State
from tuxemon.graphics import load_and_scale, load_image
from tuxemon.item.filter import ItemFilter
from tuxemon.locale.locale import T
from tuxemon.menu.interface import MenuItem
from tuxemon.menu.menu import Menu, PopUpMenu
from tuxemon.monster.monster import Monster
from tuxemon.sprite import Sprite
from tuxemon.states.item_menu import ItemMenuState
from tuxemon.states.monster_menu import MonsterMenuState
from tuxemon.technique.technique import Technique
from tuxemon.tools import fix_measure, open_dialog
from tuxemon.ui.graphic_box import GraphicBox
from tuxemon.ui.text import TextArea

if TYPE_CHECKING:
    from tuxemon.base_client import BaseClient
    from tuxemon.entity.npc import NPC
    from tuxemon.item.item import Item
    from tuxemon.session import Session
    from tuxemon.states.combat_state import CombatState

logger = logging.getLogger(__name__)


MenuGameObj = Callable[[], None]


class TechniquePreviewOverlay:
    LAYER = 200

    TYPE_ICON_POSITIONS = (
        (132 / 256, 126 / 144),
        (142 / 256, 126 / 144),
    )

    RANGE_ICON_POSITION = (7 / 256, 121 / 144)

    SPEED_ICON_POSITION = (135 / 256, 113 / 144)

    TEXT_POSITIONS = {
        "accuracy": (7 / 256, 114 / 144),
        "power": (44 / 256, 123 / 144),
        "recharge": (7 / 256, 133 / 144),
    }

    def __init__(self, menu: MainCombatMenuState):
        self.menu = menu

        self.type_icons: list[Sprite] = []
        self.text_sprites: dict[str, Sprite] = {}

        self.range_icon: Sprite | None = None
        self.speed_icon: Sprite | None = None

    @property
    def resolution(self) -> tuple[int, int]:
        return self.menu.client.context.resolution

    def _position(
        self,
        rel_x: float,
        rel_y: float,
    ) -> tuple[int, int]:
        screen_w, screen_h = self.resolution

        return (
            fix_measure(screen_w, rel_x),
            fix_measure(screen_h, rel_y),
        )

    def clear(self) -> None:
        for sprite in self.type_icons:
            sprite.kill()

        if self.range_icon:
            self.range_icon.kill()

        if self.speed_icon:
            self.speed_icon.kill()

        for sprite in self.text_sprites.values():
            sprite.kill()

        self.type_icons.clear()
        self.text_sprites.clear()

        self.range_icon = None
        self.speed_icon = None

    def show(self, technique: Technique) -> None:
        self.clear()

        self._draw_types(technique)
        self._draw_range(technique)
        self._draw_speed(technique)
        self._draw_stats(technique)

    def _draw_types(self, technique: Technique) -> None:
        for i, element in enumerate(technique.types.current[:2]):
            path = f"gfx/ui/icons/element/{element.slug}_type_small.png"

            try:
                surface = load_and_scale(path, self.menu.factor)

                sprite = Sprite()
                sprite.image = surface
                sprite.rect = surface.get_rect()

                sprite.rect.topleft = self._position(
                    *self.TYPE_ICON_POSITIONS[i]
                )

                self.menu.sprites.add(
                    sprite,
                    layer=self.LAYER,
                )

                self.type_icons.append(sprite)

            except Exception as e:
                logger.error(f"Could not load type icon {path}: {e}")

    def _draw_range(self, technique: Technique) -> None:
        path = f"gfx/ui/icons/range/{technique.range.name.lower()}.png"

        try:
            surface = load_and_scale(path, self.menu.factor)

            sprite = Sprite()
            sprite.image = surface
            sprite.rect = surface.get_rect()

            sprite.rect.topleft = self._position(*self.RANGE_ICON_POSITION)

            self.menu.sprites.add(
                sprite,
                layer=self.LAYER,
            )

            self.range_icon = sprite

        except Exception as e:
            logger.error(f"Could not load range icon {path}: {e}")

    def _draw_speed(self, technique: Technique) -> None:
        speed_label = SpeedLabel.from_numeric(technique.speed)

        path = f"gfx/ui/icons/speed/{speed_label.value}.png"

        try:
            surface = load_and_scale(path, self.menu.factor)

            sprite = Sprite()
            sprite.image = surface
            sprite.rect = surface.get_rect()

            sprite.rect.topleft = self._position(*self.SPEED_ICON_POSITION)

            self.menu.sprites.add(
                sprite,
                layer=self.LAYER,
            )

            self.speed_icon = sprite

        except Exception as e:
            logger.error(f"Could not load speed icon {path}: {e}")

    def _draw_stats(self, technique: Technique) -> None:
        scaled_power = int(technique.power * (7 + self.menu.monster.level))

        lines = {
            "accuracy": (
                f"{T.translate('technique_accuracy')} "
                f"{int(technique.accuracy * 100)}%"
            ),
            "recharge": (
                f"{T.translate('technique_recharge')} "
                f"{technique.cooldown.duration} "
                f"{T.translate('technique_turns')}"
            ),
        }

        if scaled_power > 0:
            lines["power"] = f"{T.translate('technique_power')} {scaled_power}"

        for key, text in lines.items():
            surface = self.menu.font.render(
                text,
                True,
                (0, 0, 0),
            )

            sprite = Sprite()
            sprite.image = surface
            sprite.rect = surface.get_rect()

            sprite.rect.topleft = self._position(*self.TEXT_POSITIONS[key])

            self.menu.sprites.add(
                sprite,
                layer=self.LAYER,
            )

            self.text_sprites[key] = sprite


class MainCombatMenuState(PopUpMenu[MenuGameObj]):
    """
    Main menu for combat: Fight, Item, Swap, Run

    TODO: there needs to be more general use registers in the combat state to
    query what player is doing what. There's lots of spaghetti right now.
    """

    name: ClassVar[str] = "MainCombatMenuState"
    escape_key_exits = False
    columns = 2

    def __init__(
        self,
        client: BaseClient,
        session: Session,
        combat: CombatState,
        character: NPC,
        monster: Monster,
        **kwargs: Any,
    ) -> None:
        super().__init__(client=client, **kwargs)
        self.preview_overlay = TechniquePreviewOverlay(self)
        self.rect = self.calculate_menu_rectangle()
        self.session = session
        self.combat_session = self.client.combat_session
        self.combat = combat
        self.character = character
        self.monster = monster
        self.party = self.combat_session.field_monsters.get_monsters(
            self.character
        )
        if self.character == self.combat_session.left_player:
            self.enemy = self.combat_session.right_player
        else:
            self.enemy = self.combat_session.left_player

        self.opponents = self.combat_session.field_monsters.get_monsters(
            self.enemy
        )
        self.event_bus.publish(
            "combat_dialog",
            message=self._combat_prompt(),
        )

    def _combat_prompt(self) -> str:
        return T.format(
            "combat_monster_choice",
            {"name": self.monster.name},
        )

    def calculate_menu_rectangle(self) -> Rect:
        rect_screen = self.client.context.rect.copy()
        menu_width = fix_measure(rect_screen.w, 102 / 256)
        menu_height = fix_measure(rect_screen.h, 36 / 144)
        rect = Rect(0, 0, menu_width, menu_height)
        rect.bottomright = rect_screen.w, rect_screen.h
        return rect

    def get_menu_profile(self) -> tuple[dict[str, str], dict[str, bool]]:
        if self.combat_session.is_trainer_battle:
            return MenuProfiles.default_trainer_battle()
        else:
            return MenuProfiles.default_monster_battle()

    def initialize_items(self) -> Generator[MenuItem[MenuGameObj], None, None]:
        menu_map, default_visibility = self.get_menu_profile()
        visibility_map = default_visibility.copy()
        visibility_map.update(self.combat_session.menu_visibility_map)

        if self.enemy.combat.forfeit:
            visibility_map["menu_forfeit"] = True

        # Hide Item if no usable items
        items_filtered = ItemFilter(self.character.items)
        items_filtered.set_filter_combat_targets(
            self.session, self.character.monsters, self.opponents
        )
        if not items_filtered.items:
            visibility_map["menu_item"] = False

        # Hide Swap if no valid swap targets
        if not self.can_swap_any(self.character):
            visibility_map["menu_monster"] = False

        # Yield menu items
        for key, method_name in menu_map.items():
            callback = getattr(self, method_name)
            visible = visibility_map.get(key, False)
            foreground = self.unavailable_color if not visible else None

            yield MenuItem(
                self.shadow_text(T.translate(key).upper(), fg=foreground),
                T.translate(key).upper(),
                None,
                callback,
                visible,
            )

    def forfeit(self) -> None:
        """
        Cause player to forfeit from the trainer battles.
        """
        forfeit = Technique.create("menu_forfeit")
        self.client.remove_state_by_name("MainCombatMenuState")
        self.combat_session.enqueue_action(
            self.monster, forfeit, self.opponents[0]
        )

    def run(self) -> None:
        """
        Cause player to run from the wild encounters.
        """
        run = Technique.create("menu_run")
        status = self.monster.status.current_status
        message = status.name.lower() if status else ""
        if not run.validate_monster(self.session, self.monster):
            params = {
                "monster": self.monster.name.upper(),
                "status": message,
            }
            msg = T.format("combat_player_run_status", params)
            open_dialog(self.client, [msg], dialog_speed="max")
            return
        self.client.remove_state_by_name("MainCombatMenuState")
        self.combat_session.enqueue_action(
            self.monster, run, self.opponents[0]
        )

    def can_swap_any(self, character: NPC) -> bool:
        """Return True if the character has at least one valid swap target."""
        active = self.combat_session.active_monsters
        tracker = self.combat_session.swap_tracker

        for mon in character.monsters:
            if mon.is_fainted:
                continue
            if mon in active:
                continue
            if not tracker.can_swap(mon):
                continue
            return True

        return False

    def open_swap_menu(self) -> None:
        """Open menu to swap monsters in party."""

        menu = self.client.push_state(
            MonsterMenuState(
                self.client,
                self.character.monsters,
                on_selection=self._swap_monster,
                is_valid_entry=self._validate_swap_target,
            )
        )

        menu.anchor("bottom", self.rect.top)
        menu.anchor("right", self.client.context.rect.right)

    def _validate_swap_target(
        self,
        monster: Monster | None,
    ) -> bool:
        if monster is None:
            return False

        if monster.is_fainted:
            return False

        if monster in self.combat_session.active_monsters:
            return False

        return self.combat_session.swap_tracker.can_swap(monster)

    def _swap_monster(
        self,
        menu_item: MenuItem[Monster | None],
    ) -> None:
        monster = menu_item.game_object

        if monster is None:
            return

        swap = Technique.create("swap")

        status = self.monster.status.current_status
        status_name = status.name.lower() if status else ""

        if not swap.validate_monster(
            self.session,
            self.monster,
        ):
            params = {
                "monster": self.monster.name.upper(),
                "status": status_name,
            }

            msg = T.format(
                "combat_player_swap_status",
                params,
            )

            open_dialog(
                self.client,
                [msg],
                dialog_speed="max",
            )

            return

        self.combat_session.swap_tracker.register(monster)

        self.combat_session.enqueue_action(
            self.monster,
            swap,
            monster,
        )

        self.client.pop_state()
        self.client.pop_state()

    def open_item_menu(self) -> None:
        """Open menu to choose an item."""

        items_filtered = ItemFilter(self.character.items)

        items_filtered.set_filter_combat_targets(
            self.session,
            self.character.monsters,
            self.opponents,
        )

        self.client.push_state(
            ItemMenuState(
                self.client,
                character=self.character,
                source=self.name,
                item_filter=items_filtered,
                on_selection=self._choose_item_target,
                is_valid_entry=self._validate_item,
            )
        )

    def _validate_item(
        self,
        item: Item | None,
    ) -> bool:
        if not item or not item.behaviors.throwable:
            return True

        return all(
            item.validate_monster(
                self.session,
                opponent,
            )
            for opponent in self.opponents
        )

    def _choose_item_target(
        self,
        menu_item: MenuItem[Item],
    ) -> None:
        item = menu_item.game_object

        self.client.remove_state_by_name("ItemMenuState")

        if State["MainCombatMenuState"] not in item.usable_in:
            return

        if item.behaviors.throwable:
            self._enqueue_item(
                item,
                self.opponents[0],
            )
            return

        self.client.push_state(
            MonsterMenuState(
                self.client,
                self.character.monsters,
                on_selection=partial(
                    self._enqueue_item_from_menu,
                    item,
                ),
                is_valid_entry=partial(
                    self._validate_item_target,
                    item,
                ),
            )
        )

    def _validate_item_target(
        self,
        item: Item,
        monster: Monster | None,
    ) -> bool:
        if monster is None:
            return False

        return item.validate_monster(
            self.session,
            monster,
        )

    def _enqueue_item_from_menu(
        self,
        item: Item,
        menu_item: MenuItem[Monster],
    ) -> None:
        self._enqueue_item(
            item,
            menu_item.game_object,
        )

    def _enqueue_item(
        self,
        item: Item,
        target: Monster,
    ) -> None:
        status = target.status.current_status

        if status:
            result = status.use(
                self.session,
                EffectPhase.ENQUEUE_ITEM,
            )

            if result.extras:
                template = "\n".join(
                    T.translate(extra) for extra in result.extras
                )

                open_dialog(
                    self.client,
                    [template],
                    dialog_speed="max",
                )
                return

        self.combat_session.enqueue_action(
            self.character,
            item,
            target,
        )

        self.character.battle_last_used_item_slug = item.slug

        self.client.remove_state_by_name("MainCombatMenuState")

        if not item.behaviors.throwable:
            self.client.remove_state_by_name("MonsterMenuState")

    def open_technique_menu(self) -> None:
        """Open menu to choose a technique."""

        menu = self._create_technique_menu()

        menu.on_selection_callback = self._choose_technique_target

        menu.on_menu_selection_change_callback = lambda: (
            self._show_technique_preview(menu)
        )

        menu.on_close_callback = self._hide_technique_preview

        menu.on_menu_selection_change()

    def _create_technique_menu(self) -> Menu[Any]:
        menu: Menu[Any] = self.client.push_state(Menu(self.client))
        menu.shrink_to_items = True

        usable_moves = self.monster.moves.get_usable_moves(
            self.session,
            self.opponents,
        )

        if not usable_moves:
            for move in self.monster.moves.get_fallback_moves():
                menu.add(
                    MenuItem(
                        self.shadow_text(move.name),
                        None,
                        None,
                        move,
                    )
                )
        else:
            self._populate_technique_menu(menu)

        enabled_items = [
            i for i, item in enumerate(menu.menu_items) if item.enabled
        ]

        if enabled_items:
            menu.selected_index = enabled_items[0]

        menu.anchor("bottom", self.rect.top)
        menu.anchor("right", self.client.context.rect.right)

        return menu

    def _populate_technique_menu(
        self,
        menu: Menu[Any],
    ) -> None:
        for tech in self.monster.moves.get_moves():
            usable = any(
                tech.can_use(self.session, opponent)
                for opponent in self.opponents
            )

            if usable:
                tech_name = tech.name
                tech_color = None
                enabled = True
            else:
                tech_name = (
                    f"{tech.name} ({tech.cooldown.remaining})"
                    if tech.is_recharging
                    else tech.name
                )

                tech_color = self.unavailable_color
                enabled = False

            menu.add(
                MenuItem(
                    self.shadow_text(
                        tech_name,
                        fg=tech_color,
                    ),
                    None,
                    None,
                    tech,
                    enabled,
                )
            )

    def _show_technique_preview(
        self,
        menu: Menu[Any],
    ) -> None:
        self.event_bus.publish(
            "combat_dialog",
            message="",
            dialog_speed="max",
        )

        item = menu.get_selected_item()
        if item:
            self.preview_overlay.show(item.game_object)

    def _hide_technique_preview(self) -> None:
        self.preview_overlay.clear()
        self.event_bus.publish(
            "combat_dialog",
            message=self._combat_prompt(),
            dialog_speed="max",
        )

    def _choose_technique_target(
        self,
        menu_item: MenuItem[Technique],
    ) -> None:
        technique = menu_item.game_object

        if len(self.opponents) > 1 and technique.targets_enemy():
            self.client.push_state(
                CombatTargetMenuState(
                    client=self.client,
                    combat=self.combat,
                    character=self.character,
                    monster=self.monster,
                    technique=technique,
                    on_selection=partial(
                        self._enqueue_technique_from_menu,
                        technique,
                    ),
                )
            )
            return

        target = (
            self.monster
            if technique.target["own_monster"]
            else self.opponents[0]
        )

        self._enqueue_technique(
            technique,
            target,
        )

    def _enqueue_technique_from_menu(
        self,
        technique: Technique,
        menu_item: MenuItem[Monster],
    ) -> None:
        self._enqueue_technique(
            technique,
            menu_item.game_object,
        )

    def _enqueue_technique(
        self,
        technique: Technique,
        target: Monster,
    ) -> None:

        if not technique.validate_monster(
            self.session,
            target,
        ):
            params = {"name": technique.name.upper()}
            msg = T.format(
                "cannot_use_tech_monster",
                params,
            )

            open_dialog(
                self.client,
                [msg],
                dialog_speed="max",
            )
            return

        if technique.has_effect("damage") and target == self.monster:
            params = {"name": technique.name.upper()}
            msg = T.format(
                "combat_target_itself",
                params,
            )

            open_dialog(
                self.client,
                [msg],
                dialog_speed="max",
            )
            return

        self.combat_session.set_variable(
            "action_tech",
            technique.slug,
        )

        technique = self.combat_session.pre_checking(
            self.session,
            self.monster,
            technique,
            target,
        )

        self.combat_session.enqueue_action(
            self.monster,
            technique,
            target,
        )

        if len(self.opponents) > 1:
            self.client.remove_state_by_name("CombatTargetMenuState")

        self.client.remove_state_by_name("Menu")
        self.client.pop_state(self)


class CombatTargetMenuState(Menu[Monster]):
    """Menu for selecting targets of techniques and items."""

    name: ClassVar[str] = "CombatTargetMenuState"
    transparent = True

    def __init__(
        self,
        client: BaseClient,
        combat: CombatState,
        character: NPC,
        monster: Monster,
        technique: Technique,
        *,
        on_selection: Callable[[MenuItem[Monster]], None] | None = None,
        is_valid_entry: Callable[[Monster | None], bool] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(client=client, **kwargs)
        self.character = character
        self.monster = monster
        self.combat = combat
        self.combat_session = self.client.combat_session
        self.technique = technique
        self._external_on_selection = on_selection
        self._external_is_valid_entry = is_valid_entry
        self.targeting_map: defaultdict[str, list[Monster]] = defaultdict(list)
        self._crosshairs_sprite: Sprite | None = None

        self._create_menu()

    def initialize_items(self) -> Generator[MenuItem[Monster], None, None]:
        """Generates menu items based on targeting rules for 2vs2 or 1vs2 combat."""
        self.targeting_map.clear()

        if self.technique.behaviors.bypasses_selection:
            if self.technique.target.get("enemy_monster"):
                for (
                    player,
                    monsters,
                ) in self.combat_session.field_monsters.get_all_monsters().items():
                    if player != self.character and monsters:
                        yield self._create_menu_item(monsters[0])
                        break
            else:
                yield self._create_menu_item(self.monster)
            return

        for (
            player,
            monsters,
        ) in self.combat_session.field_monsters.get_all_monsters().items():
            targeting_class = (
                "own_monster" if player == self.character else "enemy_monster"
            )
            self.targeting_map[targeting_class].extend(monsters)

            show = self.technique.target.get(targeting_class)
            if not show and targeting_class == "enemy_monster":
                show = self.technique.targets_enemy()
            if not show:
                continue

            for monster in monsters:
                yield self._create_menu_item(monster)

    def _create_menu_item(self, monster: Monster) -> MenuItem[Monster]:
        """Creates a menu item for a given monster."""
        sprite = self.combat.sprite_map.get_sprite(monster)
        if sprite is None:
            raise KeyError(f"Sprite not found for entity: {monster.name}")
        item = MenuItem(self.surface, None, monster.name, monster)
        item.rect = sprite.rect.copy()
        item.rect.inflate_ip(self.factor, self.factor)
        return item

    def _create_menu(self) -> None:
        """Sets up the menu UI."""
        rect_screen = self.client.context.rect.copy()
        rect = Rect(0, 0, rect_screen.w // 2, rect_screen.h // 4)
        rect.bottomright = rect_screen.w, rect_screen.h

        self.window = GraphicBox(
            rect,
            load_and_scale(self.borders_filename),
            color=self.background_color,
        )
        self.sprites.add(self.window, layer=100)

        self.text_area = TextArea(
            font=self.font,
            font_color=self.font_color,
            rect=self.window.inner_rect,
            scaling=self.client.context.scaling,
        )
        self.sprites.add(self.text_area, layer=100)

        self.surface = Surface(self.window.rect.size, SRCALPHA)
        self.border = GraphicBox(
            Rect(0, 0, 1, 1),
            load_and_scale(self.borders_filename),
        )

    def determine_target(self) -> None:
        """Finds the best target based on technique settings."""
        for target_tag, target_value in self.technique.target.items():
            if target_value:
                for target in self.targeting_map.get(target_tag, []):
                    menu_item = self.search_items(target)
                    if menu_item and menu_item.enabled:
                        self.selected_index = self.menu_items.sprites().index(
                            menu_item
                        )
                        return

    def refresh_layout(self, *, mutate: bool = True) -> Rect:
        """Updates layout after determining the target."""
        self.determine_target()
        return super().refresh_layout(mutate=mutate)

    def _update_borders(self) -> None:
        """Shows crosshairs over the currently selected monster in 2vs2/1vs2 combat."""
        for sprite in self.menu_items:
            sprite.image.fill((0, 0, 0, 0))

        if self._crosshairs_sprite is not None:
            self._crosshairs_sprite.kill()
            self._crosshairs_sprite = None

        if selected := self.get_selected_item():
            monster = selected.game_object
            pos = self.combat.sprite_map.get_sprite(monster)
            if pos is None:
                return

            s = self.client.context.scaling.scale_int(64)
            crosshairs_image = pg_scale(
                load_image("gfx/ui/combat/crosshairs.png"), (s, s)
            )
            spr = Sprite()
            spr.image = crosshairs_image
            spr.rect = crosshairs_image.get_rect(center=pos.rect.center)
            self.sprites.add(spr, layer=101)
            self._crosshairs_sprite = spr

            if selected.description:
                self.dialog.alert(selected.description, self.text_area)

    def update_cursor_visibility(self) -> None:
        self.hide_cursor()

    def on_open(self) -> None:
        items = [i for i in self.menu_items if i.enabled]
        if len(items) == 1:
            self.on_menu_selection(items[0])

    def on_menu_selection_change(self) -> None:
        """Handles border updates when selection changes."""
        self.hide_cursor()
        self._update_borders()

    def on_menu_selection(self, item: MenuItem[Monster]) -> None:
        if self._external_on_selection:
            return self._external_on_selection(item)

    def is_valid_entry(self, monster: Monster | None) -> bool:
        if self._external_is_valid_entry:
            return self._external_is_valid_entry(monster)
        return monster is not None
