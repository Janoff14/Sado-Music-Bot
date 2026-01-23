"""
Tests for donation handlers - comprehensive unit tests
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from sado_music_bot.donations.handlers import (
    _clean_note, on_donation_amount_selected, on_custom_amount,
    on_skip_note, on_donate_public, on_donate_anonymous,
    on_toggle_anon, on_confirm_donation, on_cancel_donation,
    DonationAmountState, router
)
from sado_music_bot.config import Config


@pytest.fixture
def mock_config():
    """Mock configuration"""
    return Config(
        bot_token="test_token",
        admin_id=12345,
        bot_username="test_bot",
        channel_pop="@test_pop",
        discussion_pop="@test_pop_disc",
    )


@pytest.fixture
def mock_db():
    """Mock database"""
    db = AsyncMock()
    return db


@pytest.fixture
def mock_bot():
    """Mock Telegram bot"""
    bot = AsyncMock()
    bot.send_message = AsyncMock(return_value=MagicMock(message_id=1000))
    bot.edit_message_text = AsyncMock()
    return bot


@pytest.fixture
def mock_state():
    """Mock FSM state"""
    state = AsyncMock()
    state.get_state = AsyncMock(return_value=None)
    state.set_state = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.update_data = AsyncMock()
    state.clear = AsyncMock()
    return state


@pytest.fixture
def sample_track():
    """Sample track tuple"""
    return (
        "trk_xyz789",       # track_id
        "art_abc123",       # artist_id
        "Test Song",        # title
        "Pop",              # genre
        "Test caption",     # caption
        "file_id_123",      # telegram_file_id
        12345,              # channel_message_id
        67890,              # discussion_anchor_message_id
        "ACTIVE"            # status
    )


@pytest.fixture
def sample_artist():
    """Sample artist tuple"""
    return (
        "art_abc123",           # artist_id
        99999,                  # tg_user_id
        "Test Artist",          # display_name
        "https://pay.me/test",  # payment_link
        None,                   # profile_url
        "Pop",                  # default_genre
        "Test bio"              # bio
    )


@pytest.fixture
def sample_donation():
    """Sample donation tuple"""
    return (
        "don_test123",      # donation_id
        "trk_xyz789",       # track_id
        "art_abc123",       # artist_id
        99999,              # donor_user_id
        "Test User",        # donor_name
        "testuser",         # donor_username
        10000,              # amount
        None,               # note
        0,                  # is_anonymous
        "CREATED"           # status
    )


@pytest.fixture
def mock_callback():
    """Mock callback query"""
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = 99999
    cb.from_user.full_name = "Test User"
    cb.from_user.username = "testuser"
    cb.data = ""
    cb.message = MagicMock()
    cb.message.edit_text = AsyncMock()
    cb.message.answer = AsyncMock()
    cb.message.message_id = 12345
    cb.answer = AsyncMock()
    return cb


@pytest.fixture
def mock_message():
    """Mock message"""
    msg = MagicMock()
    msg.from_user = MagicMock()
    msg.from_user.id = 99999
    msg.from_user.full_name = "Test User"
    msg.from_user.username = "testuser"
    msg.chat = MagicMock()
    msg.chat.id = 99999
    msg.text = ""
    msg.answer = AsyncMock()
    return msg


class TestCleanNote:
    """Tests for _clean_note helper function"""

    def test_removes_https_links(self):
        """Test HTTPS URLs are removed"""
        result = _clean_note("Check out https://example.com please")
        assert "https://example.com" not in result
        assert "Check out" in result
        assert "please" in result

    def test_removes_http_links(self):
        """Test HTTP links are removed"""
        result = _clean_note("Visit http://bad-link.com now")
        assert "http://bad-link.com" not in result
        assert "Visit" in result

    def test_limits_length_to_120(self):
        """Test note is limited to 120 characters"""
        long_text = "A" * 200
        result = _clean_note(long_text)
        assert len(result) <= 120

    def test_strips_whitespace(self):
        """Test leading/trailing whitespace is stripped"""
        result = _clean_note("  Hello world  ")
        assert result == "Hello world"

    def test_normalizes_multiple_spaces(self):
        """Test multiple spaces are collapsed to single space"""
        result = _clean_note("Hello    world")
        assert result == "Hello world"

    def test_empty_string_returns_none(self):
        """Test empty string returns None"""
        assert _clean_note("") is None

    def test_whitespace_only_returns_none(self):
        """Test whitespace-only string returns None"""
        assert _clean_note("   ") is None

    def test_only_link_returns_none(self):
        """Test string with only link returns None"""
        result = _clean_note("https://example.com")
        assert result is None

    def test_preserves_emojis(self):
        """Test emojis are preserved"""
        result = _clean_note("Great song! 🎵❤️")
        assert "🎵" in result
        assert "❤️" in result


class TestDonationRouterSetup:
    """Tests for donation router configuration"""

    def test_router_exists(self):
        """Test router is defined"""
        assert router is not None

    def test_router_has_handlers(self):
        """Test router has callback and message handlers"""
        assert len(router.callback_query.handlers) > 0 or len(router.message.handlers) > 0


class TestOnDonationAmountSelected:
    """Tests for donation amount selection handler"""

    @pytest.mark.asyncio
    async def test_invalid_data_format_shows_error(self, mock_callback, mock_db, mock_state):
        """Test invalid callback data shows error"""
        mock_callback.data = "donamtsel:invalid"  # Missing amount

        await on_donation_amount_selected(mock_callback, mock_db, mock_state)

        mock_callback.answer.assert_called_with("Invalid data", show_alert=True)

    @pytest.mark.asyncio
    async def test_custom_amount_sets_waiting_state(self, mock_callback, mock_db, mock_state):
        """Test custom amount selection sets FSM state"""
        mock_callback.data = "donamtsel:trk_123:custom"

        await on_donation_amount_selected(mock_callback, mock_db, mock_state)

        mock_state.update_data.assert_called_with(donation_track_id="trk_123")
        mock_state.set_state.assert_called_with(DonationAmountState.waiting_custom_amount)
        mock_callback.message.edit_text.assert_called()

    @pytest.mark.asyncio
    async def test_invalid_amount_string_shows_error(self, mock_callback, mock_db, mock_state):
        """Test non-numeric amount shows error"""
        mock_callback.data = "donamtsel:trk_123:notanumber"

        await on_donation_amount_selected(mock_callback, mock_db, mock_state)

        mock_callback.answer.assert_called_with("Invalid amount", show_alert=True)

    @pytest.mark.asyncio
    async def test_valid_amount_creates_donation(self, mock_callback, mock_db, mock_state, sample_track, sample_artist):
        """Test valid amount creates donation and proceeds"""
        mock_callback.data = "donamtsel:trk_xyz789:10000"
        mock_db.get_track = AsyncMock(return_value=sample_track)
        mock_db.get_artist = AsyncMock(return_value=sample_artist)
        mock_db.create_donation = AsyncMock(return_value="don_new123")

        await on_donation_amount_selected(mock_callback, mock_db, mock_state)

        # Should create donation
        mock_db.create_donation.assert_called_once()

        # Should show note options
        mock_callback.message.edit_text.assert_called()

    @pytest.mark.asyncio
    async def test_track_not_found_shows_error(self, mock_callback, mock_db, mock_state):
        """Test track not found shows error"""
        mock_callback.data = "donamtsel:trk_unknown:10000"
        mock_db.get_track = AsyncMock(return_value=None)

        await on_donation_amount_selected(mock_callback, mock_db, mock_state)

        mock_callback.answer.assert_called_with("Track not found", show_alert=True)

    @pytest.mark.asyncio
    async def test_inactive_track_shows_error(self, mock_callback, mock_db, mock_state):
        """Test inactive track shows error"""
        mock_callback.data = "donamtsel:trk_xyz789:10000"
        inactive_track = ("trk_xyz789", "art_123", "Song", "Pop", None, "file", 123, 456, "INACTIVE")
        mock_db.get_track = AsyncMock(return_value=inactive_track)

        await on_donation_amount_selected(mock_callback, mock_db, mock_state)

        mock_callback.answer.assert_called_with("Track is no longer active", show_alert=True)


class TestOnCustomAmount:
    """Tests for custom amount input handler"""

    @pytest.mark.asyncio
    async def test_ignores_commands(self, mock_message, mock_db, mock_state):
        """Test slash commands are ignored"""
        mock_message.text = "/cancel"

        await on_custom_amount(mock_message, mock_db, mock_state)

        mock_message.answer.assert_not_called()

    @pytest.mark.asyncio
    async def test_minimum_amount_validation(self, mock_message, mock_db, mock_state):
        """Test amounts below 1000 are rejected"""
        mock_message.text = "500"

        await on_custom_amount(mock_message, mock_db, mock_state)

        mock_message.answer.assert_called()
        call_text = mock_message.answer.call_args[0][0]
        assert "1 000" in call_text or "minimum" in call_text.lower()

    @pytest.mark.asyncio
    async def test_maximum_amount_validation(self, mock_message, mock_db, mock_state):
        """Test amounts above 1000000 are rejected"""
        mock_message.text = "2000000"

        await on_custom_amount(mock_message, mock_db, mock_state)

        mock_message.answer.assert_called()
        call_text = mock_message.answer.call_args[0][0]
        assert "1 000 000" in call_text or "maximum" in call_text.lower()

    @pytest.mark.asyncio
    async def test_invalid_number_shows_error(self, mock_message, mock_db, mock_state):
        """Test non-numeric input shows error"""
        mock_message.text = "not a number"

        await on_custom_amount(mock_message, mock_db, mock_state)

        mock_message.answer.assert_called()
        call_text = mock_message.answer.call_args[0][0]
        assert "valid number" in call_text.lower() or "❌" in call_text

    @pytest.mark.asyncio
    async def test_expired_session_clears_state(self, mock_message, mock_db, mock_state):
        """Test expired session (no track_id) clears state"""
        mock_message.text = "10000"
        mock_state.get_data = AsyncMock(return_value={})  # No track_id

        await on_custom_amount(mock_message, mock_db, mock_state)

        mock_message.answer.assert_called()
        call_text = mock_message.answer.call_args[0][0]
        assert "expired" in call_text.lower()
        mock_state.clear.assert_called()

    @pytest.mark.asyncio
    async def test_successful_amount_creates_donation(self, mock_message, mock_db, mock_state, sample_track, sample_artist):
        """Test valid amount creates donation and clears state"""
        mock_message.text = "15000"
        mock_state.get_data = AsyncMock(return_value={"donation_track_id": "trk_xyz789"})
        mock_db.get_track = AsyncMock(return_value=sample_track)
        mock_db.get_artist = AsyncMock(return_value=sample_artist)
        mock_db.create_donation = AsyncMock(return_value="don_new123")

        await on_custom_amount(mock_message, mock_db, mock_state)

        # Should create donation
        mock_db.create_donation.assert_called_once()

        # Should clear state after creation
        mock_state.clear.assert_called()

        # Should show success message
        mock_message.answer.assert_called()

    @pytest.mark.asyncio
    async def test_parses_comma_formatted_amount(self, mock_message, mock_db, mock_state, sample_track, sample_artist):
        """Test amounts with commas are parsed correctly"""
        mock_message.text = "10,000"
        mock_state.get_data = AsyncMock(return_value={"donation_track_id": "trk_xyz789"})
        mock_db.get_track = AsyncMock(return_value=sample_track)
        mock_db.get_artist = AsyncMock(return_value=sample_artist)
        mock_db.create_donation = AsyncMock(return_value="don_test")

        await on_custom_amount(mock_message, mock_db, mock_state)

        mock_db.create_donation.assert_called_once()

    @pytest.mark.asyncio
    async def test_parses_space_formatted_amount(self, mock_message, mock_db, mock_state, sample_track, sample_artist):
        """Test amounts with spaces are parsed correctly"""
        mock_message.text = "10 000"
        mock_state.get_data = AsyncMock(return_value={"donation_track_id": "trk_xyz789"})
        mock_db.get_track = AsyncMock(return_value=sample_track)
        mock_db.get_artist = AsyncMock(return_value=sample_artist)
        mock_db.create_donation = AsyncMock(return_value="don_test")

        await on_custom_amount(mock_message, mock_db, mock_state)

        mock_db.create_donation.assert_called_once()


class TestOnSkipNote:
    """Tests for skip note handler"""

    @pytest.mark.asyncio
    async def test_skipping_note_shows_anonymity_options(self, mock_callback, mock_db, sample_donation):
        """Test skipping note proceeds to anonymity selection"""
        mock_callback.data = "don_skip_note:don_test123"
        mock_db.get_donation = AsyncMock(return_value=sample_donation)

        await on_skip_note(mock_callback, mock_db)

        mock_callback.message.edit_text.assert_called()
        call_text = mock_callback.message.edit_text.call_args[0][0]
        assert "visibility" in call_text.lower() or "anonymous" in call_text.lower()

    @pytest.mark.asyncio
    async def test_donation_not_found_shows_error(self, mock_callback, mock_db):
        """Test missing donation shows error"""
        mock_callback.data = "don_skip_note:don_unknown"
        mock_db.get_donation = AsyncMock(return_value=None)

        await on_skip_note(mock_callback, mock_db)

        mock_callback.answer.assert_called_with("Not found", show_alert=True)


class TestOnToggleAnon:
    """Tests for toggle anonymity handler"""

    @pytest.mark.asyncio
    async def test_toggles_anonymity(self, mock_callback, mock_db, sample_donation, sample_track, sample_artist):
        """Test toggling anonymity updates donation"""
        mock_callback.data = "don_anon:don_test123"
        mock_db.get_donation = AsyncMock(return_value=sample_donation)
        mock_db.toggle_donation_anon = AsyncMock(return_value=1)  # Now anonymous
        mock_db.get_track = AsyncMock(return_value=sample_track)
        mock_db.get_artist = AsyncMock(return_value=sample_artist)
        mock_db.set_anon_default = AsyncMock()

        await on_toggle_anon(mock_callback, mock_db)

        mock_db.toggle_donation_anon.assert_called_with("don_test123")
        mock_callback.answer.assert_called_with("Updated.")

    @pytest.mark.asyncio
    async def test_not_editable_if_not_created(self, mock_callback, mock_db, sample_donation):
        """Test cannot toggle if donation not in CREATED status"""
        mock_callback.data = "don_anon:don_test123"
        confirmed = list(sample_donation)
        confirmed[9] = "CONFIRMED"
        mock_db.get_donation = AsyncMock(return_value=tuple(confirmed))

        await on_toggle_anon(mock_callback, mock_db)

        mock_callback.answer.assert_called_with("Not editable.", show_alert=True)


class TestOnConfirmDonation:
    """Tests for donation confirmation handler"""

    @pytest.mark.asyncio
    async def test_confirms_donation(self, mock_callback, mock_bot, mock_config, mock_db, sample_donation, sample_track, sample_artist):
        """Test confirming donation updates status and notifies artist"""
        mock_callback.data = "don_ok:don_test123"
        mock_db.get_donation = AsyncMock(return_value=sample_donation)
        mock_db.set_donation_status = AsyncMock()
        mock_db.get_track = AsyncMock(return_value=sample_track)
        mock_db.get_artist = AsyncMock(return_value=sample_artist)

        await on_confirm_donation(mock_callback, mock_bot, mock_config, mock_db)

        # Status should be updated
        mock_db.set_donation_status.assert_called_with("don_test123", "CONFIRMED")

        # Artist should be notified
        mock_bot.send_message.assert_called()

        # Success message shown
        mock_callback.answer.assert_called_with("Confirmed ✅")

    @pytest.mark.asyncio
    async def test_already_confirmed_shows_error(self, mock_callback, mock_bot, mock_config, mock_db, sample_donation):
        """Test already confirmed donation shows error"""
        mock_callback.data = "don_ok:don_test123"
        confirmed = list(sample_donation)
        confirmed[9] = "CONFIRMED"
        mock_db.get_donation = AsyncMock(return_value=tuple(confirmed))

        await on_confirm_donation(mock_callback, mock_bot, mock_config, mock_db)

        mock_callback.answer.assert_called_with("Already processed.", show_alert=True)


class TestOnCancelDonation:
    """Tests for donation cancellation handler"""

    @pytest.mark.asyncio
    async def test_cancels_donation(self, mock_callback, mock_db, sample_donation):
        """Test canceling donation updates status"""
        mock_callback.data = "don_cancel:don_test123"
        mock_db.get_donation = AsyncMock(return_value=sample_donation)
        mock_db.set_donation_status = AsyncMock()

        await on_cancel_donation(mock_callback, mock_db)

        mock_db.set_donation_status.assert_called_with("don_test123", "CANCELED")
        mock_callback.answer.assert_called_with("Canceled.")

    @pytest.mark.asyncio
    async def test_already_processed_shows_error(self, mock_callback, mock_db, sample_donation):
        """Test already processed donation cannot be canceled"""
        mock_callback.data = "don_cancel:don_test123"
        confirmed = list(sample_donation)
        confirmed[9] = "CONFIRMED"
        mock_db.get_donation = AsyncMock(return_value=tuple(confirmed))

        await on_cancel_donation(mock_callback, mock_db)

        mock_callback.answer.assert_called_with("Already processed.", show_alert=True)

