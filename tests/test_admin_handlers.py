"""
Tests for admin handlers - comprehensive unit tests
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from sado_music_bot.admin.handlers import on_admin_approve, on_admin_reject, router
from sado_music_bot.config import Config


@pytest.fixture
def mock_config():
    """Mock configuration"""
    return Config(
        bot_token="test_token",
        admin_id=12345,
        bot_username="test_bot",
        channel_pop="@test_pop",
        channel_rock="@test_rock",
        channel_hiphop="@test_hiphop",
        channel_discovery="@test_discovery",
        discussion_pop="@test_pop_disc",
        discussion_rock="@test_rock_disc",
        discussion_hiphop="@test_hiphop_disc",
        discussion_discovery="@test_discovery_disc",
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
def sample_submission():
    """Sample submission tuple"""
    return (
        "sub_test123",      # submission_id
        "art_abc123",       # artist_id
        99999,              # submitter_user_id
        "Test Track",       # title
        "Pop",              # genre
        "Test caption",     # caption
        "file_id_123",      # telegram_file_id
        "PENDING",          # status
        None                # admin_message_id
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
def admin_callback(mock_config):
    """Mock callback from admin"""
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = mock_config.admin_id
    cb.data = "admin_approve:sub_test123"
    cb.message = MagicMock()
    cb.message.caption = "Test submission caption"
    cb.message.edit_caption = AsyncMock()
    cb.answer = AsyncMock()
    return cb


@pytest.fixture
def non_admin_callback():
    """Mock callback from non-admin"""
    cb = MagicMock()
    cb.from_user = MagicMock()
    cb.from_user.id = 99999  # Not admin
    cb.data = "admin_approve:sub_test123"
    cb.answer = AsyncMock()
    return cb


class TestAdminHandlerRouterSetup:
    """Tests for admin router configuration"""

    def test_router_exists(self):
        """Test router is defined"""
        assert router is not None

    def test_router_has_callback_handlers(self):
        """Test router has callback handlers registered"""
        assert len(router.callback_query.handlers) > 0


class TestAdminHandlerFunctions:
    """Tests for admin handler functions exist"""

    def test_approve_handler_exists(self):
        """Test on_admin_approve function exists"""
        assert callable(on_admin_approve)

    def test_reject_handler_exists(self):
        """Test on_admin_reject function exists"""
        assert callable(on_admin_reject)


class TestOnAdminApprove:
    """Tests for admin approval handler"""

    @pytest.mark.asyncio
    async def test_unauthorized_user_rejected(self, non_admin_callback, mock_bot, mock_config, mock_db):
        """Test non-admin user is rejected"""
        await on_admin_approve(non_admin_callback, mock_bot, mock_config, mock_db)

        non_admin_callback.answer.assert_called_with("You're not authorized.", show_alert=True)
        mock_db.get_submission.assert_not_called()

    @pytest.mark.asyncio
    async def test_submission_not_found(self, admin_callback, mock_bot, mock_config, mock_db):
        """Test missing submission shows error"""
        mock_db.get_submission = AsyncMock(return_value=None)

        await on_admin_approve(admin_callback, mock_bot, mock_config, mock_db)

        admin_callback.answer.assert_called_with("Submission not found.", show_alert=True)

    @pytest.mark.asyncio
    async def test_already_approved_submission(self, admin_callback, mock_bot, mock_config, mock_db, sample_submission):
        """Test already processed submission shows error"""
        # Modify to APPROVED status
        approved = list(sample_submission)
        approved[7] = "APPROVED"
        mock_db.get_submission = AsyncMock(return_value=tuple(approved))

        await on_admin_approve(admin_callback, mock_bot, mock_config, mock_db)

        admin_callback.answer.assert_called()
        call_args = admin_callback.answer.call_args[0][0]
        assert "APPROVED" in call_args

    @pytest.mark.asyncio
    async def test_channel_not_configured(self, admin_callback, mock_bot, mock_db, sample_submission, sample_artist):
        """Test approval fails when channel not configured for genre"""
        # Config with empty channel for Pop
        cfg = Config(
            bot_token="test",
            admin_id=12345,
            bot_username="test_bot",
            channel_pop="",  # Not configured
        )

        mock_db.get_submission = AsyncMock(return_value=sample_submission)
        mock_db.get_artist = AsyncMock(return_value=sample_artist)

        await on_admin_approve(admin_callback, mock_bot, cfg, mock_db)

        admin_callback.answer.assert_called()
        call_args = admin_callback.answer.call_args
        assert "Channel not configured" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_successful_approval_flow(self, admin_callback, mock_bot, mock_config, mock_db, sample_submission, sample_artist):
        """Test successful approval posts track and updates status"""
        mock_db.get_submission = AsyncMock(return_value=sample_submission)
        mock_db.get_artist = AsyncMock(return_value=sample_artist)
        mock_db.insert_track = AsyncMock()
        mock_db.set_submission_status = AsyncMock()

        await on_admin_approve(admin_callback, mock_bot, mock_config, mock_db)

        # Verify track was posted to channel
        mock_bot.send_audio.assert_called_once()
        call_kwargs = mock_bot.send_audio.call_args[1]
        assert call_kwargs['chat_id'] == "@test_pop"  # Pop channel
        assert call_kwargs['audio'] == "file_id_123"

        # Verify track was inserted in DB
        mock_db.insert_track.assert_called_once()

        # Verify submission status updated
        mock_db.set_submission_status.assert_called_with("sub_test123", "APPROVED")

        # Verify submitter was notified
        assert mock_bot.send_message.call_count >= 1

        # Verify success answer
        admin_callback.answer.assert_called_with("✅ Approved and posted!")

    @pytest.mark.asyncio
    async def test_discussion_anchor_created(self, admin_callback, mock_bot, mock_config, mock_db, sample_submission, sample_artist):
        """Test discussion anchor message is created"""
        mock_db.get_submission = AsyncMock(return_value=sample_submission)
        mock_db.get_artist = AsyncMock(return_value=sample_artist)
        mock_db.insert_track = AsyncMock()
        mock_db.set_submission_status = AsyncMock()

        await on_admin_approve(admin_callback, mock_bot, mock_config, mock_db)

        # Verify discussion message was sent
        send_message_calls = mock_bot.send_message.call_args_list
        discussion_call = [c for c in send_message_calls if c[1].get('chat_id') == "@test_pop_disc"]
        assert len(discussion_call) >= 1

    @pytest.mark.asyncio
    async def test_missing_callback_data(self, mock_bot, mock_config, mock_db):
        """Test handler handles missing callback data"""
        cb = MagicMock()
        cb.from_user = MagicMock(id=12345)
        cb.data = None

        # Should return early without error
        await on_admin_approve(cb, mock_bot, mock_config, mock_db)


class TestOnAdminReject:
    """Tests for admin rejection handler"""

    @pytest.mark.asyncio
    async def test_unauthorized_user_rejected(self, non_admin_callback, mock_bot, mock_config, mock_db):
        """Test non-admin user is rejected"""
        non_admin_callback.data = "admin_reject:sub_test123"

        await on_admin_reject(non_admin_callback, mock_bot, mock_config, mock_db)

        non_admin_callback.answer.assert_called_with("You're not authorized.", show_alert=True)

    @pytest.mark.asyncio
    async def test_submission_not_found(self, admin_callback, mock_bot, mock_config, mock_db):
        """Test missing submission shows error"""
        admin_callback.data = "admin_reject:sub_unknown"
        mock_db.get_submission = AsyncMock(return_value=None)

        await on_admin_reject(admin_callback, mock_bot, mock_config, mock_db)

        admin_callback.answer.assert_called_with("Submission not found.", show_alert=True)

    @pytest.mark.asyncio
    async def test_already_rejected_submission(self, admin_callback, mock_bot, mock_config, mock_db, sample_submission):
        """Test already processed submission shows error"""
        admin_callback.data = "admin_reject:sub_test123"
        rejected = list(sample_submission)
        rejected[7] = "REJECTED"
        mock_db.get_submission = AsyncMock(return_value=tuple(rejected))

        await on_admin_reject(admin_callback, mock_bot, mock_config, mock_db)

        admin_callback.answer.assert_called()
        call_args = admin_callback.answer.call_args[0][0]
        assert "REJECTED" in call_args

    @pytest.mark.asyncio
    async def test_successful_rejection_flow(self, admin_callback, mock_bot, mock_config, mock_db, sample_submission):
        """Test successful rejection updates status and notifies submitter"""
        admin_callback.data = "admin_reject:sub_test123"
        mock_db.get_submission = AsyncMock(return_value=sample_submission)
        mock_db.set_submission_status = AsyncMock()

        await on_admin_reject(admin_callback, mock_bot, mock_config, mock_db)

        # Verify submission status updated
        mock_db.set_submission_status.assert_called_with("sub_test123", "REJECTED")

        # Verify submitter was notified
        mock_bot.send_message.assert_called()
        notify_call = mock_bot.send_message.call_args
        assert notify_call[1]['chat_id'] == 99999  # submitter_user_id
        assert "not approved" in notify_call[1]['text'].lower() or "rejected" in notify_call[1]['text'].lower()

        # Verify answer
        admin_callback.answer.assert_called_with("❌ Rejected")

    @pytest.mark.asyncio
    async def test_admin_message_updated(self, admin_callback, mock_bot, mock_config, mock_db, sample_submission):
        """Test admin message caption is updated with REJECTED"""
        admin_callback.data = "admin_reject:sub_test123"
        mock_db.get_submission = AsyncMock(return_value=sample_submission)
        mock_db.set_submission_status = AsyncMock()

        await on_admin_reject(admin_callback, mock_bot, mock_config, mock_db)

        # Verify caption was updated
        admin_callback.message.edit_caption.assert_called()
        call_args = admin_callback.message.edit_caption.call_args[1]
        assert "REJECTED" in call_args['caption']
