import argparse
import html

import mosestokenizer
import re
import codecs


class Processor:
    def __init__(self, lang: str, bpe_model=None):
        self.lang = lang
        self.word_tokenize = mosestokenizer.MosesTokenizer(self.lang)
        self.word_detokenize = mosestokenizer.MosesDetokenizer(self.lang)
        self.splitsents = mosestokenizer.MosesSentenceSplitter(self.lang)
        self.normalize = mosestokenizer.MosesPunctuationNormalizer(self.lang)

        if bpe_model:
            codes = codecs.open(bpe_model)
            #self.bpe = BPE(codes)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()

    def close(self):
        self.word_tokenize.close()
        self.word_detokenize.close()
        self.splitsents.close()
        self.normalize.close()

    def apply_bpe(self, text: str) -> str:
        """
        Apply BPE to a given text with a given BPE model
        :return: The text as a single string with BPE parts separated by spaces
        """
        return self.bpe.segment(text)

    def reverse_bpe(self, text: str) -> str:
        """
        Reverse BPE on a given BPE-split text
        :return: The text as a single string
        """
        return re.sub(r"(@@ )|(@@ ?$)",r"",text)

    def tokenize(self, text: str) -> str:
        """
        Tokenize an input text on word level.
        :return: The text as a single string, with tokens separated by spaces
        """
        # tokenizer cannot handle new line chars

        return " ".join(self.word_tokenize(text))

    def detokenize(self, text: str) -> str:
        """
        Detokenize an input text.
        :return:
        """
        # detokenizer cannot handle new line chars
        return self.word_detokenize(text.split())

    @staticmethod
    def unescape_html_entities(text: str):
        return html.unescape(text)

    @staticmethod
    def escape_newlines(text: str):
        return re.sub(r"\n", "<newline/>", text)

    @staticmethod
    def unescape_newlines(text: str):
        text = re.sub("< newline / >", r"\n", text) # for tokenized text
        return re.sub("<newline/>", r"\n", text) # for detokenized text

    def preprocess(self, text):
        text = self.escape_newlines(text)
        text = self.tokenize(text)
        text = self.unescape_html_entities(text)
        # text = self.apply_bpe(text)

        return text

    def postprocess(self, text):
        # text = self.reverse_bpe(text)
        text = self.unescape_html_entities(text)
        text = self.detokenize(text)
        text = self.unescape_newlines(text)
        return text


def get_argument_parser():
    parser = argparse.ArgumentParser(description='apply preprocessing functions')
    parser.add_argument('functions', metavar='F', nargs="+", help='the functions to apply')
    parser.add_argument('-i', '--infile')
    parser.add_argument('-o', '--outfile')
    parser.add_argument('-l', '--lang')
    parser.add_argument('--bpe')

    return parser


def main():
    args = get_argument_parser().parse_args()

    p = Processor(args.lang or 'en', bpe_model=args.bpe or None)
    text = input()
    for f_name in args.functions:
        text = getattr(p, f_name)(text)
    print(text)


if __name__ == "__main__":
    main()