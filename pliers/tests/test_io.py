from .utils import get_test_data_path
from pliers.stimuli import (load_stims, AudioStim, ImageStim)
from pliers.extractors import (STFTAudioExtractor,
                               GoogleVisionAPIFaceExtractor,
                               ExtractorResult)
from pliers.export import to_long_format
from pliers.graph import Graph
from os.path import join
from six import string_types
import pytest

import pytest


def test_magic_loader():
    text_file = join(get_test_data_path(), 'text', 'sample_text.txt')
    audio_file = join(get_test_data_path(), 'audio', 'barber.wav')
    video_file = join(get_test_data_path(), 'video', 'small.mp4')
    stim_files = [text_file, audio_file, video_file]
    stims = load_stims(stim_files)
    assert len(stims) == 3
    assert round(stims[1].duration) == 57
    assert isinstance(stims[0].text, string_types)
    assert stims[2].width == 560


def test_magic_loader2():
    text_file = join(get_test_data_path(), 'text', 'sample_text.txt')
    video_url = 'http://www.obamadownloads.com/videos/iran-deal-speech.mp4'
    audio_url = 'http://www.bobainsworth.com/wav/simpsons/themodyn.wav'
    image_url = 'https://www.whitehouse.gov/sites/whitehouse.gov/files/images/twitter_cards_potus.jpg'
    text_url = 'https://github.com/tyarkoni/pliers/blob/master/README.md'
    stims = load_stims([text_file, video_url, audio_url, image_url, text_url])
    assert len(stims) == 5
    assert stims[1].fps == 12
    assert stims[3].data.shape == (240, 240, 3)


def test_loader_nonexistent():
    text_file = 'this/doesnt/exist.txt'
    with pytest.raises(IOError):
        stims = load_stims(text_file)

    audio_file = 'no/audio/here.wav'
    with pytest.raises(IOError):
        stims = load_stims([text_file, audio_file])

    text_file = join(get_test_data_path(), 'text', 'sample_text.txt')
    stims = load_stims([text_file, audio_file], fail_silently=True)
    assert len(stims) == 1

    with pytest.raises(IOError):
        stims = load_stims(audio_file, fail_silently=True)


def test_convert_to_long():
    audio_dir = join(get_test_data_path(), 'audio')
    stim = AudioStim(join(audio_dir, 'barber.wav'))
    ext = STFTAudioExtractor(frame_size=1., spectrogram=False,
                        freq_bins=[(100, 300), (300, 3000), (3000, 20000)])
    timeline = ext.transform(stim)
    long_timeline = to_long_format(timeline)
    assert long_timeline.shape == (timeline.to_df().shape[0] * 3, 4)
    assert 'feature' in long_timeline.columns
    assert 'value' in long_timeline.columns
    assert '100_300' not in long_timeline.columns
    timeline = ExtractorResult.merge_features([timeline])
    long_timeline = to_long_format(timeline)
    assert 'feature' in long_timeline.columns
    assert 'extractor' in long_timeline.columns
    assert '100_300' not in long_timeline.columns


@pytest.mark.skipif("'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ")
def test_convert_to_long_graph():
    image_dir = join(get_test_data_path(), 'image')
    stim = ImageStim(join(image_dir, 'obama.jpg'))
    ext = GoogleVisionAPIFaceExtractor()
    g = Graph([ext])
    timeline = g.run(stim)
    long_timeline = to_long_format(timeline)
    assert 'feature' in long_timeline.columns
    assert 'extractor' in long_timeline.columns
    assert 'history' in long_timeline.columns
