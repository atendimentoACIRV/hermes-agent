"""
OPC-03 RED Tests: Trello READ Vertical - Live Validation

These tests define the expected behavior for the Trello READ vertical.
They will FAIL until OPC-03 is fully implemented with live credentials.

Gate: H-079 baseline qualification must be GREEN before implementation.
"""
from __future__ import annotations

import os
import pytest
from unittest.mock import patch, MagicMock

# These tests require live Trello credentials
# They will be skipped unless TRELLO_API_KEY and TRELLO_TOKEN are set
TRELLO_CREDS_AVAILABLE = bool(os.getenv("TRELLO_API_KEY") and os.getenv("TRELLO_TOKEN"))


class TestTrelloReadLiveValidation:
    """Live validation tests for Trello READ operations."""

    @pytest.mark.skipif(not TRELLO_CREDS_AVAILABLE, reason="TRELLO_API_KEY and TRELLO_TOKEN not set")
    def test_open_editorial_board_via_prefab(self):
        """User command 'Abra o Calendário Editorial' should navigate and verify URL."""
        from workstation.prefabs.integration import maybe_resolve_navigation
        from workstation.prefabs.catalog import match_navigation

        # Match the navigation intent
        dest = match_navigation("Abra o Calendário Editorial")
        assert dest is not None
        assert dest.key == "trello_editorial"

        # This will require a full agent context with browser tools
        # RED: Currently fails because maybe_resolve_navigation needs full agent context
        # with valid_tool_names including browser_navigate and browser_snapshot
        pytest.fail("RED: maybe_resolve_navigation requires full agent context with browser tools - not yet integrated")

    @pytest.mark.skipif(not TRELLO_CREDS_AVAILABLE, reason="TRELLO_API_KEY and TRELLO_TOKEN not set")
    def test_open_scrum_board_via_prefab(self):
        """User command 'Abra o quadro SCRUM' should navigate and verify URL."""
        from workstation.prefabs.catalog import match_navigation
        dest = match_navigation("Abra o quadro SCRUM")
        assert dest is not None
        assert dest.key == "trello_scrum"
        pytest.fail("RED: Full navigation flow not yet wired to browser_workstation")

    @pytest.mark.skipif(not TRELLO_CREDS_AVAILABLE, reason="TRELLO_API_KEY and TRELLO_TOKEN not set")
    def test_list_editorial_cards_via_api(self):
        """TrelloClient.board_cards('editorial') should return real cards via official API."""
        from workstation.prefabs.trello import TrelloClient

        client = TrelloClient()
        result = client.board_cards("editorial", limit=10)

        assert "board" in result
        assert "total_matches" in result
        assert "cards" in result
        assert isinstance(result["cards"], list)
        # Verify card structure
        if result["cards"]:
            card = result["cards"][0]
            assert "id" in card
            assert "name" in card
            assert "shortUrl" in card

    @pytest.mark.skipif(not TRELLO_CREDS_AVAILABLE, reason="TRELLO_API_KEY and TRELLO_TOKEN not set")
    def test_list_scrum_cards_via_api(self):
        """TrelloClient.board_cards('scrum') should return real cards."""
        from workstation.prefabs.trello import TrelloClient

        client = TrelloClient()
        result = client.board_cards("scrum", limit=10)

        assert result["board"] == "scrum"
        assert isinstance(result["cards"], list)

    @pytest.mark.skipif(not TRELLO_CREDS_AVAILABLE, reason="TRELLO_API_KEY and TRELLO_TOKEN not set")
    def test_search_cards_by_name(self):
        """TrelloClient.board_cards with search should filter correctly."""
        from workstation.prefabs.trello import TrelloClient

        client = TrelloClient()
        # Search for a known card name pattern
        result = client.board_cards("editorial", search="test", limit=5)
        assert "cards" in result
        # All returned cards should match search term (case-insensitive, normalized)
        for card in result["cards"]:
            assert "test" in card["name"].lower() or result["total_matches"] == 0

    @pytest.mark.skipif(not TRELLO_CREDS_AVAILABLE, reason="TRELLO_API_KEY and TRELLO_TOKEN not set")
    def test_read_single_card(self):
        """TrelloClient.card() should read a specific card by ID."""
        from workstation.prefabs.trello import TrelloClient

        client = TrelloClient()
        # First get a card ID from the board
        board_result = client.board_cards("editorial", limit=1)
        if board_result["cards"]:
            card_id = board_result["cards"][0]["id"]
            card = client.card(card_id)
            assert card["id"] == card_id
            assert "description_sha256" in card
            assert "description" not in card  # Default: no description leak

    @pytest.mark.skipif(not TRELLO_CREDS_AVAILABLE, reason="TRELLO_API_KEY and TRELLO_TOKEN not set")
    def test_read_card_with_description(self):
        """TrelloClient.card(include_description=True) should include description."""
        from workstation.prefabs.trello import TrelloClient

        client = TrelloClient()
        board_result = client.board_cards("editorial", limit=1)
        if board_result["cards"]:
            card_id = board_result["cards"][0]["id"]
            card = client.card(card_id, include_description=True)
            assert "description" in card
            assert isinstance(card["description"], str)


class TestTrelloReadIntentMatching:
    """Test exact-match intent recognition (no LLM)."""

    def test_match_liste_cards_editorial(self):
        from workstation.prefabs.catalog import match_trello_read
        intent = match_trello_read("Liste os cards do Calendário Editorial")
        assert intent is not None
        assert intent.board == "editorial"
        assert intent.search == ""

    def test_match_liste_cards_scrum(self):
        from workstation.prefabs.catalog import match_trello_read
        intent = match_trello_read("Liste os cards do Quadro SCRUM")
        assert intent is not None
        assert intent.board == "scrum"

    def test_match_encontre_card(self):
        from workstation.prefabs.catalog import match_trello_read
        intent = match_trello_read("Encontre o card Dia das Crianças no Quadro SCRUM")
        assert intent is not None
        assert intent.board == "scrum"
        assert intent.search == "dia das criancas"

    def test_abstain_ambiguous(self):
        from workstation.prefabs.catalog import match_trello_read
        assert match_trello_read("Liste todos os cartões de qualquer quadro e delete todos") is None
        assert match_trello_read("Delete all cards") is None
        assert match_trello_read("") is None

    def test_trusted_human_only(self):
        from workstation.prefabs.integration import prepare_user_trello_read
        from types import SimpleNamespace

        e = lambda origin, authority: SimpleNamespace(
            origin=SimpleNamespace(value=origin),
            intent_authority=SimpleNamespace(value=authority),
            content="Liste os cards do Calendário Editorial"
        )
        assert prepare_user_trello_read(e("human", "CREATE_WORK")) is not None
        assert prepare_user_trello_read(e("agent", "CREATE_WORK")) is None
        assert prepare_user_trello_read(e("human", "OBSERVATION_ONLY")) is None


class TestTrelloReadToolsetVisibility:
    """Test that prefab tools appear/disappear with correct toolsets."""

    def test_prefab_catalog_in_browser_toolset(self):
        from tools.registry import discover_builtin_tools, registry
        discover_builtin_tools()
        browser_tools = registry.get_tool_names_for_toolset("browser")
        assert "prefab_catalog" in browser_tools

    def test_prefab_execute_in_desktop_ui_toolset(self):
        from tools.registry import discover_builtin_tools, registry
        discover_builtin_tools()
        desktop_tools = registry.get_tool_names_for_toolset("desktop_ui")
        assert "prefab_execute" in desktop_tools

    def test_prefab_catalog_actions(self):
        """Test prefab_catalog tool actions work."""
        from tools.registry import discover_builtin_tools, registry
        discover_builtin_tools()

        entry = registry.get_entry("prefab_catalog")
        assert entry is not None

        # Test catalog action
        result = entry.handler({"action": "catalog"})
        import json
        data = json.loads(result)
        assert data["ok"] is True
        assert "targets" in data["data"]
        assert len(data["data"]["targets"]) >= 7  # trello, trello_editorial, trello_scrum, whatsapp, chatgpt, instagram, instagram_acirv

        # Test match_navigation
        result = entry.handler({"action": "match_navigation", "text": "Abra o Trello"})
        data = json.loads(result)
        assert data["ok"] is True
        assert data["data"]["status"] == "matched"
        assert data["data"]["target"]["id"] == "trello"

        # Test match_trello_read
        result = entry.handler({"action": "match_trello_read", "text": "Liste os cards do Calendário Editorial"})
        data = json.loads(result)
        assert data["ok"] is True
        assert data["data"]["status"] == "matched"
        assert data["data"]["board"] == "editorial"


class TestTrelloReadIntegrationRED:
    """RED tests documenting what's needed for full OPC-03 completion."""

    def test_fast_path_zero_llm_on_exact_match(self):
        """EXACT MATCH: Human command should resolve without any LLM call."""
        pytest.fail("""
        RED: Fast Path integration incomplete
        - turn_admission.py extracts _prefab_navigation_intent / _prefab_trello_read_intent
        - operational_resolution.py calls maybe_resolve_navigation() before durable task lookup
        - BUT: Agent context needs valid_tool_names with browser_navigate, browser_snapshot
        - BUT: workstation_durable_dispatch needs real browser session
        - BUT: Independent browser_snapshot verification not yet wired end-to-end
        """)

    def test_independent_snapshot_verification(self):
        """Navigation success requires INDEPENDENT browser_snapshot, not ack."""
        pytest.fail("""
        RED: engine.navigate() requires independent_read callback
        - Current: dispatch("browser_snapshot") after browser_navigate
        - Needed: Separate browser_snapshot call with fresh tab state
        - Verification: same_destination() on observed URL vs expected URL
        """)

    def test_toolset_disable_denial(self):
        """When browser toolset disabled, prefab should gracefully deny."""
        pytest.fail("""
        RED: maybe_resolve_navigation checks 'browser_navigate' in valid_tool_names
        - When toolset disabled, should return None (fallback to reasoning)
        - Should NOT attempt browser dispatch
        """)

    def test_no_hidden_profile_fallback(self):
        """Must not fall back to launch profile's credentials."""
        pytest.fail("""
        RED: TrelloClient uses os.getenv() directly - PROFILE LEAK
        - Must use agent.secret_scope.get_secret() for profile-scoped credentials
        - Each served profile must have its own TRELLO_API_KEY/TRELLO_TOKEN
        """)

    def test_official_api_preferred_over_browser(self):
        """Trello READ should use official REST API, not browser scraping."""
        pytest.fail("""
        RED: TrelloClient uses official API (api.trello.com)
        - Good: No browser cookies, no HTML parsing for reads
        - Needed: Cache with TTL, pagination, stable IDs
        - Needed: Explicit error on missing creds (not invented results)
        """)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])