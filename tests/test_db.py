"""
Tests for database module
"""
import pytest
import time
from unittest.mock import MagicMock, patch, call
import psycopg2

from sado_music_bot.db import DB


class TestDBInit:
    """Tests for DB initialization"""

    @pytest.mark.asyncio
    async def test_init_creates_tables(self):
        """Test that init creates all required tables"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        with patch('psycopg2.connect', return_value=mock_conn):
            db = DB("postgresql://test")
            await db.init()

            # Verify tables were created
            execute_calls = mock_cursor.execute.call_args_list
            sql_statements = [str(call[0][0]) for call in execute_calls]

            assert any("user_settings" in sql for sql in sql_statements)
            assert any("artists" in sql for sql in sql_statements)
            assert any("submissions" in sql for sql in sql_statements)
            assert any("tracks" in sql for sql in sql_statements)
            assert any("donation_events" in sql for sql in sql_statements)

            # Verify commit was called
            mock_conn.commit.assert_called()


class TestUserSettings:
    """Tests for user settings methods"""

    @pytest.mark.asyncio
    async def test_get_lang_returns_default(self):
        """Test get_lang returns 'uz' for new user"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        db = DB("postgresql://test")
        db.conn = mock_conn

        result = await db.get_lang(12345)
        assert result == "uz"

    @pytest.mark.asyncio
    async def test_get_lang_returns_saved(self):
        """Test get_lang returns saved language"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("ru",)
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        db = DB("postgresql://test")
        db.conn = mock_conn

        result = await db.get_lang(12345)
        assert result == "ru"

    @pytest.mark.asyncio
    async def test_set_lang(self):
        """Test set_lang updates database"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        db = DB("postgresql://test")
        db.conn = mock_conn

        await db.set_lang(12345, "ru")

        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()


class TestArtists:
    """Tests for artist methods"""

    @pytest.mark.asyncio
    async def test_upsert_artist(self):
        """Test upserting an artist"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        db = DB("postgresql://test")
        db.conn = mock_conn

        await db.upsert_artist(
            artist_id="art_test123",
            tg_user_id=99999,
            display_name="Test Artist",
            payment_link="https://pay.me/test",
            profile_url=None,
            default_genre="Pop",
            bio="Test bio"
        )

        mock_cursor.execute.assert_called_once()
        call_args = mock_cursor.execute.call_args[0]
        assert "INSERT INTO artists" in call_args[0]
        assert "ON CONFLICT" in call_args[0]
        mock_conn.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_artist_not_found(self):
        """Test get_artist returns None for unknown artist"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        db = DB("postgresql://test")
        db.conn = mock_conn

        result = await db.get_artist("unknown_id")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_artist_field_valid(self):
        """Test updating valid artist field"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        db = DB("postgresql://test")
        db.conn = mock_conn

        await db.update_artist_field("art_test", "display_name", "New Name")
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_artist_field_invalid(self):
        """Test updating invalid field raises error"""
        db = DB("postgresql://test")
        db.conn = MagicMock()

        with pytest.raises(ValueError, match="Invalid field"):
            await db.update_artist_field("art_test", "invalid_field", "value")


class TestDonations:
    """Tests for donation methods"""

    @pytest.mark.asyncio
    async def test_create_donation_returns_id(self):
        """Test create_donation returns donation ID"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        db = DB("postgresql://test")
        db.conn = mock_conn

        donation_id = await db.create_donation(
            track_id="trk_test",
            artist_id="art_test",
            donor_user_id=99999,
            donor_name="Test User",
            donor_username="testuser",
            amount=10000,
            is_anonymous=0
        )

        assert donation_id.startswith("don_")
        assert len(donation_id) == 16  # "don_" + 12 hex chars
        mock_conn.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_toggle_donation_anon_atomic(self):
        """Test toggle_donation_anon uses atomic update"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)  # New value after toggle
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        db = DB("postgresql://test")
        db.conn = mock_conn

        result = await db.toggle_donation_anon("don_test123")

        # Verify atomic update was used
        call_args = mock_cursor.execute.call_args[0]
        sql = call_args[0]
        assert "CASE WHEN is_anonymous = 1 THEN 0 ELSE 1 END" in sql
        assert "RETURNING is_anonymous" in sql
        assert result == 1

    @pytest.mark.asyncio
    async def test_toggle_donation_anon_not_found(self):
        """Test toggle_donation_anon raises for unknown donation"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        db = DB("postgresql://test")
        db.conn = mock_conn

        with pytest.raises(ValueError, match="Donation not found"):
            await db.toggle_donation_anon("unknown_donation")

    @pytest.mark.asyncio
    async def test_set_donation_status_confirmed(self):
        """Test setting donation status to CONFIRMED sets timestamp"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        db = DB("postgresql://test")
        db.conn = mock_conn

        await db.set_donation_status("don_test", "CONFIRMED")

        call_args = mock_cursor.execute.call_args[0]
        assert "confirmed_at" in call_args[0]
        mock_conn.commit.assert_called_once()


class TestTracks:
    """Tests for track methods"""

    @pytest.mark.asyncio
    async def test_insert_track(self):
        """Test inserting a track"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        db = DB("postgresql://test")
        db.conn = mock_conn

        await db.insert_track(
            track_id="trk_test",
            artist_id="art_test",
            title="Test Track",
            genre="Pop",
            caption="Test caption",
            telegram_file_id="file_123",
            channel_msg_id=12345,
            discussion_anchor_id=67890
        )

        call_args = mock_cursor.execute.call_args[0]
        assert "INSERT INTO tracks" in call_args[0]
        mock_conn.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_artist_tracks(self):
        """Test counting artist tracks"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (5,)
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        db = DB("postgresql://test")
        db.conn = mock_conn

        count = await db.count_artist_tracks("art_test")
        assert count == 5


class TestSubmissions:
    """Tests for submission methods"""

    @pytest.mark.asyncio
    async def test_create_submission(self):
        """Test creating a submission"""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__ = MagicMock(return_value=mock_cursor)
        mock_conn.cursor.return_value.__exit__ = MagicMock(return_value=False)

        db = DB("postgresql://test")
        db.conn = mock_conn

        await db.create_submission(
            submission_id="sub_test",
            artist_id="art_test",
            submitter_user_id=99999,
            title="Test Track",
            genre="Rock",
            caption="Test caption",
            telegram_file_id="file_123"
        )

        call_args = mock_cursor.execute.call_args[0]
        assert "INSERT INTO submissions" in call_args[0]
        assert "PENDING" in str(call_args[1])  # Default status
        mock_conn.commit.assert_called_once()

