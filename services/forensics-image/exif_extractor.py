
from datetime import datetime
from typing import Optional, Tuple

from PIL import Image
from PIL.ExifTags import TAGS
from pydantic import BaseModel


class EXIFData(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    software: Optional[str] = None
    gpsCoords: Optional[Tuple[float, float]] = None
    dateOriginal: Optional[str] = None
    modifyDate: Optional[str] = None
    gpsCoherent: bool = True
    editorDetected: bool = False
    suspicionScore: int = 0


class EXIFExtractor:
    EDITORS = [
        "photoshop",
        "gimp",
        "lightroom",
        "canva",
        "snapseed",
        "picsart",
    ]

    def extract(self, image_path: str) -> EXIFData:
        image = Image.open(image_path)
        raw_exif = image.getexif()

        if not raw_exif:
            return EXIFData(
                editorDetected=False,
                gpsCoherent=False,
                suspicionScore=40,
            )

        exif = {
            TAGS.get(tag_id, tag_id): value
            for tag_id, value in raw_exif.items()
        }

        software = str(exif.get("Software", "")).strip() or None
        make = str(exif.get("Make", "")).strip() or None
        model = str(exif.get("Model", "")).strip() or None
        date_original = str(exif.get("DateTimeOriginal", "")).strip() or None
        modify_date = str(exif.get("DateTime", "")).strip() or None

        editor_detected = self.detect_editor(software)
        gps_coords = None

        suspicion = 0

        if editor_detected:
            suspicion += 30

        if not make or not model:
            suspicion += 10

        if date_original and modify_date:
            try:
                d1 = datetime.strptime(date_original, "%Y:%m:%d %H:%M:%S")
                d2 = datetime.strptime(modify_date, "%Y:%m:%d %H:%M:%S")

                if d2 > d1:
                    suspicion += 20
            except Exception:
                suspicion += 5

        return EXIFData(
            make=make,
            model=model,
            software=software,
            gpsCoords=gps_coords,
            dateOriginal=date_original,
            modifyDate=modify_date,
            gpsCoherent=True,
            editorDetected=editor_detected,
            suspicionScore=min(suspicion, 100),
        )

    def detect_editor(self, software: Optional[str]) -> bool:
        if not software:
            return False

        software = software.lower()

        return any(editor in software for editor in self.EDITORS)
