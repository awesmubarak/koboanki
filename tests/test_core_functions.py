"""Tests for core functions in koboanki.core module."""

from __future__ import annotations

import os
import sqlite3
import tempfile
import unicodedata
from unittest.mock import patch
import pytest

from koboanki.core import find_kobo_db, get_kobo_wordlist, normalise_word


class TestNormaliseWord:
    """Test the normalise_word function."""

    def test_basic_lowercasing(self):
        """Test that words are converted to lowercase."""
        assert normalise_word("HELLO") == "hello"
        assert normalise_word("Hello") == "hello"
        assert normalise_word("hELLo") == "hello"

    def test_unicode_normalization(self):
        """Test that unicode characters are normalized to NFC form."""
        # Test combining characters (é can be é or e + ́)
        composed = "café"  # é as single character (NFC)
        decomposed = "cafe" + "\u0301"  # e + combining acute accent (NFD)
        
        assert normalise_word(composed) == "café"
        assert normalise_word(decomposed) == "café"
        
        # Both should normalize to the same result
        assert normalise_word(composed) == normalise_word(decomposed)

    def test_mixed_case_and_unicode(self):
        """Test combination of case conversion and unicode normalization."""
        word = "NAÏVE"  # Uppercase with unicode
        result = normalise_word(word)
        assert result == "naïve"
        
        # Verify it's properly normalized
        assert unicodedata.normalize("NFC", result) == result

    def test_empty_string(self):
        """Test that empty string is handled correctly."""
        assert normalise_word("") == ""

    def test_whitespace_preserved(self):
        """Test that whitespace is preserved but lowercased."""
        assert normalise_word("Hello World") == "hello world"
        assert normalise_word("  Test  ") == "  test  "

    def test_numbers_and_symbols(self):
        """Test that numbers and symbols are preserved."""
        assert normalise_word("Test123") == "test123"
        assert normalise_word("Hello-World!") == "hello-world!"


class TestFindKoboDb:
    """Test the find_kobo_db function."""

    @patch('os.path.isdir')
    @patch('os.listdir')
    @patch('os.path.isfile')
    def test_kobo_db_found(self, mock_isfile, mock_listdir, mock_isdir):
        """Test successful location of Kobo database."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ['KoboReader', 'OtherDevice']
        
        # Only the KoboReader volume has the database
        def mock_isfile_func(path):
            return 'KoboReader' in path and 'KoboReader.sqlite' in path
        
        mock_isfile.side_effect = mock_isfile_func
        
        result = find_kobo_db()
        assert result == "/Volumes/KoboReader/.kobo/KoboReader.sqlite"

    @patch('os.path.isdir')
    def test_volumes_directory_not_found(self, mock_isdir):
        """Test when /Volumes directory doesn't exist."""
        mock_isdir.return_value = False
        
        result = find_kobo_db()
        assert result is None

    @patch('os.path.isdir')
    @patch('os.listdir')
    @patch('os.path.isfile')
    def test_no_kobo_volumes_found(self, mock_isfile, mock_listdir, mock_isdir):
        """Test when no Kobo volumes are found."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ['SomeUSB', 'AnotherDevice']
        mock_isfile.return_value = False
        
        result = find_kobo_db()
        assert result is None

    @patch('os.path.isdir')
    @patch('os.listdir')
    def test_empty_volumes_directory(self, mock_listdir, mock_isdir):
        """Test when /Volumes directory is empty."""
        mock_isdir.return_value = True
        mock_listdir.return_value = []
        
        result = find_kobo_db()
        assert result is None

    @patch('os.path.isdir')
    @patch('os.listdir')
    @patch('os.path.isfile')
    def test_multiple_kobo_devices_returns_first(self, mock_isfile, mock_listdir, mock_isdir):
        """Test that first found Kobo database is returned."""
        mock_isdir.return_value = True
        mock_listdir.return_value = ['Kobo1', 'Kobo2', 'OtherDevice']
        
        # Both Kobo devices have databases
        def mock_isfile_func(path):
            return ('Kobo1' in path or 'Kobo2' in path) and 'KoboReader.sqlite' in path
        
        mock_isfile.side_effect = mock_isfile_func
        
        result = find_kobo_db()
        assert result == "/Volumes/Kobo1/.kobo/KoboReader.sqlite"


class TestGetKoboWordlist:
    """Test the get_kobo_wordlist function."""

    def create_test_db(self, temp_dir: str) -> str:
        """Create a temporary test database with sample data."""
        db_path = os.path.join(temp_dir, "test.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create WordList table
        cursor.execute("""
            CREATE TABLE WordList (
                Text TEXT PRIMARY KEY,
                VolumeId TEXT,
                DictSuffix TEXT,
                DateCreated TEXT
            )
        """)
        
        # Insert test data
        test_data = [
            ("Apple", "book1.epub", "-en", "2023-01-01"),
            ("BANANA", "book2.epub", "-en", "2023-01-02"),
            ("Café", "book3.epub", "-fr", "2023-01-03"),
            ("Straße", "book4.epub", "-de", "2023-01-04"),
            ("test", "book5.epub", None, "2023-01-05"),  # No DictSuffix
            ("héllo", "book6.epub", "", "2023-01-06"),   # Empty DictSuffix
        ]
        
        cursor.executemany(
            "INSERT INTO WordList (Text, VolumeId, DictSuffix, DateCreated) VALUES (?, ?, ?, ?)",
            test_data
        )
        
        conn.commit()
        conn.close()
        return db_path

    def test_successful_wordlist_extraction(self):
        """Test successful extraction of word list with normalization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = self.create_test_db(temp_dir)
            
            result = get_kobo_wordlist(db_path)
            
            # Check that we get the expected words with proper normalization
            expected = [
                ("apple", "en"),
                ("banana", "en"),
                ("café", "fr"),
                ("straße", "de"),
                ("test", "en"),    # Default to 'en' when DictSuffix is None
                ("héllo", "en"),   # Default to 'en' when DictSuffix is empty
            ]
            
            assert result == expected

    def test_empty_database(self):
        """Test behavior with empty WordList table."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "empty.sqlite")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE WordList (
                    Text TEXT PRIMARY KEY,
                    VolumeId TEXT,
                    DictSuffix TEXT,
                    DateCreated TEXT
                )
            """)
            
            conn.commit()
            conn.close()
            
            result = get_kobo_wordlist(db_path)
            assert result == []

    def test_database_file_not_found(self):
        """Test error handling when database file doesn't exist."""
        with pytest.raises(sqlite3.OperationalError):
            get_kobo_wordlist("/nonexistent/path/database.sqlite")

    def test_missing_wordlist_table(self):
        """Test error handling when WordList table doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "notable.sqlite")
            conn = sqlite3.connect(db_path)
            # Create database but don't create WordList table
            conn.close()
            
            with pytest.raises(sqlite3.OperationalError):
                get_kobo_wordlist(db_path)

    def test_language_code_processing(self):
        """Test various language code processing edge cases."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = os.path.join(temp_dir, "langtest.sqlite")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE WordList (
                    Text TEXT PRIMARY KEY,
                    VolumeId TEXT,
                    DictSuffix TEXT,
                    DateCreated TEXT
                )
            """)
            
            # Test various language code formats
            test_data = [
                ("word1", "book.epub", "-en", "2023-01-01"),    # Normal case
                ("word2", "book.epub", "en", "2023-01-02"),     # No leading dash
                ("word3", "book.epub", "-en-US", "2023-01-03"), # Regional variant
                ("word4", "book.epub", "de-DE", "2023-01-04"),  # Regional without dash
                ("word5", "book.epub", None, "2023-01-05"),     # None/null
                ("word6", "book.epub", "", "2023-01-06"),       # Empty string
                ("word7", "book.epub", "-", "2023-01-07"),      # Just dash
            ]
            
            cursor.executemany(
                "INSERT INTO WordList (Text, VolumeId, DictSuffix, DateCreated) VALUES (?, ?, ?, ?)",
                test_data
            )
            
            conn.commit()
            conn.close()
            
            result = get_kobo_wordlist(db_path)
            
            # Check language code processing
            expected = [
                ("word1", "en"),     # -en -> en
                ("word2", "en"),     # en -> en  
                ("word3", "en-US"),  # -en-US -> en-US (regional preserved)
                ("word4", "de-DE"),  # de-DE -> de-DE (regional preserved)
                ("word5", "en"),     # None -> en (default)
                ("word6", "en"),     # "" -> en (default)
                ("word7", ""),       # "-" -> "" (just dash stripped)
            ]
            
            assert result == expected 