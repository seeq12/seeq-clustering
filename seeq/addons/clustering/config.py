import sys

def checksum(checksum):
    f = open( './app/clusterApp/checksum.py', 'w' )
    f.write( 'checksum = ' + repr(checksum) + '\n' )
    f.close()
    return


if __name__ == '__main__':
    try:
        globals()[sys.argv[1]](sys.argv[2])
    except IndexError:
        if len(sys.argv) == 1:
            raise ValueError('No configuration function specified. Options are "checksum"')
        else:
            raise ValueError('Please specify a single argument for function: {}'.format(sys.argv[1]))