import os
import sys
import argparse
from ._config import update_checksum


def cli_interface():
    """ Update script name for clustering Seeq Add-on Tool """
    parser = argparse.ArgumentParser(description='Configuration for Clustering.')
    parser.add_argument('--script_name', type=str,
                        help='Script name from external-calc')
    return parser.parse_args()


if __name__ == '__main__':

    args = cli_interface()

    update_checksum(args.script_name)