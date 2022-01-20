import sys
from pathlib import Path
import os

__all__ = ('update_override',)


def update_override(str_bool):
	if str_bool.lower() == 'true':
		b = True
	else:
		b = False
	print('Updating external calc version override to "{}"'.format(b))

	_dir = Path(__file__).resolve().parent # dir should be equiv to seeq/addons/clustering/_external_calc_override
	filename = _dir.joinpath('override.py')
	filename = filename.joinpath()

	f = open( filename, 'w' )
	f.write( 'ext_calc_override = ' + repr(b) + '\n' )
	f.close()
	print('done.')
	return