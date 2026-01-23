"""
Pytest configuration and fixtures for Sado Music Bot tests
"""
import os
import sys
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sado_music_bot.config import Config


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return Config(
        bot_token="test_token_123",
        admin_id=12345,
        bot_username="test_bot",
        app_name="Test Sado Music",
        max_donations_per_hour=5,
        channel_pop="@test_pop_channel",
        channel_rock="@test_rock_channel",
        channel_hiphop="@test_hiphop_channel",
        channel_discovery="@test_discovery_channel",
        discussion_pop="@test_pop_discussion",
        discussion_rock="@test_rock_discussion",
        discussion_hiphop="@test_hiphop_discussion",
        discussion_discovery="@test_discovery_discussion",
    )


@pytest.fixture
def mock_db():
    """Mock database for testing"""
    db = MagicMock()

    # Make all methods async
    db.init = AsyncMock()
    db.get_lang = AsyncMock(return_value="uz")
    db.set_lang = AsyncMock()
    db.get_anon_default = AsyncMock(return_value=0)
    db.set_anon_default = AsyncMock()
    db.upsert_artist = AsyncMock()
    db.get_artist = AsyncMock(return_value=None)
    db.get_artist_by_tg = AsyncMock(return_value=None)
    db.update_artist_field = AsyncMock()
    db.create_submission = AsyncMock()
    db.get_submission = AsyncMock(return_value=None)
    db.set_submission_admin_message = AsyncMock()
    db.set_submission_status = AsyncMock()
    db.insert_track = AsyncMock()
    db.get_track = AsyncMock(return_value=None)
    db.list_artist_tracks = AsyncMock(return_value=[])
    db.list_artist_tracks_with_file = AsyncMock(return_value=[])
    db.count_artist_tracks = AsyncMock(return_value=0)
    db.create_donation = AsyncMock(return_value="don_test123")
    db.get_donation = AsyncMock(return_value=None)
    db.set_donation_note = AsyncMock()
    db.toggle_donation_anon = AsyncMock(return_value=1)
    db.set_donation_status = AsyncMock()
    db.count_recent_confirmed = AsyncMock(return_value=0)

    return db


@pytest.fixture
def mock_bot():
    """Mock Telegram bot"""
    bot = MagicMock()
    bot.send_message = AsyncMock()
    bot.send_audio = AsyncMock()
    bot.edit_message_text = AsyncMock()
    bot.get_me = AsyncMock(return_value=MagicMock(username="test_bot"))
    return bot


@pytest.fixture
def mock_message():
    """Mock Telegram message"""
    msg = MagicMock()
    msg.from_user = MagicMock()
    msg.from_user.id = 99999
    msg.from_user.full_name = "Test User"
    msg.from_user.username = "testuser"
    msg.chat = MagicMock()
    msg.chat.id = 99999
    msg.text = ""
    msg.answer = AsyncMock()
    msg.answer_audio = AsyncMock()
    return msg


@pytest.fixture
def mock_callback():
    """Mock Telegram callback query"""
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = 99999
    cb.from_user.full_name = "Test User"
    cb.from_user.username = "testuser"
    cb.data = ""
    cb.message = MagicMock()
    cb.message.edit_text = AsyncMock()
    cb.message.edit_caption = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.message.message_id = 12345
    cb.answer = AsyncMock()
    return cb


@pytest.fixture
def mock_state():
    """Mock FSM state context"""
    state = MagicMock()
    state.get_state = AsyncMock(return_value=None)
    state.set_state = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.update_data = AsyncMock()
    state.clear = AsyncMock()
    return state


@pytest.fixture
def sample_artist():
    """Sample artist tuple from database"""
    return (
        "art_abc123",      # artist_id
        99999,             # tg_user_id
        "Test Artist",     # display_name
        "https://pay.me/test",  # payment_link
        None,              # profile_url
        "Pop",             # default_genre
        "Test bio"         # bio
    )


@pytest.fixture
def sample_track():
    """Sample track tuple from database"""
    return (
        "trk_xyz789",      # track_id
        "art_abc123",      # artist_id
        "Test Song",       # title
        "Pop",             # genre
        "Test caption",    # caption
        "file_id_123",     # telegram_file_id
        12345,             # channel_message_id
        67890,             # discussion_anchor_message_id
        "ACTIVE"           # status
    )


@pytest.fixture
def sample_donation():
    """Sample donation tuple from database"""
    return (
        "don_test123",     # donation_id
        "trk_xyz789",      # track_id
        "art_abc123",      # artist_id
        99999,             # donor_user_id
        "Test User",       # donor_name
        "testuser",        # donor_username
        10000,             # amount
        "Great song!",     # note
        0,                 # is_anonymous
        "CREATED"          # status
    )


@pytest.fixture
def sample_submission():
    """Sample submission tuple from database"""
    return (
        "sub_test456",     # submission_id
        "art_abc123",      # artist_id
        99999,             # submitter_user_id
        "New Track",       # title
        "Rock",            # genre
        "A new rock song", # caption
        "file_id_456",     # telegram_file_id
        "PENDING",         # status
        None               # admin_message_id
    )

