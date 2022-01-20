import sys
from pathlib import Path
import os

__all__ = ('update_checksum',)


def update_checksum(checksum):
    print('Updating checksum to "{}"'.format(checksum))

    _dir = Path(__file__).resolve().parent.parent #dir should be equiv to seeq/addons/clustering
    filename = _dir.joinpath('app').joinpath('clusterApp').joinpath('checksum.py')
    filename = filename.joinpath()

    f = open( filename, 'w' )
    f.write( 'checksum = ' + repr(checksum) + '\n' )
    f.close()
    print('done.')
    return