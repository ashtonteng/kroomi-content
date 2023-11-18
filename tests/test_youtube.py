import pytest

from youtube import *


def setup_function():
    pass


def teardown_function():
    pass


def test_extract_youtube_video_id():
    video_id = "sYyVi-H-ozI"
    assert extract_youtube_video_id(
        "https://youtu.be/sYyVi-H-ozI?si=FXsmI_AILXYU2oBA"
    ) == video_id
    assert extract_youtube_video_id(
        "https://www.youtube.com/watch?v=sYyVi-H-ozI"
    ) == video_id
    assert extract_youtube_video_id(
        "https://youtu.be/sYyVi-H-ozI"
    ) == video_id
    with pytest.raises(ValueError):
        extract_youtube_video_id("https://www.google.com")
    # assert extract_youtube_video_id(
    #     "https://youtu.be/sYyVi-H-ozI/"
    # ) == video_id
    # assert extract_youtube_video_id(
    #     "www.youtu.be/sYyVi-H-ozI"
    # ) == video_id
    # assert extract_youtube_video_id(
    #     "youtu.be/sYyVi-H-ozI"
    # ) == video_id
