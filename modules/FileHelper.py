import os, re, sys, getopt, fnmatch, shutil
from distutils import dir_util

path_sep = os.path.sep

# getFileStr
# Returns the string content of the file
# 
# @param {String} source - path or actual file
# 
# @retruns {String} - the source of the file in string format
def getFileStr(source):
	file_open = fileOpen(source) if type(source) is str else source
	lines = file_open.readlines()
	file_open.close()
	new_str = "".join(lines)
	return new_str

# fileOpen
# Reads the file
# 
# @param {String} source_path - source of the file
# 
# @returns {File}
def fileOpen(source_path):
	file_open = open(source_path, "r")
	return file_open


# writeFile
# Writes the string as a new file
# 
# @param {String} output_str - string to write to the file
# @param {String} file_path - path to the file to write to
def writeFile(output_str, file_path = None):

	if not file_path:
		print '[FileHelper.writeFile] Requires file_path.'

	else:

		path = file_path.split(path_sep)
		
		if len(path) > 1:
			# check if the folder exists
			folder_path = path_sep.join(path[:-1])

			# if it doesn't create the path
			if not os.path.isdir(folder_path):
				try:
					os.makedirs(folder_path)
					print '[FileHelper.writeFile] Folder path created: ' + folder_path
				except OSError, e:
					print '[FileHelper.writeFile] Cannot create the folder path: ' + folder_path
					print '[FileHelper.writeFile] (Error Code: ' + e.errno + ' )'


		output_file = open(file_path, 'w')
		output_file.write(output_str)
		output_file.close()


# getFilePaths
# Gets the file paths 
# 
# @param {String} source_path - path to the file/files
# @param {String} file_ext - file extension to grab (default: txt)
# @param {boolean} recursive - turn on/off recursion
# 
# @returns {File[]} - files in an array
def getFilePaths(source_path, file_ext = 'txt', recursive = True):
	
	return_arr = []

	# check if file
	if os.path.isfile(source_path):
		
		# only if it's that extension
		if (source_path.endswith(file_ext)):
			return_arr.append(source_path)

	# if directory
	elif os.path.isdir(source_path):
		
		# depth=infinity
		file_ext = '*.' + file_ext

		level = 0

		for root, dirnames, filenames in os.walk(source_path):
			level += 1

			if not recursive and level > 1:
				break
			else:
				for filename in fnmatch.filter(filenames, file_ext):
					return_arr.append(os.path.join(root, filename))

	return return_arr


# copyFile
# Copy the same file to a different directory
# 
# @param {string} source_file Source file
# @param {string} dest_path Destination file
def copyFile(source_file, dest_path):
	ret = 0
	dest_file = dest_path + source_file.split(path_sep)[-1]
	source_path = path_sep.join(source_file.split(path_sep)[:-1])

	if os.path.isfile(source_file) and os.path.isdir(dest_path) and not os.path.samefile(source_path, dest_path):
		try:
			shutil.copyfile(source_file, dest_file)
			ret = 1
		except:
			ret = 0
	
	return ret

# copyDir
# Copy the whole director to destination path
# 
# @param {string} source_path
# @param {string} dest_path
def copyDir(source_path, dest_path):
	ret = 0

	if os.path.isdir(source_path) and os.path.isdir(dest_path):
		try:
			dir_util.copy_tree(source_path, dest_path)
			ret = 1
		except:
			ret = 0
	
	return ret


# getFileLists
# Recursive file list
# 
# @param {string} source_path
# 
# @return {list}
def _getFileLists(source_path, ext = None, full_path = 0):

	matches = []
	for root, dirnames, filenames in os.walk(source_path):

		if ext:

			for filename in fnmatch.filter(filenames, '*.' + ext):
				if full_path:
					matches.append(os.path.join(root, filename))
				else:
					folder_path = re.sub(source_path, '', root).strip()
					file_path = ((folder_path + path_sep) if len(folder_path) > 0 else '') + filename
					matches.append(file_path)

		else:

			for filename in fnmatch.filter(filenames):
				if full_path:
					matches.append(os.path.join(root, filename))
				else:
					folder_path = re.sub(source_path, '', root).strip()
					file_path = ((folder_path + path_sep) if len(folder_path) > 0 else '') + filename
					matches.append(file_path)

	return matches