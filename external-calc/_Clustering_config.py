FILE = open('Clustering.py', 'r')
list_of_lines = FILE.readlines()

import sys
import os

def clusteringModelsPath(path):
	path = path.replace('\\', '/')
	print("updating models path to {}".format(path))
	list_of_lines[1] = "wkdir = '{}'\n".format(path)

	a_file = open("Clustering.py", "w")
	a_file.writelines(list_of_lines)
	a_file.close()
	return


if __name__ == '__main__':
	try:
		if sys.argv[1] != 'clusteringModelsPath':
			raise ValueError('Incorrect configuration function specified. Options are "clusteringModelsPath"')
		globals()[sys.argv[1]](sys.argv[2])
	except IndexError:
		if len(sys.argv) == 1:
			raise ValueError('No configuration function specified. Options are "clusteringModelsPath"')
		else:
			globals()[sys.argv[1]](os.getcwd())
