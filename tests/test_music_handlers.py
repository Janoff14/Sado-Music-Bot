"""
Tests for music handlers - comprehensive unit tests
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from sado_music_bot.music.handlers import (
    cmd_start, cmd_profile, cmd_submit, cmd_cancel, cmd_help, cmd_chatid,
    on_lang_choice, onboard_name, onboard_paylink, onboard_bio,
    sub_audio, sub_title, sub_caption,
    OnboardingStates, SubmitStates, ProfileEditStates, router
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
    bot.send_audio = AsyncMock(return_value=MagicMock(message_id=999))
    bot.send_message = AsyncMock(return_value=MagicMock(message_id=1000))
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
def mock_message():
    """Mock Telegram message"""
    msg = MagicMock()
    msg.from_user = MagicMock()
    msg.from_user.id = 99999
    msg.from_user.full_name = "Test User"
    msg.from_user.username = "testuser"
    msg.chat = MagicMock()
    msg.chat.id = 99999
    msg.text = "/start"
    msg.answer = AsyncMock()
    msg.answer_audio = AsyncMock()
    return msg


@pytest.fixture
def mock_callback():
    """Mock callback query"""
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = 99999
    cb.from_user.full_name = "Test User"
    cb.data = ""
    cb.message = MagicMock()
    cb.message.edit_text = AsyncMock()
    cb.answer = AsyncMock()
    return cb


class TestMusicHandlerStates:
    """Tests for FSM states"""

    def test_onboarding_states_exist(self):
        """Test onboarding states are defined"""
        assert OnboardingStates.waiting_name is not None
        assert OnboardingStates.waiting_payment_link is not None
        assert OnboardingStates.waiting_genre is not None
        assert OnboardingStates.waiting_bio is not None

    def test_submit_states_exist(self):
        """Test submission states are defined"""
        assert SubmitStates.waiting_audio is not None
        assert SubmitStates.waiting_title is not None
        assert SubmitStates.waiting_genre is not None
        assert SubmitStates.waiting_caption is not None

    def test_profile_edit_states_exist(self):
        """Test profile edit states are defined"""
        assert ProfileEditStates.waiting_value is not None


class TestMusicHandlerRouterSetup:
    """Tests for router configuration"""

    def test_router_exists(self):
        """Test router is defined"""
        assert router is not None

    def test_router_has_handlers(self):
        """Test router has message and callback handlers"""
        assert len(router.message.handlers) > 0 or len(router.callback_query.handlers) > 0


class TestCmdStart:
    """Tests for /start command handler"""

    @pytest.mark.asyncio
    async def test_new_user_sees_welcome(self, mock_message, mock_db, mock_config):
        """Test new user sees welcome message with language selection"""
        mock_db.get_artist_by_tg = AsyncMock(return_value=None)
        mock_db.get_lang = AsyncMock(return_value="uz")

        await cmd_start(mock_message, mock_db, mock_config)

        mock_message.answer.assert_called()
        call_args = mock_message.answer.call_args
        text = call_args[0][0]
        # Accept both English and Uzbek language selection prompt
        assert "Welcome" in text or "Sado Music" in text or "tanlang" in text or "Выберите" in text
        # Should have language selection keyboard
        assert call_args[1].get('reply_markup') is not None

    @pytest.mark.asyncio
    async def test_existing_artist_sees_menu(self, mock_message, mock_db, mock_config, sample_artist):
        """Test existing artist sees command menu"""
        mock_db.get_artist_by_tg = AsyncMock(return_value=sample_artist)
        mock_db.get_lang = AsyncMock(return_value="uz")

        await cmd_start(mock_message, mock_db, mock_config)

        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        # Accept both English and Uzbek welcome message
        assert "/submit" in text or "/profile" in text or "Salom" in text or "SadoMusicBot" in text

    @pytest.mark.asyncio
    async def test_donate_deep_link_shows_amounts(self, mock_message, mock_db, mock_config, sample_track, sample_artist):
        """Test donate deep link shows donation amount selection"""
        mock_message.text = "/start donate_trk_xyz789"
        mock_db.get_track = AsyncMock(return_value=sample_track)
        mock_db.get_artist = AsyncMock(return_value=sample_artist)

        await cmd_start(mock_message, mock_db, mock_config)

        mock_message.answer.assert_called()
        call_args = mock_message.answer.call_args
        # Should have amount selection keyboard
        assert call_args[1].get('reply_markup') is not None

    @pytest.mark.asyncio
    async def test_donate_deep_link_track_not_found(self, mock_message, mock_db, mock_config):
        """Test donate deep link with unknown track shows error"""
        mock_message.text = "/start donate_unknown"
        mock_db.get_track = AsyncMock(return_value=None)

        await cmd_start(mock_message, mock_db, mock_config)

        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        assert "not found" in text.lower()

    @pytest.mark.asyncio
    async def test_artist_deep_link_shows_profile(self, mock_message, mock_db, mock_config, sample_artist):
        """Test artist deep link shows artist profile"""
        mock_message.text = "/start artist_art_abc123"
        mock_db.get_artist = AsyncMock(return_value=sample_artist)
        mock_db.count_artist_tracks = AsyncMock(return_value=5)
        mock_db.list_artist_tracks_with_file = AsyncMock(return_value=[])

        await cmd_start(mock_message, mock_db, mock_config)

        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        assert "Test Artist" in text

    @pytest.mark.asyncio
    async def test_artist_deep_link_not_found(self, mock_message, mock_db, mock_config):
        """Test artist deep link with unknown artist shows error"""
        mock_message.text = "/start artist_unknown"
        mock_db.get_artist = AsyncMock(return_value=None)

        await cmd_start(mock_message, mock_db, mock_config)

        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        assert "not found" in text.lower()

    @pytest.mark.asyncio
    async def test_handles_missing_from_user(self, mock_message, mock_db, mock_config):
        """Test handler gracefully handles missing from_user"""
        mock_message.from_user = None

        result = await cmd_start(mock_message, mock_db, mock_config)

        mock_message.answer.assert_not_called()


class TestCmdProfile:
    """Tests for /profile command handler"""

    @pytest.mark.asyncio
    async def test_no_profile_shows_message(self, mock_message, mock_db):
        """Test user without profile sees helpful message"""
        mock_db.get_artist_by_tg = AsyncMock(return_value=None)

        await cmd_profile(mock_message, mock_db)

        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        assert "No profile" in text or "/submit" in text

    @pytest.mark.asyncio
    async def test_shows_profile_with_edit_buttons(self, mock_message, mock_db, sample_artist):
        """Test existing profile is shown with edit options"""
        mock_db.get_artist_by_tg = AsyncMock(return_value=sample_artist)
        mock_db.list_artist_tracks = AsyncMock(return_value=[])

        await cmd_profile(mock_message, mock_db)

        mock_message.answer.assert_called()
        call_args = mock_message.answer.call_args
        text = call_args[0][0]
        assert "Test Artist" in text
        # Should have edit buttons
        assert call_args[1].get('reply_markup') is not None


class TestCmdSubmit:
    """Tests for /submit command handler"""

    @pytest.mark.asyncio
    async def test_new_artist_starts_onboarding(self, mock_message, mock_db, mock_state):
        """Test new artist starts onboarding flow"""
        mock_db.get_artist_by_tg = AsyncMock(return_value=None)

        await cmd_submit(mock_message, mock_db, mock_state)

        mock_state.set_state.assert_called_with(OnboardingStates.waiting_name)
        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        assert "artist" in text.lower() or "name" in text.lower()

    @pytest.mark.asyncio
    async def test_existing_artist_goes_to_audio(self, mock_message, mock_db, mock_state, sample_artist):
        """Test existing artist goes straight to audio upload"""
        mock_db.get_artist_by_tg = AsyncMock(return_value=sample_artist)

        await cmd_submit(mock_message, mock_db, mock_state)

        mock_state.set_state.assert_called_with(SubmitStates.waiting_audio)
        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        assert "audio" in text.lower() or "file" in text.lower()


class TestCmdCancel:
    """Tests for /cancel command handler"""

    @pytest.mark.asyncio
    async def test_cancel_with_active_state(self, mock_message, mock_db, mock_state):
        """Test cancel with active FSM state shows 'Cancelled'"""
        mock_state.get_state = AsyncMock(return_value="some_state")
        mock_db.get_lang = AsyncMock(return_value="uz")

        await cmd_cancel(mock_message, mock_db, mock_state)

        mock_state.clear.assert_called()
        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        # Accept both English and Uzbek
        assert "Cancelled" in text or "Bekor" in text or "cancelled" in text.lower()

    @pytest.mark.asyncio
    async def test_cancel_without_active_state(self, mock_message, mock_db, mock_state):
        """Test cancel without active state shows cancelled message"""
        mock_state.get_state = AsyncMock(return_value=None)
        mock_db.get_lang = AsyncMock(return_value="uz")

        await cmd_cancel(mock_message, mock_db, mock_state)

        mock_state.clear.assert_called()
        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        # Accept both English and Uzbek
        assert "cancel" in text.lower() or "Bekor" in text


class TestCmdHelp:
    """Tests for /help command handler"""

    @pytest.mark.asyncio
    async def test_shows_help_with_commands(self, mock_message, mock_db):
        """Test help message shows available commands"""
        mock_db.get_lang = AsyncMock(return_value="uz")

        await cmd_help(mock_message, mock_db)

        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        # Accept Uzbek help text
        assert "/start" in text or "/help" in text or "Buyruqlar" in text or "Список" in text


class TestCmdChatId:
    """Tests for /chatid command handler"""

    @pytest.mark.asyncio
    async def test_shows_chat_id(self, mock_message):
        """Test chatid command shows current chat ID"""
        mock_message.chat.id = -1001234567890

        await cmd_chatid(mock_message)

        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        assert "-1001234567890" in text


class TestOnLangChoice:
    """Tests for language selection callback"""

    @pytest.mark.asyncio
    async def test_sets_uzbek_language(self, mock_callback, mock_db):
        """Test selecting Uzbek language"""
        mock_callback.data = "lang:uz"

        await on_lang_choice(mock_callback, mock_db)

        mock_db.set_lang.assert_called_with(99999, "uz")
        mock_callback.message.edit_text.assert_called()
        mock_callback.answer.assert_called()

    @pytest.mark.asyncio
    async def test_sets_russian_language(self, mock_callback, mock_db):
        """Test selecting Russian language"""
        mock_callback.data = "lang:ru"

        await on_lang_choice(mock_callback, mock_db)

        mock_db.set_lang.assert_called_with(99999, "ru")

    @pytest.mark.asyncio
    async def test_invalid_language_shows_error(self, mock_callback, mock_db):
        """Test invalid language selection shows error"""
        mock_callback.data = "lang:invalid"

        await on_lang_choice(mock_callback, mock_db)

        mock_callback.answer.assert_called()
        # Accept both English and Uzbek error messages
        call_args = mock_callback.answer.call_args[0][0]
        assert "Invalid" in call_args or "Noto'g'ri" in call_args or "invalid" in call_args.lower()


class TestOnboardingFlow:
    """Tests for artist onboarding flow"""

    @pytest.mark.asyncio
    async def test_onboard_name_short_name_rejected(self, mock_message, mock_state):
        """Test names shorter than 2 chars are rejected"""
        mock_message.text = "A"

        await onboard_name(mock_message, mock_state)

        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        assert "short" in text.lower()

    @pytest.mark.asyncio
    async def test_onboard_name_valid_proceeds(self, mock_message, mock_state):
        """Test valid name proceeds to payment link step"""
        mock_message.text = "Test Artist"

        await onboard_name(mock_message, mock_state)

        mock_state.update_data.assert_called_with(onb_name="Test Artist")
        mock_state.set_state.assert_called_with(OnboardingStates.waiting_payment_link)

    @pytest.mark.asyncio
    async def test_onboard_paylink_invalid_url_rejected(self, mock_message, mock_state):
        """Test invalid URLs are rejected"""
        mock_message.text = "not a url"

        await onboard_paylink(mock_message, mock_state)

        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        assert "http" in text.lower() or "url" in text.lower()

    @pytest.mark.asyncio
    async def test_onboard_paylink_valid_proceeds(self, mock_message, mock_state):
        """Test valid URL proceeds to genre step"""
        mock_message.text = "https://pay.me/test"

        await onboard_paylink(mock_message, mock_state)

        mock_state.update_data.assert_called_with(onb_paylink="https://pay.me/test")
        mock_state.set_state.assert_called_with(OnboardingStates.waiting_genre)


class TestSubmissionFlow:
    """Tests for track submission flow"""

    @pytest.mark.asyncio
    async def test_sub_audio_stores_file_id(self, mock_message, mock_state):
        """Test audio upload stores file ID"""
        mock_message.audio = MagicMock()
        mock_message.audio.file_id = "file_abc123"

        await sub_audio(mock_message, mock_state)

        mock_state.update_data.assert_called_with(file_id="file_abc123")
        mock_state.set_state.assert_called_with(SubmitStates.waiting_title)

    @pytest.mark.asyncio
    async def test_sub_title_short_title_rejected(self, mock_message, mock_state):
        """Test titles shorter than 2 chars are rejected"""
        mock_message.text = "A"

        await sub_title(mock_message, mock_state)

        mock_message.answer.assert_called()
        text = mock_message.answer.call_args[0][0]
        assert "short" in text.lower()

    @pytest.mark.asyncio
    async def test_sub_title_valid_proceeds(self, mock_message, mock_state):
        """Test valid title proceeds to genre step"""
        mock_message.text = "My Great Song"
        mock_state.get_data = AsyncMock(return_value={"default_genre": "Pop"})

        await sub_title(mock_message, mock_state)

        mock_state.update_data.assert_called_with(title="My Great Song")
        mock_state.set_state.assert_called_with(SubmitStates.waiting_genre)
