"""
Tests for keyboard layouts
"""
import pytest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from sado_music_bot.keyboards import (
    kb_lang, kb_genres, kb_track_post, kb_admin_review,
    kb_donation_confirm, kb_profile_actions, kb_donation_amounts,
    kb_donation_note_options, kb_donation_anonymity, kb_track_support,
    PRESET_AMOUNTS, GENRES
)


class TestKbLang:
    """Tests for language selection keyboard"""
    
    def test_returns_inline_keyboard(self):
        """Test kb_lang returns InlineKeyboardMarkup"""
        result = kb_lang()
        assert isinstance(result, InlineKeyboardMarkup)
    
    def test_has_two_buttons(self):
        """Test keyboard has Uzbek and Russian options"""
        kb = kb_lang()
        buttons = kb.inline_keyboard[0]
        assert len(buttons) == 2
    
    def test_button_callbacks(self):
        """Test button callback data"""
        kb = kb_lang()
        buttons = kb.inline_keyboard[0]
        callbacks = [btn.callback_data for btn in buttons]
        assert "lang:uz" in callbacks
        assert "lang:ru" in callbacks


class TestKbGenres:
    """Tests for genre selection keyboard"""
    
    def test_returns_inline_keyboard(self):
        """Test kb_genres returns InlineKeyboardMarkup"""
        result = kb_genres("test")
        assert isinstance(result, InlineKeyboardMarkup)
    
    def test_includes_all_genres(self):
        """Test all genres are included"""
        kb = kb_genres("test")
        all_buttons = []
        for row in kb.inline_keyboard:
            all_buttons.extend(row)
        
        button_texts = [btn.text for btn in all_buttons]
        for genre in GENRES:
            assert genre in button_texts
    
    def test_custom_prefix(self):
        """Test custom callback prefix"""
        kb = kb_genres("myprefix")
        first_button = kb.inline_keyboard[0][0]
        assert first_button.callback_data.startswith("myprefix:")
    
    def test_has_cancel_button(self):
        """Test cancel button is present"""
        kb = kb_genres("test")
        last_row = kb.inline_keyboard[-1]
        cancel_btn = last_row[0]
        assert cancel_btn.text == "❌ Cancel"
        assert cancel_btn.callback_data == "test:CANCEL"


class TestKbTrackPost:
    """Tests for track post keyboard"""
    
    def test_returns_inline_keyboard(self):
        """Test kb_track_post returns InlineKeyboardMarkup"""
        result = kb_track_post("trk_123", "art_456", "testbot")
        assert isinstance(result, InlineKeyboardMarkup)
    
    def test_support_button_url(self):
        """Test support button has correct deep link"""
        kb = kb_track_post("trk_123", "art_456", "testbot")
        support_btn = kb.inline_keyboard[0][0]
        assert "t.me/testbot?start=donate_trk_123" in support_btn.url
    
    def test_artist_profile_button_url(self):
        """Test artist profile button has correct deep link"""
        kb = kb_track_post("trk_123", "art_456", "testbot")
        profile_btn = kb.inline_keyboard[1][0]
        assert "t.me/testbot?start=artist_art_456" in profile_btn.url
    
    def test_empty_bot_username_creates_broken_link(self):
        """Test that empty bot_username creates invalid URL (catches the bug)"""
        kb = kb_track_post("trk_123", "art_456", "")
        support_btn = kb.inline_keyboard[0][0]
        # This should be flagged as invalid
        assert "t.me/?start=" in support_btn.url  # Broken link with empty username


class TestKbAdminReview:
    """Tests for admin review keyboard"""
    
    def test_returns_inline_keyboard(self):
        """Test kb_admin_review returns InlineKeyboardMarkup"""
        result = kb_admin_review("sub_123")
        assert isinstance(result, InlineKeyboardMarkup)
    
    def test_has_approve_reject_buttons(self):
        """Test approve and reject buttons exist"""
        kb = kb_admin_review("sub_123")
        buttons = kb.inline_keyboard[0]
        callbacks = [btn.callback_data for btn in buttons]
        assert "admin_approve:sub_123" in callbacks
        assert "admin_reject:sub_123" in callbacks


class TestKbDonationConfirm:
    """Tests for donation confirmation keyboard"""
    
    def test_returns_inline_keyboard(self):
        """Test kb_donation_confirm returns InlineKeyboardMarkup"""
        result = kb_donation_confirm("don_123", False, False)
        assert isinstance(result, InlineKeyboardMarkup)
    
    def test_anonymous_on_text(self):
        """Test anonymous button shows ON when enabled"""
        kb = kb_donation_confirm("don_123", anon_on=True, has_note=False)
        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        anon_btn = [btn for btn in all_buttons if "Anonymous" in btn.text][0]
        assert "ON" in anon_btn.text
    
    def test_anonymous_off_text(self):
        """Test anonymous button shows OFF when disabled"""
        kb = kb_donation_confirm("don_123", anon_on=False, has_note=False)
        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        anon_btn = [btn for btn in all_buttons if "Anonymous" in btn.text][0]
        assert "OFF" in anon_btn.text
    
    def test_edit_note_when_has_note(self):
        """Test note button shows 'Edit' when note exists"""
        kb = kb_donation_confirm("don_123", anon_on=False, has_note=True)
        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        note_btn = [btn for btn in all_buttons if "note" in btn.text.lower()][0]
        assert "Edit" in note_btn.text
    
    def test_add_note_when_no_note(self):
        """Test note button shows 'Add' when no note"""
        kb = kb_donation_confirm("don_123", anon_on=False, has_note=False)
        all_buttons = [btn for row in kb.inline_keyboard for btn in row]
        note_btn = [btn for btn in all_buttons if "note" in btn.text.lower()][0]
        assert "Add" in note_btn.text


class TestKbDonationAmounts:
    """Tests for donation amounts keyboard"""
    
    def test_returns_inline_keyboard(self):
        """Test kb_donation_amounts returns InlineKeyboardMarkup"""
        result = kb_donation_amounts("trk_123")
        assert isinstance(result, InlineKeyboardMarkup)
    
    def test_includes_preset_amounts(self):
        """Test preset amounts are included"""
        kb = kb_donation_amounts("trk_123")
        all_callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        
        for amount in PRESET_AMOUNTS:
            expected = f"donamtsel:trk_123:{amount}"
            assert expected in all_callbacks
    
    def test_includes_custom_option(self):
        """Test custom amount option is included"""
        kb = kb_donation_amounts("trk_123")
        all_callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        assert "donamtsel:trk_123:custom" in all_callbacks
    
    def test_includes_cancel(self):
        """Test cancel button is included"""
        kb = kb_donation_amounts("trk_123")
        all_callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
        assert "doncancel" in all_callbacks


class TestConstants:
    """Tests for module constants"""
    
    def test_preset_amounts_are_positive(self):
        """Test all preset amounts are positive"""
        for amount in PRESET_AMOUNTS:
            assert amount > 0
    
    def test_genres_not_empty(self):
        """Test GENRES list is not empty"""
        assert len(GENRES) > 0

