import os
import sys
import pytest

cur_dir = os.getcwd()
src_path = cur_dir[
    : cur_dir.index("my-little-markov-model") + len("my-little-markov-model")
]
if src_path not in sys.path:
    sys.path.append(src_path)

from src.data.corpus import Corpus


def test_return_type():

    corp = Corpus(corpus_name="test")
    corp.load_corpus()

    assert type(corp.name) == str
    assert type(corp.raw_text) == str


def test_file_not_found():

    with pytest.raises(FileNotFoundError):
        corp = Corpus("does-not-exist")
        corp.load_corpus()


@pytest.mark.parametrize("corpus_name", [(123), (1.23), ([1, 2, 3])])
def test_invalid_corpus_name(corpus_name):

    with pytest.raises(TypeError):
        corp = Corpus(corpus_name)
