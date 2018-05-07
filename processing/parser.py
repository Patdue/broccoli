import csv
import json
import argparse

import sys

from processing.processor import Processor


def iter_comment_dump(file):
    """
    Parse (iteratively) a :param file of the format described in
    https://www.reddit.com/r/datasets/comments/3bxlg7/i_have_every_publicly_available_reddit_comment/
    """
    for line in file:
        yield json.loads(line)


def write_comments(comments, attributes, file=sys.stdout):
    """
    write the :param attributes of all :param comments to a csv :param file.
    """
    writer = csv.writer(file, dialect='unix')

    with Processor('en') as p:
        for comment in comments:
            row = []
            for attribute in attributes:
                try:
                    row.append(p.preprocess(comment[attribute]))
                except TypeError:
                    row.append(comment[attribute])

            writer.writerow(row)


def get_argument_parser():
    parser = argparse.ArgumentParser(description='parse a reddit comment dump file')
    parser.add_argument('file', metavar='F', help='A reddit comment dump file')
    parser.add_argument('-e', '--extract', nargs='+', help='', default=['body'])
    parser.add_argument('-o', '--outfile', help='')

    return parser


def main():
    args = get_argument_parser().parse_args()

    with open(args.file) as fin:
        comments = iter_comment_dump(fin)

        if args.outfile:
            with open(args.outfile) as fout:
                write_comments(comments, args.extract, fout or sys.stdout)
        else:
            write_comments(comments, args.extract)


if __name__ == "__main__":
    main()