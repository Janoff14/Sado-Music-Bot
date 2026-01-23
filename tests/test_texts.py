"""
Tests for text templates
"""
import pytest

from sado_music_bot.texts import (
    track_caption, track_caption_with_payment,
    donation_dm_card, appreciation_public, creator_dm,
    artist_profile_text, donation_start_text
)


class TestTrackCaption:
    """Tests for track_caption function"""

    def test_includes_title(self):
        """Test caption includes track title"""
        result = track_caption("My Song", "Artist Name")
        assert "My Song" in result

    def test_includes_artist(self):
        """Test caption includes artist name"""
        result = track_caption("My Song", "Artist Name")
        assert "Artist Name" in result


class TestTrackCaptionWithPayment:
    """Tests for track_caption_with_payment function"""

    def test_includes_title_and_artist(self):
        """Test caption includes title and artist"""
        result = track_caption_with_payment("My Song", "Artist", None, None)
        assert "My Song" in result
        assert "Artist" in result

    def test_includes_payment_link_when_provided(self):
        """Test caption includes payment link"""
        result = track_caption_with_payment("Song", "Artist", "https://pay.me/test", None)
        assert "https://pay.me/test" in result

    def test_includes_caption_when_provided(self):
        """Test caption includes description"""
        result = track_caption_with_payment("Song", "Artist", None, "Great track!")
        assert "Great track!" in result


class TestDonationDmCard:
    """Tests for donation_dm_card function"""

    def test_includes_amount_formatted(self):
        """Test amount is formatted with spaces"""
        result = donation_dm_card("Song", "Artist", 10000, False, None)
        assert "10 000" in result or "10,000" in result

    def test_includes_track_and_artist(self):
        """Test card includes track and artist"""
        result = donation_dm_card("My Song", "Test Artist", 5000, False, None)
        assert "My Song" in result
        assert "Test Artist" in result

    def test_anonymous_on(self):
        """Test anonymous flag shows ON"""
        result = donation_dm_card("Song", "Artist", 5000, True, None)
        assert "ON" in result

    def test_anonymous_off(self):
        """Test anonymous flag shows OFF"""
        result = donation_dm_card("Song", "Artist", 5000, False, None)
        assert "OFF" in result

    def test_includes_note_when_provided(self):
        """Test note is included"""
        result = donation_dm_card("Song", "Artist", 5000, False, "Great song!")
        assert "Great song!" in result

    def test_shows_none_when_no_note(self):
        """Test shows (none) when no note"""
        result = donation_dm_card("Song", "Artist", 5000, False, None)
        assert "(none)" in result


class TestAppreciationPublic:
    """Tests for appreciation_public function"""

    def test_includes_donor_name(self):
        """Test includes donor name"""
        result = appreciation_public("John", 10000, "Artist", "Song", None)
        assert "John" in result

    def test_includes_amount(self):
        """Test includes formatted amount"""
        result = appreciation_public("John", 10000, "Artist", "Song", None)
        assert "10 000" in result or "10,000" in result

    def test_includes_artist_and_track(self):
        """Test includes artist and track"""
        result = appreciation_public("John", 5000, "Test Artist", "Test Song", None)
        assert "Test Artist" in result
        assert "Test Song" in result

    def test_includes_note_when_provided(self):
        """Test note is included"""
        result = appreciation_public("John", 5000, "Artist", "Song", "Love this!")
        assert "Love this!" in result


class TestCreatorDm:
    """Tests for creator_dm function"""

    def test_anonymous_donation(self):
        """Test anonymous donation message"""
        result = creator_dm(True, "John", "john123", 10000, "Song", None)
        assert "anonymous" in result.lower()

    def test_public_donation_includes_name(self):
        """Test public donation includes donor name"""
        result = creator_dm(False, "John", "john123", 10000, "Song", None)
        assert "John" in result

    def test_public_donation_includes_username(self):
        """Test public donation includes username"""
        result = creator_dm(False, "John", "john123", 10000, "Song", None)
        assert "@john123" in result

    def test_includes_amount(self):
        """Test includes formatted amount"""
        result = creator_dm(False, "John", None, 10000, "Song", None)
        assert "10 000" in result or "10,000" in result

    def test_includes_track(self):
        """Test includes track title"""
        result = creator_dm(False, "John", None, 5000, "My Song", None)
        assert "My Song" in result

    def test_includes_note(self):
        """Test includes note when provided"""
        result = creator_dm(False, "John", None, 5000, "Song", "Great work!")
        assert "Great work!" in result


class TestArtistProfileText:
    """Tests for artist_profile_text function"""

    def test_includes_artist_name(self):
        """Test includes artist name"""
        result = artist_profile_text("Test Artist", None, 0, [])
        assert "Test Artist" in result

    def test_includes_bio_when_provided(self):
        """Test includes bio"""
        result = artist_profile_text("Artist", "My awesome bio", 0, [])
        assert "My awesome bio" in result

    def test_includes_track_count(self):
        """Test includes total track count"""
        result = artist_profile_text("Artist", None, 5, [])
        assert "5" in result

    def test_includes_tracks_list(self):
        """Test includes track list"""
        tracks = [
            ("Song 1", "Pop", "trk_1"),
            ("Song 2", "Rock", "trk_2"),
        ]
        result = artist_profile_text("Artist", None, 2, tracks)
        assert "Song 1" in result
        assert "Song 2" in result


class TestDonationStartText:
    """Tests for donation_start_text function"""

    def test_includes_track_title(self):
        """Test includes track title"""
        result = donation_start_text("My Song", "Artist")
        assert "My Song" in result

    def test_includes_artist_name(self):
        """Test includes artist name"""
        result = donation_start_text("Song", "Test Artist")
        assert "Test Artist" in result

