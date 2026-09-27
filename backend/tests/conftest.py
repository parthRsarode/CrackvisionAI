import io
import pytest
import numpy as np
from PIL import Image, ImageDraw

@pytest.fixture
def blank_image_bytes() -> bytes:
    """Generate blank concrete-colored image bytes (no cracks)."""
    img = Image.new("RGB", (640, 640), color=(180, 180, 180))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()

@pytest.fixture
def synthetic_crack_image_bytes() -> bytes:
    """Generate image with a prominent dark line simulating a crack fissure."""
    img = Image.new("RGB", (640, 640), color=(190, 190, 190))
    draw = ImageDraw.Draw(img)
    # Draw dark jagged line from top-left towards center-right
    points = [
        (100, 100), (140, 180), (160, 240), (210, 310),
        (230, 390), (280, 470), (320, 540)
    ]
    draw.line(points, fill=(20, 20, 20), width=4)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()

@pytest.fixture
def tie_hole_image_bytes() -> bytes:
    """Generate image with a circular dark spot simulating a formwork tie hole."""
    img = Image.new("RGB", (640, 640), color=(185, 185, 185))
    draw = ImageDraw.Draw(img)
    # Circular tie hole (aspect ratio ~1.0:1)
    draw.ellipse([(280, 280), (360, 360)], fill=(30, 30, 30))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()
