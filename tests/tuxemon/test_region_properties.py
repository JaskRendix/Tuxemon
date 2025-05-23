# SPDX-License-Identifier: GPL-3.0
# Copyright (c) 2014-2025 William Edwards <shadowapex@gmail.com>, Benjamin Bean <superman2k5@gmail.com>
import unittest

from tuxemon.db import Direction
from tuxemon.map import RegionProperties, extract_region_properties


class TestExtractRegionProperties(unittest.TestCase):
    def test_empty_properties(self):
        self.assertIsNone(extract_region_properties({}))

    def test_only_enter_from(self):
        properties = {"enter_from": "up, left"}
        expected = RegionProperties(
            enter_from=[Direction.left, Direction.up],
            exit_from=[],
            endure=[],
            entity=None,
            key=None,
        )
        self.assertEqual(extract_region_properties(properties), expected)

    def test_only_exit_from(self):
        properties = {"exit_from": "down"}
        expected = RegionProperties(
            enter_from=[Direction.up, Direction.left, Direction.right],
            exit_from=[Direction.down],
            endure=[],
            entity=None,
            key=None,
        )
        self.assertEqual(extract_region_properties(properties), expected)

    def test_all_properties(self):
        properties = {
            "enter_from": "up, left",
            "exit_from": "down, right",
            "endure": "left",
            "key": "door",
        }
        expected = RegionProperties(
            enter_from=[Direction.left, Direction.up],
            exit_from=[Direction.down, Direction.right],
            endure=[Direction.left],
            entity=None,
            key="door",
        )
        self.assertEqual(extract_region_properties(properties), expected)

    def test_slide_label(self):
        properties = {"key": "slide"}
        expected = RegionProperties(
            enter_from=list(Direction),
            exit_from=list(Direction),
            endure=list(Direction),
            entity=None,
            key="slide",
        )
        self.assertEqual(extract_region_properties(properties), expected)

    def test_invalid_direction(self):
        properties = {"enter_from": "up, invalid"}
        with self.assertRaises(ValueError):
            extract_region_properties(properties)

    def test_none_value(self):
        properties = {"enter_from": None}
        expected = RegionProperties(
            enter_from=[], exit_from=[], endure=[], entity=None, key=None
        )
        self.assertEqual(extract_region_properties(properties), expected)

    def test_duplicate_directions(self):
        properties = {"enter_from": "up, up, left"}
        expected = RegionProperties(
            enter_from=[Direction.left, Direction.up],
            exit_from=[],
            endure=[],
            entity=None,
            key=None,
        )
        self.assertEqual(extract_region_properties(properties), expected)

    def test_mixed_case_directions(self):
        properties = {"enter_from": "Up, Left"}
        expected = RegionProperties(
            enter_from=[Direction.left, Direction.up],
            exit_from=[],
            endure=[],
            entity=None,
            key=None,
        )
        self.assertEqual(extract_region_properties(properties), expected)

    def test_extra_whitespace(self):
        properties = {"enter_from": " up , left "}
        expected = RegionProperties(
            enter_from=[Direction.left, Direction.up],
            exit_from=[],
            endure=[],
            entity=None,
            key=None,
        )
        self.assertEqual(extract_region_properties(properties), expected)

    def test_invalid_key(self):
        properties = {"invalid_key": "value"}
        self.assertIsNone(extract_region_properties(properties))

    def test_empty_string_values(self):
        properties = {"enter_from": "", "exit_from": ""}
        with self.assertRaises(ValueError):
            extract_region_properties(properties)

    def test_missing_enter_exit_from(self):
        properties = {"endure": "left"}
        expected = RegionProperties(
            enter_from=[],
            exit_from=[],
            endure=[Direction.left],
            entity=None,
            key=None,
        )
        self.assertEqual(extract_region_properties(properties), expected)

    def test_invalid_slide_label(self):
        properties = {"enter_from": "slide"}
        with self.assertRaises(ValueError):
            extract_region_properties(properties)

    def test_mixed_valid_invalid_keys(self):
        properties = {
            "enter_from": "up, left",
            "invalid_key": "value",
            "key": "door",
        }
        expected = RegionProperties(
            enter_from=[Direction.left, Direction.up],
            exit_from=[],
            endure=[],
            entity=None,
            key="door",
        )
        self.assertEqual(extract_region_properties(properties), expected)

    def test_empty_endure(self):
        properties = {"endure": ""}
        with self.assertRaises(ValueError):
            extract_region_properties(properties)

    def test_circular_logic(self):
        properties = {"exit_from": "left, right"}
        expected = RegionProperties(
            enter_from=[Direction.up, Direction.down],
            exit_from=[Direction.left, Direction.right],
            endure=[],
            entity=None,
            key=None,
        )
        self.assertEqual(extract_region_properties(properties), expected)

    def test_all_keys_missing(self):
        properties = {"unknown_key": "value"}
        self.assertIsNone(extract_region_properties(properties))

    def test_case_insensitive_keys(self):
        properties = {"Enter_from": "up, left"}
        expected = RegionProperties(
            enter_from=[Direction.left, Direction.up],
            exit_from=[],
            endure=[],
            entity=None,
            key=None,
        )
        self.assertEqual(extract_region_properties(properties), expected)

    def test_all_directions_empty_key(self):
        properties = {"enter_from": "up, down, left, right", "key": ""}
        with self.assertRaises(ValueError):
            extract_region_properties(properties)

    def test_invalid_characters_in_directions(self):
        properties = {"enter_from": "up, @, left"}
        with self.assertRaises(ValueError):
            extract_region_properties(properties)
