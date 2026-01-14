"""
HTML Cleaning Utility with BeautifulSoup
Membersihkan HTML dari tag, whitespace, dan karakter tidak perlu
"""

import re
from typing import Optional, List, Dict
from bs4 import BeautifulSoup, Tag


def clean_html(html_text: str, parser: str = 'lxml') -> str:
    """
    Membersihkan HTML menjadi plain text menggunakan BeautifulSoup
    
    Args:
        html_text: String HTML yang akan dibersihkan
        parser: Parser yang digunakan ('lxml', 'html.parser', dll)
        
    Returns:
        Plain text yang sudah dibersihkan
    """
    if not html_text:
        return ""
    
    # Parse HTML dengan BeautifulSoup
    soup = BeautifulSoup(html_text, parser)
    
    # Hapus script dan style tags
    for script in soup(['script', 'style']):
        script.decompose()
    
    # Get text
    text = soup.get_text(separator='\n')
    
    # Bersihkan whitespace berlebih
    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]  # Hapus baris kosong
    text = '\n'.join(lines)
    
    return text.strip()


def extract_text_from_element(
    html_text: str, 
    tag: str, 
    class_name: Optional[str] = None,
    id_name: Optional[str] = None,
    parser: str = 'lxml'
) -> str:
    """
    Ekstrak text dari element HTML tertentu menggunakan BeautifulSoup
    
    Args:
        html_text: String HTML
        tag: Tag HTML yang dicari (contoh: 'div', 'span', 'p')
        class_name: Class name dari element (optional)
        id_name: ID dari element (optional)
        parser: Parser yang digunakan
        
    Returns:
        Text yang sudah dibersihkan dari element tersebut
    """
    soup = BeautifulSoup(html_text, parser)
    
    # Cari element
    if id_name:
        element = soup.find(tag, id=id_name)
    elif class_name:
        element = soup.find(tag, class_=class_name)
    else:
        element = soup.find(tag)
    
    if element:
        return clean_html(str(element), parser)
    
    return ""


def extract_structured_data(
    html_text: str,
    selectors: Dict[str, str],
    parser: str = 'lxml'
) -> Dict[str, str]:
    """
    Ekstrak data terstruktur dari HTML menggunakan CSS selectors
    
    Args:
        html_text: String HTML
        selectors: Dictionary dengan key=field_name, value=css_selector
        parser: Parser yang digunakan
        
    Returns:
        Dictionary dengan data yang sudah diekstrak
    """
    soup = BeautifulSoup(html_text, parser)
    result = {}
    
    for field_name, selector in selectors.items():
        element = soup.select_one(selector)
        if element:
            result[field_name] = element.get_text(strip=True)
        else:
            result[field_name] = ""
    
    return result


def extract_list_items(
    html_text: str,
    container_selector: str,
    item_selector: str,
    parser: str = 'lxml'
) -> List[str]:
    """
    Ekstrak list items dari HTML
    
    Args:
        html_text: String HTML
        container_selector: CSS selector untuk container
        item_selector: CSS selector untuk items
        parser: Parser yang digunakan
        
    Returns:
        List of strings
    """
    soup = BeautifulSoup(html_text, parser)
    container = soup.select_one(container_selector)
    
    if not container:
        return []
    
    items = container.select(item_selector)
    return [item.get_text(strip=True) for item in items]


def remove_extra_whitespace(text: str) -> str:
    """
    Hapus whitespace berlebih dari text
    
    Args:
        text: Text yang akan dibersihkan
        
    Returns:
        Text tanpa whitespace berlebih
    """
    # Ganti multiple spaces dengan single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def normalize_text(text: str) -> str:
    """
    Normalisasi text: lowercase, hapus karakter spesial, dll
    
    Args:
        text: Text yang akan dinormalisasi
        
    Returns:
        Text yang sudah dinormalisasi
    """
    # Lowercase
    text = text.lower()
    
    # Hapus karakter spesial kecuali alphanumeric dan whitespace
    text = re.sub(r'[^a-z0-9\s]', '', text)
    
    # Hapus whitespace berlebih
    text = remove_extra_whitespace(text)
    
    return text
