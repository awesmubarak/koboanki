"""Tests for the card builder system."""

from koboanki.card_builder import (
    CardBuilder,
    CardLevel,
    build_card_fields,
    get_card_template,
)
from koboanki.core import WordData, WordExample, WordSense


def test_card_levels() -> None:
    """Test that all card levels are properly defined."""
    assert CardLevel.BASIC.value == "basic"
    assert CardLevel.INTERMEDIATE.value == "intermediate"
    assert CardLevel.FULL.value == "full"


def test_basic_level_fields() -> None:
    """Test basic level field generation."""
    # Create minimal test data
    word_data = WordData(
        word="test",
        language="en",
        senses=[
            WordSense(glosses=["a trial or examination"])
        ]
    )
    
    builder = CardBuilder(CardLevel.BASIC)
    fields = builder.build_fields(word_data)
    
    # Check basic fields are present
    assert fields["Word"] == "test"
    assert fields["Language"] == "en"
    assert "trial or examination" in fields["DefinitionList"]
    assert fields["HasDefinitions"] == "1"


def test_intermediate_level_fields() -> None:
    """Test intermediate level field generation."""
    # Create richer test data
    word_data = WordData(
        word="example",
        language="en",
        part_of_speech="noun",
        senses=[
            WordSense(
                glosses=["a representative form or pattern"],
                examples=[WordExample("This is an example sentence.")],
                tags=["formal"]
            )
        ],
        synonyms=[{"word": "sample"}, {"word": "instance"}],
        pronunciation=[{"ipa": "ɪɡˈzæmpəl"}]
    )
    
    builder = CardBuilder(CardLevel.INTERMEDIATE)
    fields = builder.build_fields(word_data)
    
    # Check intermediate fields
    assert fields["Word"] == "example"
    assert fields["PartOfSpeech"] == "noun"
    assert fields["HasPartOfSpeech"] == "1"
    assert "representative form" in fields["DefinitionList"]
    assert "formal" in fields["DefinitionList"]  # Tags should be included
    assert "example sentence" in fields["DefinitionList"]  # Examples now inline
    assert fields["Pronunciation"] == "/ɪɡˈzæmpəl/"
    assert fields["HasPronunciation"] == "1"
    assert "sample" in fields["Synonyms"]
    assert fields["HasSynonyms"] == "1"
    assert fields["Examples"] == ""  # No separate examples field anymore
    assert fields["HasExamples"] == ""  # No separate examples field anymore


def test_full_level_fields() -> None:
    """Test full level field generation."""
    # Create comprehensive test data
    word_data = WordData(
        word="comprehensive",
        language="en",
        part_of_speech="adjective",
        etymology_text="From Latin comprehensivus",
        senses=[
            WordSense(
                glosses=["complete and including everything"],
                examples=[WordExample("A comprehensive study")],
                categories=["academic"],
                tags=["formal"]
            )
        ],
        synonyms=[{"word": "complete"}, {"word": "thorough"}],
        derived=[{"word": "comprehensively"}, {"word": "comprehensiveness"}],
        categories=["Education", "Academic"],
        pronunciation=[{"ipa": "ˌkɒmprɪˈhɛnsɪv"}]
    )
    
    builder = CardBuilder(CardLevel.FULL)
    fields = builder.build_fields(word_data)
    
    # Check full level fields
    assert fields["Word"] == "comprehensive"
    assert fields["Etymology"] == "From Latin comprehensivus"
    assert fields["HasEtymology"] == "1"
    assert "comprehensively" in fields["DerivedTerms"]
    assert fields["HasDerivedTerms"] == "1"
    assert "Education" in fields["Categories"]
    assert fields["HasCategories"] == "1"


def test_convenience_functions() -> None:
    """Test the convenience functions."""
    word_data = WordData(
        word="convenience",
        language="en",
        senses=[WordSense(glosses=["the state of being convenient"])]
    )
    
    # Test build_card_fields function
    fields = build_card_fields(word_data, CardLevel.BASIC)
    assert fields["Word"] == "convenience"
    
    # Test get_card_template function
    template = get_card_template(CardLevel.BASIC)
    assert template.front
    assert template.back
    assert template.css


def test_html_escaping() -> None:
    """Test that HTML is properly escaped."""
    word_data = WordData(
        word="<script>",
        language="en",
        senses=[WordSense(glosses=["a dangerous input & test"])]
    )
    
    builder = CardBuilder(CardLevel.BASIC)
    fields = builder.build_fields(word_data)
    
    # Check that HTML is escaped
    assert fields["Word"] == "&lt;script&gt;"
    assert "&amp;" in fields["DefinitionList"]


def test_empty_data_handling() -> None:
    """Test handling of empty or missing data."""
    # Test with minimal data
    word_data = WordData(word="empty", language="en")
    
    builder = CardBuilder(CardLevel.FULL)
    fields = builder.build_fields(word_data)
    
    # Should have basic fields but empty optional ones
    assert fields["Word"] == "empty"
    assert fields["Language"] == "en"
    assert fields["Etymology"] == ""
    assert fields["HasEtymology"] == ""
    assert fields["DefinitionList"] == ""


def test_field_limits() -> None:
    """Test that field content respects reasonable limits."""
    # Create data with many items
    many_synonyms = [{"word": f"synonym{i}"} for i in range(20)]
    long_etymology = "This is a very long etymology text " * 20
    
    word_data = WordData(
        word="limited",
        language="en",
        etymology_text=long_etymology,
        synonyms=many_synonyms,
        senses=[WordSense(glosses=["test definition"])]
    )
    
    builder = CardBuilder(CardLevel.FULL)
    fields = builder.build_fields(word_data)
    
    # Check that limits are applied
    assert len(fields["Etymology"]) <= 203  # 200 + "..."
    # Should have reasonable number of synonyms, not all 20
    synonym_count = fields["Synonyms"].count("<li>")
    assert synonym_count <= 8


if __name__ == "__main__":
    # Run a basic test if executed directly
    test_basic_level_fields()
    test_intermediate_level_fields()
    test_full_level_fields()
    print("All tests passed!") 