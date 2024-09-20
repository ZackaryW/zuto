import pytest
from zuto.utils import match_scope

class TestMatchScope:
    @pytest.mark.parametrize("scope, path, expected", [
        ("*", "any/path", True),
        ("*/folder", "path/to/folder", True),
        ("*/folder", "path/to/other", False),
        ("folder/*", "folder/any/path", True),
        ("folder/*", "other/any/path", False),
        ("*/middle/*", "start/middle/end", True),
        ("*/middle/*", "start/other/end", False),
        ("exact/path", "exact/path", True),
        ("exact/path", "different/path", False),
        ("", "", True),
        ("*/*", "single/level", True),
        ("*/*", "multiple/levels/path", True),
    ])
    def test_match_scope_variations(self, scope, path, expected):
        assert match_scope(scope, path) == expected

    def test_match_scope_case_sensitivity(self):
        assert match_scope("Folder/*", "folder/subpath") is False
        assert match_scope("*/Folder", "path/to/folder") is False

    def test_match_scope_empty_strings(self):
        assert match_scope("", "") is True
        assert match_scope("*", "") is True
        assert match_scope("", "path") is False

    def test_match_scope_special_characters(self):
        assert match_scope("folder-with-dashes/*", "folder-with-dashes/subpath") is True
        assert match_scope("*/file.txt", "path/to/file.txt") is True
        assert match_scope("folder_with_underscores/*", "folder_with_underscores/subpath") is True

    def test_match_scope_multiple_wildcards(self):
        assert match_scope("*/*/*/*", "one/two/three/four") is True
        assert match_scope("*/*/*/*", "one/two/three") is False
        assert match_scope("*/*/*/*", "one/two/three/four/five") is True

    def test_match_scope_edge_cases(self):
        assert match_scope("*/", "path/") is True
        assert match_scope("/*", "/path") is True
        assert match_scope("*//*", "path//subpath") is True
