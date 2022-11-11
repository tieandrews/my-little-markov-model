import os


class Corpus:
    def __init__(self, corpus_name):
        """An object to store/manage corpuses.

        Parameters
        ----------
        corpus_name : str
            The name for which to refer to the given corpus.
        """
        if type(corpus_name) != str:
            raise TypeError(f"Corpus name must be of type str, got {type(corpus_name)}")

        self.name = corpus_name
        self.raw_text = None

    def load_corpus(self):
        """Loads in the raw corpus from the raw data folder by model name.

        Looks in data/raw/corpuses/{model_name}.
        """

        cur_dir = os.getcwd()
        src_path = cur_dir[
            : cur_dir.index("my-little-markov-model") + len("my-little-markov-model")
        ]
        corpus_path = os.path.join(src_path, "data", "raw", "corpuses", self.name)

        for file in os.listdir(corpus_path):
            # Check whether file is in text format or not
            if file.endswith(".txt"):
                file_path = os.path.join(corpus_path, file)

                with open(file_path, encoding="utf8") as f:
                    lines = f.read()

        self.raw_text = lines
