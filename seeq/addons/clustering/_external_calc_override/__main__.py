import os
import sys
import argparse
from ._config import update_override


def cli_interface():
    """ Update script name for clustering Seeq Add-on Tool """
    parser = argparse.ArgumentParser(description='Configuration for Overriding external calc version (to R54).')
    parser.add_argument('--override', type=str, default='true',
                        help='Setting override to True will force the >R54 version of ext-calc.')
    return parser.parse_args()


if __name__ == '__main__':

    args = cli_interface()

    update_override(args.override)