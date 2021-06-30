import sys
import json

def checksum(checksum):
	data = {'checksum':checksum}
	with open("./app/clusterApp/checksum.json", "w") as outfile:
		json.dump(data, outfile)
	return


if __name__ == '__main__':
	try:
		globals()[sys.argv[1]](sys.argv[2])
	except IndexError:
		if len(sys.argv) == 1:
			raise ValueError('No configuration function specified. Options are "checksum"')
		else:
			raise ValueError('Please specify a single argument for function: {}'.format(sys.argv[1]))