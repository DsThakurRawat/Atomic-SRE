"""Tests for MCP tool filtering logic."""

from unittest.mock import MagicMock

from atomic_sre.core.agent import _filter_mcp_tools


def _mock_tool(name: str) -> MagicMock:
    """Create a mock BaseTool with a given name."""
    tool = MagicMock()
    tool.name = name
    return tool


class TestFilterMcpTools:
    """Tests for _filter_mcp_tools."""

    def test_allows_slack_conversations_add_message(self) -> None:
        """Should keep conversations_add_message from Slack."""
        tools = [_mock_tool("slack_conversations_add_message")]
        filtered, has_slack = _filter_mcp_tools(tools)
        assert len(filtered) == 1
        assert has_slack is True

    def test_blocks_other_slack_tools(self) -> None:
        """Should block Slack tools that are not in the allow list."""
        tools = [
            _mock_tool("slack_conversations_list"),
            _mock_tool("slack_users_list"),
        ]
        filtered, has_slack = _filter_mcp_tools(tools)
        assert len(filtered) == 0
        assert has_slack is False

    def test_allows_github_search_and_get_file(self) -> None:
        """Should keep search_code and get_file_contents from GitHub."""
        tools = [
            _mock_tool("search_code"),
            _mock_tool("get_file_contents"),
            _mock_tool("create_pull_request"),
        ]
        filtered, _ = _filter_mcp_tools(tools)
        assert len(filtered) == 2
        names = {t.name for t in filtered}
        assert "search_code" in names
        assert "get_file_contents" in names

    def test_empty_input_returns_empty(self) -> None:
        """Empty tool list should return empty results."""
        filtered, has_slack = _filter_mcp_tools([])
        assert filtered == []
        assert has_slack is False
