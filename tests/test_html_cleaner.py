"""
Test untuk HTML Cleaner utility
"""

from app.utils.html_cleaner import (
    clean_html,
    extract_text_from_element,
    remove_extra_whitespace,
    normalize_text
)


def test_clean_html_basic():
    """Test cleaning HTML sederhana"""
    html = "<p>Hello <b>World</b></p>"
    result = clean_html(html)
    assert result == "Hello World"


def test_clean_html_with_breaks():
    """Test cleaning HTML dengan line breaks"""
    html = "<p>Line 1</p><br><p>Line 2</p>"
    result = clean_html(html)
    assert "Line 1" in result
    assert "Line 2" in result


def test_clean_html_with_scripts():
    """Test menghapus script tags"""
    html = "<div>Content</div><script>alert('test')</script>"
    result = clean_html(html)
    assert result == "Content"
    assert "alert" not in result


def test_clean_html_with_entities():
    """Test unescape HTML entities"""
    html = "<p>Hello&nbsp;World &amp; Friends</p>"
    result = clean_html(html)
    assert "Hello World & Friends" in result


def test_extract_text_from_element():
    """Test ekstrak text dari element tertentu"""
    html = "<div class='profile-name'>John Doe</div><div>Other content</div>"
    result = extract_text_from_element(html, 'div', 'profile-name')
    assert result == "John Doe"


def test_remove_extra_whitespace():
    """Test menghapus whitespace berlebih"""
    text = "Hello    World   Test"
    result = remove_extra_whitespace(text)
    assert result == "Hello World Test"


def test_normalize_text():
    """Test normalisasi text"""
    text = "Hello World! 123"
    result = normalize_text(text)
    assert result == "hello world 123"


if __name__ == "__main__":
    # Run basic tests
    test_clean_html_basic()
    test_clean_html_with_breaks()
    test_clean_html_with_scripts()
    test_clean_html_with_entities()
    test_extract_text_from_element()
    test_remove_extra_whitespace()
    test_normalize_text()
    print("✓ All tests passed!")
