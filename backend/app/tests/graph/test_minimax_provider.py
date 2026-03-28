"""Tests for MiniMax LLM provider integration."""

import os
from unittest.mock import patch

import pytest
from langchain_openai import ChatOpenAI

from app.core.graph.members import BaseNode, GraphMember, GraphTeam


class TestMiniMaxProviderInit:
    """Unit tests for MiniMax provider initialization in BaseNode."""

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_provider_creates_chat_openai(self) -> None:
        """MiniMax provider should create a ChatOpenAI instance."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=0.7,
        )
        assert isinstance(node.model, ChatOpenAI)

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_provider_default_base_url(self) -> None:
        """MiniMax provider should use default base_url when none is provided."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=0.7,
        )
        assert isinstance(node.model, ChatOpenAI)
        assert str(node.model.openai_api_base) == "https://api.minimax.io/v1"

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_provider_custom_base_url(self) -> None:
        """MiniMax provider should use custom base_url when provided."""
        custom_url = "https://custom-proxy.example.com/v1"
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=custom_url,
            temperature=0.7,
        )
        assert isinstance(node.model, ChatOpenAI)
        assert str(node.model.openai_api_base) == custom_url

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_provider_model_name(self) -> None:
        """MiniMax provider should pass the correct model name."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=0.7,
        )
        assert node.model.model_name == "MiniMax-M2.7"

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_provider_highspeed_model(self) -> None:
        """MiniMax provider should work with highspeed model variant."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7-highspeed",
            base_url=None,
            temperature=0.5,
        )
        assert node.model.model_name == "MiniMax-M2.7-highspeed"

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_provider_streaming_enabled(self) -> None:
        """MiniMax provider should have streaming enabled."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=0.7,
        )
        assert node.model.streaming is True

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_provider_api_key_from_env(self) -> None:
        """MiniMax provider should read API key from MINIMAX_API_KEY env var."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=0.7,
        )
        assert isinstance(node.model, ChatOpenAI)
        assert node.model.openai_api_key.get_secret_value() == "test-minimax-key-123"

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_final_answer_model_same_as_model(self) -> None:
        """final_answer_model should be the same as model for MiniMax provider."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=0.7,
        )
        assert node.final_answer_model is node.model


class TestMiniMaxTemperatureClamping:
    """Unit tests for MiniMax temperature clamping behavior."""

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_temperature_zero_clamped_to_min(self) -> None:
        """Temperature of 0.0 should be clamped to 0.01 for MiniMax."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=0.0,
        )
        assert node.model.temperature == pytest.approx(0.01)

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_temperature_normal_value(self) -> None:
        """Normal temperature values should pass through unchanged."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=0.7,
        )
        assert node.model.temperature == pytest.approx(0.7)

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_temperature_max_boundary(self) -> None:
        """Temperature of 1.0 should be accepted as-is."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=1.0,
        )
        assert node.model.temperature == pytest.approx(1.0)

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_temperature_above_max_clamped(self) -> None:
        """Temperature above 1.0 should be clamped to 1.0."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=1.5,
        )
        assert node.model.temperature == pytest.approx(1.0)

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_temperature_negative_clamped(self) -> None:
        """Negative temperature should be clamped to 0.01."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=-0.5,
        )
        assert node.model.temperature == pytest.approx(0.01)

    @patch.dict(os.environ, {"MINIMAX_API_KEY": "test-minimax-key-123"})
    def test_minimax_temperature_small_positive(self) -> None:
        """Small positive temperature should pass through."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=0.1,
        )
        assert node.model.temperature == pytest.approx(0.1)


class TestMiniMaxGraphModels:
    """Unit tests for MiniMax with GraphMember and GraphTeam models."""

    def test_graph_member_minimax_provider(self) -> None:
        """GraphMember should accept minimax as provider."""
        member = GraphMember(
            name="test-member",
            role="researcher",
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=0.7,
            backstory="A research assistant",
            tools=[],
            interrupt=False,
        )
        assert member.provider == "minimax"
        assert member.model == "MiniMax-M2.7"

    def test_graph_team_minimax_provider(self) -> None:
        """GraphTeam should accept minimax as provider."""
        team = GraphTeam(
            name="test-team",
            role="coordinator",
            backstory="A team coordinator",
            members={},
            provider="minimax",
            model="MiniMax-M2.7-highspeed",
            base_url=None,
            temperature=0.5,
        )
        assert team.provider == "minimax"
        assert team.model == "MiniMax-M2.7-highspeed"


class TestMiniMaxProviderIntegration:
    """Integration tests for MiniMax provider (require MINIMAX_API_KEY)."""

    @pytest.mark.skipif(
        not os.environ.get("MINIMAX_API_KEY"),
        reason="MINIMAX_API_KEY not set",
    )
    def test_minimax_provider_real_init(self) -> None:
        """Integration test: MiniMax provider initializes with real API key."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7",
            base_url=None,
            temperature=0.7,
        )
        assert isinstance(node.model, ChatOpenAI)
        assert node.model.model_name == "MiniMax-M2.7"

    @pytest.mark.skipif(
        not os.environ.get("MINIMAX_API_KEY"),
        reason="MINIMAX_API_KEY not set",
    )
    def test_minimax_highspeed_real_init(self) -> None:
        """Integration test: MiniMax highspeed model initializes correctly."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7-highspeed",
            base_url=None,
            temperature=0.5,
        )
        assert isinstance(node.model, ChatOpenAI)
        assert node.model.model_name == "MiniMax-M2.7-highspeed"

    @pytest.mark.skipif(
        not os.environ.get("MINIMAX_API_KEY"),
        reason="MINIMAX_API_KEY not set",
    )
    @pytest.mark.asyncio
    async def test_minimax_provider_basic_invoke(self) -> None:
        """Integration test: MiniMax provider can make a basic API call."""
        node = BaseNode(
            provider="minimax",
            model="MiniMax-M2.7-highspeed",
            base_url=None,
            temperature=0.7,
        )
        response = await node.model.ainvoke("Say 'hello' in one word.")
        assert response.content
        assert len(response.content) > 0
