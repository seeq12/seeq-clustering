import sys

def checksum(checksum):
    print('Updating checksum to {}'.format(checksum))
    f = open( './app/clusterApp/checksum.py', 'w' )
    f.write( 'checksum = ' + repr(checksum) + '\n' )
    f.close()
    print('done.')
    return


if __name__ == '__main__':
    try:
        if sys.argv[1] != 'checksum':
            raise ValueError('Incorrect configuration function specified. Options are "checksum"')
        globals()[sys.argv[1]](sys.argv[2])
    except IndexError:
        if len(sys.argv) == 1:
            raise ValueError('No configuration function specified. Options are "checksum"')
        else:
            raise ValueError('Please specify a single argument for function: {}'.format(sys.argv[1]))