import numpy as np
from odp_platform.frame_source.factory import create_frame_source
from odp_platform.frame_source.core.types import SourceType

def test_create_image_source(tmp_path):
    import cv2
    img_path = tmp_path / "test.jpg"
    cv2.imwrite(str(img_path), np.zeros((100, 100, 3), dtype=np.uint8))
    src = create_frame_source(str(img_path))
    assert src.source_type == SourceType.IMAGE

def test_create_invalid_source_raises():
    import pytest
    with pytest.raises(ValueError, match="不存在"):
        create_frame_source("/nonexistent/path.jpg")
