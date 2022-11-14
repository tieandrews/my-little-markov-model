import os

import numpy as np
from collections import defaultdict, Counter
import pickle


class MarkovModel:
    def __init__(self):
        """Creates a MarkovModel object."""

        self.n = None
        self.model_name = None
        self.letter_probabilities = None
        self.start_prompts = None
        self.corpus_type = None

    def fit_corpus(
        self, model_name, corpus, n, corpus_type, retrain=False, save_model=False
    ):
        """Generates next letter probability for every n-gram.

        Parameters
        ----------
        model_name : str
            Name of the model ro be used for internal reference and exporting of weights
        corpus : str
            Full text file for which to generate the ngram results for.
        n : int
            How large the n-grams should be.
        corpus_type : str
            What style of writing the text to be generated is.
            Options are: "book", "lyric", "tweet"
        retrain : bool, optional
            Whether to retrain or load pre-exisiting weights for the given model name
            and n-gram size if it already exists, by default False so it loads existing weights
        save_model : bool, optional
            Whether to save off the model weights under the models folder, by default False
        """

        self.n = n
        self.model_name = model_name
        self.corpus_type = corpus_type
        if retrain == False:
            try:
                self.load_model_weights(self.model_name, self.n)
                return
            except FileNotFoundError as e:
                print(
                    f"Didn't find existing model weights for {self.model_name}, n = {self.n}. Training now..."
                )
                pass

        # make text circular so Markov chain doesn't get stuck when generating
        circ_text = corpus + corpus[: self.n]

        encoded_text = self.encode_corpus(circ_text)

        self.generate_start_prompts(encoded_text)

        # count letter occurences followin ngram instances
        ngram_dict = defaultdict(Counter)
        for i in range(0, len(encoded_text) - self.n):
            ngram_dict[encoded_text[i : i + self.n]][encoded_text[i + self.n]] += 1

        # normalize counts into conditional probabilites
        less_than_3 = 0
        for ngram in ngram_dict:
            sum_occurences = sum(ngram_dict[ngram].values())
            if sum_occurences <= 3:
                less_than_3 += 1
            ngram_dict[ngram] = {
                key: value / sum_occurences for key, value in ngram_dict[ngram].items()
            }

        print(
            f"No of ngrams <3 occurences: {less_than_3}, total n_grams: {len(ngram_dict)}, percent: {less_than_3/len(ngram_dict)*100:.2f}%"
        )

        self.letter_probabilities = ngram_dict

        # option to export saved model to models folder
        if save_model is True:
            self.save_model_weights()

    def save_model_weights(self):
        """Saves model weights into models/markov-models folder by model name."""

        pickle_dict = {
            "model_name": self.model_name,
            "n": self.n,
            "start_prompts": self.start_prompts,
            "corpus_type": self.corpus_type,
            "letter_probabilities": self.letter_probabilities,
        }

        model_directory_path = os.path.join(
            os.getcwd(), os.pardir, "models", "markov-models", self.model_name
        )

        if not os.path.isdir(model_directory_path):
            os.makedirs(model_directory_path)

        file_name = f"{self.model_name}_{self.n}-ngrams.pkl"

        with open(os.path.join(model_directory_path, file_name), "wb") as handle:

            pickle.dump(pickle_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_model_weights(self, model_name, n):
        """Reads in pre-trained Markov Model weights.

        Parameters
        ----------
        model_name : str
            Which model name to read in from models/markov-models directpry
        n : int
            What n-gram size to read in the model weights for, can have multiple saved.
        """

        file_name = f"{model_name}_{n}-ngrams.pkl"
        model_path = os.path.join(
            os.getcwd(), os.pardir, "models", "markov-models", model_name, file_name
        )

        if not os.path.exists(model_path):

            print("Model not saved by that name/n-grams.")

        with open(model_path, "rb") as f:  # "rb" because we want to read in binary mode
            markov_model_dict = pickle.load(f)

        self.n = markov_model_dict["n"]
        self.model_name = model_name
        self.corpus_type = markov_model_dict["corpus_type"]
        self.letter_probabilities = markov_model_dict["letter_probabilities"]
        self.start_prompts = markov_model_dict["start_prompts"]

    def load_production_model(self, model_name):
        """Reads in production Markov Model weights.

        Parameters
        ----------
        model_name : str
            Which model name to read in from models/markov-models directpry
        """
        model_path = os.path.join(
            os.getcwd(), os.pardir, "models", "markov-models", model_name, "prod-model"
        )
        prod_model_files = os.listdir(model_path)
        if (not os.path.exists(model_path)) | (len(prod_model_files) == 0):
            print("No production model by that name.")
        elif len(prod_model_files) > 1:
            print("More than one model in production folder")
        else:
            for model_file in prod_model_files:
                with open(
                    os.path.join(model_path, model_file), "rb"
                ) as f:  # "rb" because we want to read in binary mode
                    markov_model_dict = pickle.load(f)

        self.n = markov_model_dict["n"]
        self.model_name = model_name
        self.corpus_type = markov_model_dict["corpus_type"]
        self.letter_probabilities = markov_model_dict["letter_probabilities"]
        self.start_prompts = markov_model_dict["start_prompts"]

    def generate_tweet(self, seq_len=80):
        """Uses the Markov Models to create a tweet including quality checks.

        Parameters
        ----------
        seq_len : int, optional
            Max length the tweet should be, may be shorter if text ends in incomplete
            sentences, by default 80

        Returns
        -------
        str
            The generated tweet.
        """

        s = self.get_start_prompt()

        while len(s) < seq_len:
            current_ngram = s[-self.n :]

            if current_ngram in self.letter_probabilities.keys():
                next_letter = np.random.choice(
                    a=list(self.letter_probabilities[current_ngram].keys()),
                    p=list(self.letter_probabilities[current_ngram].values()),
                )

            else:
                next_letter = " "

            s = s + next_letter

        trimmed_tweet = self.trim_tweet(s)

        # if valid tweet return otherwise generate a new one
        if self.validate_tweet(trimmed_tweet) is True:
            decoded_tweet = self.decode_generated_text(trimmed_tweet)
            return decoded_tweet
        else:
            return self.generate_tweet(seq_len)

    def trim_tweet(self, raw_tweet):
        """CLeans up generated tweet to remove incomplete sentences.

        Parameters
        ----------
        raw_tweet : str
            The raw Markov Model generated text string.

        Returns
        -------
        str
            The cleaned up tweet.
        """

        trimmed_tweet = raw_tweet

        if self.corpus_type == "book":
            # remove last incomplete sentence if one complete sentence exists.
            if "^" in trimmed_tweet:
                # remove last trailing line as likely incomplete
                if len(trimmed_tweet.split("^")) > 1:
                    lines = trimmed_tweet.split("^")[0:-1]
                else:
                    lines = trimmed_tweet.split("^")
                # remove last trailing sentence, likely incomplete
                sentences = [l.split(".")[0:-1] for l in lines]
                # capitalizes and removes leading spaces to help ensure new lines start with no space
                trimmed_tweet = [
                    sent.strip().capitalize() + ". "
                    for line in sentences
                    for sent in line
                ]
                # join with no spaces as spaces are maintained by the period insertion
                trimmed_tweet = "".join(trimmed_tweet)
            trimmed_tweet = trimmed_tweet.replace("“", "").replace("”", "")

        elif self.corpus_type == "tweet":
            # just get complete lines of tweets and make one complete sentence
            if "^" in trimmed_tweet:
                # remove last trailing line as likely incomplete
                if len(trimmed_tweet.split("^")) > 1:
                    lines = trimmed_tweet.split("^")[0:-1]
                else:
                    lines = trimmed_tweet.split("^")
                # remove last trailing sentence, if only one sentence, don't remove
                sentences = [
                    l.split(".")[0:-1] if len(l.split(".")) > 1 else l.strip()
                    for l in lines
                ]
                # capitalizes and removes leading spaces to help ensure new lines start with no space
                trimmed_tweet = [
                    sent.strip().capitalize() + ". "
                    for line in sentences
                    for sent in line
                ]
                # re-inserts the new line characters after they were removed in the split
                trimmed_tweet = [
                    "^" if sent == ". " else sent for sent in trimmed_tweet
                ]
                # join with no spaces as spaces are maintained by the period insertion
                trimmed_tweet = "".join(trimmed_tweet)
            # missing unique closing quote character, remove the quotes
            # if (trimmed_tweet.count("“") + trimmed_tweet.count("”")) % 2 != 0:
            trimmed_tweet = trimmed_tweet.replace("“", "").replace("”", "")
            if trimmed_tweet.count('"') % 2 != 0:
                trimmed_tweet = trimmed_tweet.replace('"', "")

        elif self.corpus_type == "lyric":
            # just get complete lines of lyrics
            if "^" in trimmed_tweet:
                lines = trimmed_tweet.split("^")[0:-1]
                lines = [l.capitalize() for l in lines]
                trimmed_tweet = "^".join(lines)
            trimmed_tweet = trimmed_tweet.replace("“", "").replace("”", "")

        # capitalize output
        trimmed_tweet = trimmed_tweet.capitalize()

        return trimmed_tweet

    def validate_tweet(self, trimmed_tweet):
        """Final checks if generated tweet meets criteria for being posted.

        Parameters
        ----------
        trimmed_tweet : str
            The generated tweet after trimming before decoding

        Returns
        -------
        bool
            Result of the validation, True if it's a valid tweet, False if it's not.
        """

        validation = True

        # if there are two many new lines for a valid tweet
        if trimmed_tweet.count("^") >= 3:
            validation = False
        # we don't want to post super short tweets
        if len(trimmed_tweet) < 60:
            validation = False

        return validation

    def encode_corpus(self, corpus):
        """Encodes certain text values to single characters so on generation new text follows
        a similar format to the corpus.

        Parameters
        ----------
        corpus : str
            The full corpus text.

        Returns
        -------
        str
            The corpus with transformations applied.
        """

        encoded_text = " ".join(
            str.split(
                corpus.lower().replace("\n", "^").replace('""', "").replace("&amp", "&")
            )
        )

        return encoded_text

    def decode_generated_text(self, string):
        """Reverses the transformations made during corpus encoding but on generated text.

        Parameters
        ----------
        string : str
            The generated text string to decode to the same corpus styling.

        Returns
        -------
        str
            The decoded string matching original corpus styling.
        """

        return string.replace("^", "\n")

    def generate_start_prompts(self, corpus, num_sentences=100):
        """Gets sentences for which the starts of will be used when generating new text.

        Parameters
        ----------
        corpus : str
            The full encoded corpus from which to pull sentences from.
        num_sentences : int, optional
            How many sentences to extract and store for use while generating. The more
            sentence options, the more varied the text will be, by default 100
        """
        if (self.corpus_type == "tweet") | (self.corpus_type == "lyric"):
            raw_sentences = corpus.split("^")
            min_char_count = 30
        elif self.corpus_type == "book":
            raw_sentences = corpus.split(".")
            min_char_count = 100
        else:
            raise ValueError(
                "Invalid corpus type {}, expect one of 'book', 'tweet', 'lyric'"
            )

        # if song lyrics, not many periods, split by encoded new line character instead
        # reduce minimum number of characters as well

        verified_sentences = []
        sentence_index = 0

        # asearch for valid prompts until quota filled or reach end of possible sentences
        while (len(verified_sentences) < num_sentences) & (
            sentence_index < len(raw_sentences)
        ):

            if len(raw_sentences[sentence_index]) > min_char_count:

                verified_sentences.append(raw_sentences[sentence_index])

            sentence_index += 1

        self.start_prompts = verified_sentences

    def get_start_prompt(self):
        """Randomly selects a start prompt to use when generating new text.

        Returns
        -------
        str
            A string of length n to start the text generation from.
        """

        sentence = np.random.choice(self.start_prompts)

        return sentence[0 : self.n]
