# tests/test_i18n.py
"""Tests for i18n (internationalization) module"""
import pytest

from sado_music_bot.i18n import (
    t, t_channel, LANGUAGES, DEFAULT_LANGUAGE, CHANNEL_LANGUAGE,
    get_language_name, get_available_languages
)


class TestTranslationFunction:
    """Tests for t() function"""

    def test_returns_uzbek_by_default(self):
        """Default language should be Uzbek"""
        result = t("welcome_back")
        assert "Xush kelibsiz" in result

    def test_returns_uzbek_when_specified(self):
        """Explicitly specifying 'uz' should return Uzbek"""
        result = t("welcome_back", "uz")
        assert "Xush kelibsiz" in result

    def test_returns_russian_when_specified(self):
        """Specifying 'ru' should return Russian"""
        result = t("welcome_back", "ru")
        assert "С возвращением" in result

    def test_unknown_language_falls_back_to_default(self):
        """Unknown language code should fall back to default (Uzbek)"""
        result = t("welcome_back", "fr")
        assert "Xush kelibsiz" in result

    def test_returns_key_if_not_found(self):
        """Missing key should return the key itself"""
        result = t("nonexistent_key", "uz")
        assert result == "nonexistent_key"

    def test_none_language_uses_default(self):
        """None language should use default"""
        result = t("welcome_back", None)
        assert "Xush kelibsiz" in result

    def test_format_arguments(self):
        """Should support format arguments"""
        result = t("uploading_as", "uz", name="TestArtist")
        assert "TestArtist" in result

    def test_format_arguments_russian(self):
        """Format arguments should work in Russian too"""
        result = t("uploading_as", "ru", name="TestArtist")
        assert "TestArtist" in result


class TestChannelTranslation:
    """Tests for t_channel() function"""

    def test_always_returns_uzbek(self):
        """Channel translations should always be Uzbek"""
        result = t_channel("welcome_back")
        assert "Xush kelibsiz" in result

    def test_channel_language_is_uzbek(self):
        """CHANNEL_LANGUAGE constant should be 'uz'"""
        assert CHANNEL_LANGUAGE == "uz"


class TestLanguageConstants:
    """Tests for language constants"""

    def test_default_language_is_uzbek(self):
        """Default language should be Uzbek"""
        assert DEFAULT_LANGUAGE == "uz"

    def test_languages_dict_has_uzbek(self):
        """LANGUAGES should contain Uzbek"""
        assert "uz" in LANGUAGES

    def test_languages_dict_has_russian(self):
        """LANGUAGES should contain Russian"""
        assert "ru" in LANGUAGES

    def test_languages_have_same_keys(self):
        """All languages should have the same keys"""
        uz_keys = set(LANGUAGES["uz"].keys())
        ru_keys = set(LANGUAGES["ru"].keys())
        assert uz_keys == ru_keys


class TestGetLanguageName:
    """Tests for get_language_name() function"""

    def test_uzbek_name(self):
        """Uzbek should return correct display name"""
        result = get_language_name("uz")
        assert "O'zbekcha" in result
        assert "🇺🇿" in result

    def test_russian_name(self):
        """Russian should return correct display name"""
        result = get_language_name("ru")
        assert "Русский" in result
        assert "🇷🇺" in result

    def test_unknown_returns_code(self):
        """Unknown language should return the code itself"""
        result = get_language_name("xyz")
        assert result == "xyz"


class TestGetAvailableLanguages:
    """Tests for get_available_languages() function"""

    def test_returns_dict(self):
        """Should return a dictionary"""
        result = get_available_languages()
        assert isinstance(result, dict)

    def test_contains_uzbek(self):
        """Should contain Uzbek"""
        result = get_available_languages()
        assert "uz" in result

    def test_contains_russian(self):
        """Should contain Russian"""
        result = get_available_languages()
        assert "ru" in result


class TestTranslationKeys:
    """Tests for specific translation keys"""

    @pytest.mark.parametrize("key", [
        "welcome_back",
        "welcome_new",
        "select_language",
        "language_saved",
        "track_not_found",
        "artist_not_found",
        "no_profile",
        "cancelled",
        "help_text",
        "onboard_start",
        "profile_created",
        "submitter_approved",
        "submitter_rejected",
    ])
    def test_key_exists_in_uzbek(self, key):
        """All essential keys should exist in Uzbek"""
        result = t(key, "uz")
        assert result != key  # Should return translation, not the key itself

    @pytest.mark.parametrize("key", [
        "welcome_back",
        "welcome_new",
        "select_language",
        "language_saved",
        "track_not_found",
        "artist_not_found",
        "no_profile",
        "cancelled",
        "help_text",
        "onboard_start",
        "profile_created",
        "submitter_approved",
        "submitter_rejected",
    ])
    def test_key_exists_in_russian(self, key):
        """All essential keys should exist in Russian"""
        result = t(key, "ru")
        assert result != key  # Should return translation, not the key itself


class TestHTMLFormatting:
    """Tests to ensure translations use HTML formatting"""

    def test_uzbek_texts_use_html(self):
        """Uzbek texts should use HTML tags, not MarkdownV2"""
        result = t("help_text", "uz")
        assert "<b>" in result or "<i>" in result

    def test_russian_texts_use_html(self):
        """Russian texts should use HTML tags, not MarkdownV2"""
        result = t("help_text", "ru")
        assert "<b>" in result or "<i>" in result

    def test_no_markdownv2_escaping(self):
        """Texts should not have MarkdownV2 escape characters"""
        for lang in ["uz", "ru"]:
            for key in LANGUAGES[lang]:
                text = LANGUAGES[lang][key]
                # Check no excessive backslash escaping
                assert "\\." not in text, f"Key '{key}' in '{lang}' has MarkdownV2 escaping"
                assert "\\!" not in text, f"Key '{key}' in '{lang}' has MarkdownV2 escaping"
                assert "\\-" not in text, f"Key '{key}' in '{lang}' has MarkdownV2 escaping"

