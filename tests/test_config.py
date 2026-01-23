"""
Tests for configuration module
"""
import os
import pytest
from unittest.mock import patch

from sado_music_bot.config import (
    Config, load_config, _parse_chat_id,
    get_channel_for_genre, get_discussion_for_genre,
    GENRE_CHANNELS, GENRE_DISCUSSIONS
)


class TestParseChartId:
    """Tests for _parse_chat_id function"""

    def test_parse_numeric_id(self):
        """Test parsing numeric chat IDs"""
        assert _parse_chat_id("-1001234567890") == -1001234567890
        assert _parse_chat_id("12345") == 12345

    def test_parse_username(self):
        """Test parsing @username format"""
        assert _parse_chat_id("@my_channel") == "@my_channel"
        assert _parse_chat_id("@test_group") == "@test_group"

    def test_parse_empty(self):
        """Test parsing empty strings"""
        assert _parse_chat_id("") == 0
        assert _parse_chat_id("   ") == 0

    def test_parse_with_whitespace(self):
        """Test parsing with surrounding whitespace"""
        assert _parse_chat_id("  @my_channel  ") == "@my_channel"
        assert _parse_chat_id("  12345  ") == 12345


class TestLoadConfig:
    """Tests for load_config function"""

    def test_missing_bot_token(self):
        """Test that missing BOT_TOKEN raises error"""
        with patch.dict(os.environ, {"BOT_TOKEN": "", "ADMIN_ID": "12345"}, clear=True):
            with pytest.raises(RuntimeError, match="BOT_TOKEN is missing"):
                load_config()

    def test_missing_admin_id(self):
        """Test that missing ADMIN_ID raises error"""
        with patch.dict(os.environ, {"BOT_TOKEN": "test_token", "ADMIN_ID": "0"}, clear=True):
            with pytest.raises(RuntimeError, match="ADMIN_ID is missing"):
                load_config()

    def test_valid_config(self):
        """Test loading valid configuration"""
        env_vars = {
            "BOT_TOKEN": "test_token_123",
            "ADMIN_ID": "12345",
            "BOT_USERNAME": "test_bot",
            "APP_NAME": "Test App",
            "MAX_DONATIONS_PER_HOUR": "10",
            "CHANNEL_POP": "@pop_channel",
            "DISCUSSION_POP": "@pop_discussion",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            cfg = load_config()
            assert cfg.bot_token == "test_token_123"
            assert cfg.admin_id == 12345
            assert cfg.bot_username == "test_bot"
            assert cfg.app_name == "Test App"
            assert cfg.max_donations_per_hour == 10
            assert cfg.channel_pop == "@pop_channel"
            assert cfg.discussion_pop == "@pop_discussion"

    def test_default_values(self):
        """Test default values are applied"""
        env_vars = {
            "BOT_TOKEN": "test_token",
            "ADMIN_ID": "12345",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            cfg = load_config()
            assert cfg.app_name == "Sado Music"
            assert cfg.max_donations_per_hour == 5
            assert cfg.channel_pop == ""


class TestGetChannelForGenre:
    """Tests for get_channel_for_genre function"""

    def test_pop_genre(self, mock_config):
        """Test getting channel for Pop genre"""
        result = get_channel_for_genre(mock_config, "Pop")
        assert result == "@test_pop_channel"

    def test_rock_genre(self, mock_config):
        """Test getting channel for Rock genre"""
        result = get_channel_for_genre(mock_config, "Rock")
        assert result == "@test_rock_channel"

    def test_hiphop_genre(self, mock_config):
        """Test getting channel for Hip Hop genre"""
        result = get_channel_for_genre(mock_config, "Hip Hop")
        assert result == "@test_hiphop_channel"

    def test_rap_maps_to_hiphop(self, mock_config):
        """Test that Rap maps to Hip Hop channel"""
        result = get_channel_for_genre(mock_config, "Rap")
        assert result == "@test_hiphop_channel"

    def test_indie_maps_to_discovery(self, mock_config):
        """Test that Indie maps to Discovery channel"""
        result = get_channel_for_genre(mock_config, "Indie")
        assert result == "@test_discovery_channel"

    def test_unknown_genre_defaults_to_discovery(self, mock_config):
        """Test unknown genre defaults to discovery channel"""
        result = get_channel_for_genre(mock_config, "Unknown")
        assert result == "@test_discovery_channel"

    def test_unconfigured_channel_returns_zero(self):
        """Test that unconfigured channel returns 0"""
        cfg = Config(
            bot_token="test",
            admin_id=12345,
            channel_pop="",  # Not configured
        )
        result = get_channel_for_genre(cfg, "Pop")
        assert result == 0


class TestGetDiscussionForGenre:
    """Tests for get_discussion_for_genre function"""

    def test_pop_discussion(self, mock_config):
        """Test getting discussion group for Pop genre"""
        result = get_discussion_for_genre(mock_config, "Pop")
        assert result == "@test_pop_discussion"

    def test_rock_discussion(self, mock_config):
        """Test getting discussion group for Rock genre"""
        result = get_discussion_for_genre(mock_config, "Rock")
        assert result == "@test_rock_discussion"

    def test_unconfigured_discussion_returns_zero(self):
        """Test that unconfigured discussion returns 0"""
        cfg = Config(
            bot_token="test",
            admin_id=12345,
            discussion_pop="",  # Not configured
        )
        result = get_discussion_for_genre(cfg, "Pop")
        assert result == 0


class TestGenreMappings:
    """Tests for genre mapping dictionaries"""

    def test_all_genres_have_channel_mapping(self):
        """Verify all expected genres have channel mappings"""
        expected_genres = ["Pop", "Rock", "Hip Hop", "Rap", "Indie", "Electronic", "Other"]
        for genre in expected_genres:
            assert genre in GENRE_CHANNELS, f"Missing channel mapping for {genre}"

    def test_all_genres_have_discussion_mapping(self):
        """Verify all expected genres have discussion mappings"""
        expected_genres = ["Pop", "Rock", "Hip Hop", "Rap", "Indie", "Electronic", "Other"]
        for genre in expected_genres:
            assert genre in GENRE_DISCUSSIONS, f"Missing discussion mapping for {genre}"

