
from exif_extractor import EXIFExtractor


def test_detect_editor():
    extractor = EXIFExtractor()

    assert extractor.detect_editor("Adobe Photoshop") is True
    assert extractor.detect_editor("GIMP") is True
    assert extractor.detect_editor("iPhone Camera") is False


def test_empty_software():
    extractor = EXIFExtractor()

    assert extractor.detect_editor("") is False
