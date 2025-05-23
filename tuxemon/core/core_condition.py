# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

from tuxemon.session import Session
from tuxemon.tools import cast_dataclass_parameters

if TYPE_CHECKING:
    from tuxemon.item.item import Item
    from tuxemon.monster import Monster
    from tuxemon.status.status import Status
    from tuxemon.technique.technique import Technique

logger = logging.getLogger(__name__)


@dataclass
class CoreCondition:
    """
    CoreCondition handles multiple condition types with operational state
    tracking via is_expected.
    """

    name: ClassVar[str]
    # Represents truth state (is/not)
    is_expected: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        cast_dataclass_parameters(self)

    def test_with_monster(self, session: Session, target: Monster) -> bool:
        """Test conditions related to a Monster's attributes."""
        logger.info(f"Testing {target.name} for condition {self.name}")
        return True

    def test_with_item(self, session: Session, target: Item) -> bool:
        """Test conditions related to a Item's attributes."""
        logger.info(f"Testing {target.name} for condition {self.name}")
        return True

    def test_with_tech(self, session: Session, target: Technique) -> bool:
        """Test conditions related to a Technique's attributes."""
        logger.info(f"Testing {target.name} for condition {self.name}")
        return True

    def test_with_status(self, session: Session, target: Status) -> bool:
        """Test conditions related to a Status's attributes."""
        logger.info(f"Testing {target.name} for condition {self.name}")
        return True

    def test_multiple_targets(
        self, session: Session, targets: list[Any]
    ) -> bool:
        """
        Validate all conditions for multiple targets using the appropriate test methods.
        """
        if not targets:
            logger.warning("No targets provided for validation.")
            return False

        failed_targets = []

        for target in targets:
            target_type = target.__class__.__name__.lower()
            test_method_name = f"test_with_{target_type}"

            test_method = getattr(self, test_method_name, None)
            if test_method is None:
                logger.warning(
                    f"Missing test method '{test_method_name}' for target: {target}"
                )
                failed_targets.append(target)
                continue

            try:
                if not test_method(session, target):
                    failed_targets.append(target)
            except Exception as e:
                logger.error(f"Error while testing target {target_type}: {e}")
                failed_targets.append(target)

        if failed_targets:
            logger.info(f"Validation failed for targets: {failed_targets}")
            return False

        return True
