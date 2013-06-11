# JS Documentation Parser
# @version 0.0.2
# 
# This parser will not go through your code and translate it for you.
# It will all depend on the accuracy of your documentation.
# 
# It follows most of the key JS Doc tags to the tee, with some variations 
# to adapt to our coding styles in-house
# 
import sys, getopt, subprocess, re, hashlib, os
import json, csv
import FileHelper, StringHelper, DictHelper, HTMLBuilder

# globals
log_arr = []
path_sep = os.path.sep

# parse
def parse(config):
	return JSDoc_Constructor(config)

# getComments
# Get the comment blocks in the file
# 
# @param {String} file_str File from the string
# 
# @returns {String[]} List of comments
def _getComments(file_str):
	regex = re.compile(r'/\*\*(.+?)\*/', re.DOTALL)
	comments = re.findall(regex, file_str)

	comments = comments if isinstance(comments, list) else []
	return comments


# parseComment
# Parse the comment block
# 
# @param {String} comment Comment string
# @param {string} file_id file identifier
# 
# @returns {Object} Comment information
def _parseComment(comment, file_id):

	# break down by lines
	reg_perline = re.compile(r'(.+)\n', re.MULTILINE)
	lines = re.findall(reg_perline, comment)

	comment_arr = []
	doc = 0

	# remove unecessary chars
	for i, ln in enumerate(lines):
		lns = StringHelper.fullStrip(ln)
		lns = re.sub(r'^\*', '', lns)
		lns = lns.strip()

		if len(lns) > 0:
			comment_arr.append(lns)

	if len(comment_arr) > 0 :

		doc_type = _getType(comment_arr[0])
		doc_name = _getTypeName(comment_arr[0])

		if doc_type == 'overview':

			doc = {}

			# doc names can be multiple words
			doc_name = _getTypeName(comment_arr[0], 0, 1)

			# type
			doc['type'] = doc_type	

			# type name
			if doc_name:
				doc['name'] = doc_name

			# description
			doc['desc'] = _getTypeDescription(comment_arr)

		elif doc_type and doc_name:

			doc = {}

			# type
			doc['type'] = doc_type	

			# type name
			doc['name'] = doc_name

			# member of
			member = _getMemberOf(comment_arr)
			if member:
				doc['parent_constructor'] = member
				ident = file_id + member + doc_name + doc_type
			else:
				ident = file_id + doc_name + doc_type

			# identifier
			doc_id = hashlib.md5()
			doc_id.update(ident)
			doc['id'] = doc_id.hexdigest()

			# description
			doc['desc'] = _getTypeDescription(comment_arr)

			# examples
			doc['ex'] = _getTypeDescription(comment_arr, 'example')

			# params
			doc['params'] = _getParams(comment_arr)
			
			# requires
			doc['requires'] = _getRequires(comment_arr)

			# private/public
			scope = _getScope(comment_arr)
			if scope:
				doc['scope'] = scope

	return doc


# getType
# Get the type of the comment block
# 
# @param {String} str Comment string
# 
# @returns {String|Boolean}
def _getType(str):
	ret = 0

	if re.match(r'^\@(constructor|object)', str, re.IGNORECASE):
		ret = 'constructor'
	elif re.match(r'^\@function', str, re.IGNORECASE):
		ret = 'function'
	elif re.match(r'^\@namespace', str, re.IGNORECASE):
		ret = 'namespace'
	elif re.match(r'^\@name', str, re.IGNORECASE):
		ret = 'name'
	elif re.match(r'^\@fileOverview', str, re.IGNORECASE):
		ret = 'overview'

	return ret


# getMemberOf
# Get the memberOf value
# 
# @param {List} arr Comments
# 
# @returns {String|Boolean}
def _getMemberOf(arr):
	ret = 0
	for i, ln in enumerate(arr):

		if re.match(r'\@memberOf', ln, re.IGNORECASE):
			
			sp = StringHelper.fullStrip(ln)
			sp = sp.split(' ')
			if len(sp) > 1:
				ret = sp[1]

			break

	# if nothing, try checking this type's name
	if not ret:

		doc_name = _getTypeName(arr[0], 1)

		if doc_name:

			# if on dot notation
			if len(doc_name.split('.')) > 1:
				ret = '.' . join(doc_name.split('.')[:-1])

	return ret


# getScope
# Get the scope
# 
# @param {List} arr Comments
# 
# @returns {String|Boolean}
def _getScope(arr):
	ret = 0
	for i, ln in enumerate(arr):

		if re.match(r'\@private', ln, re.IGNORECASE):
			ret = 'private'
			break
		elif re.match(r'\@public', ln, re.IGNORECASE):
			ret = 'public'
			break

	return ret



# getTypeName
# Get the Name of the type
# 
# @param {String} str Comment string
# @param {boolean} full_namespace If output the name with the full dot notation (ex. MyConstructor.myFunctionName )
# 
# @returns {String|Boolean}
# 
def _getTypeName(str, full_namespace = None, multi_word = None):
	ret = 0
	sp = StringHelper.fullStrip(str)
	sp = sp.split(' ')

	if len(sp) > 1:
		ret = sp[1]

		if multi_word:
			ret = ' '.join(sp[1:])

		elif not full_namespace and ret and len(ret.split('.')) > 0:
			ret = ret.split('.')[-1]

	return ret


# getTypeDescription
# Get the type's description and example
# 
# @param {List} arr Comments
# 
# @returs {String}
def _getTypeDescription(arr, desc_type = 'description'):
	desc = []

	desc_found = 0
	desc_parse_stop = 0
	
	if desc_type == 'example':
		regex = re.compile(r'^\@example', re.IGNORECASE)
	else:
		regex = re.compile(r'^\@description', re.IGNORECASE)

	for i, ln in enumerate(arr):

		# first line
		if i == 0 and desc_type == 'description':

			sp = StringHelper.fullStrip(ln)
			sp = sp.split()
			
			if len(sp) > 2 and not re.match(r'\@fileOverview', ln, re.IGNORECASE):

				desc_attr = ' '.join(sp[2:])
				desc_attr = StringHelper.fullStrip(desc_attr)
				desc_attr = re.sub(r'^\-', '', desc_attr)
				desc_attr = desc_attr.strip()

				if len(desc_attr) > 0:
					desc.append(desc_attr)
		
		else:

			# description stops until there is another doc notation not name @description
			if re.match(r'^\@', ln, re.IGNORECASE) and not desc_parse_stop:
				
				if regex.search(ln):

					desc_found = 1

					sp = StringHelper.fullStrip(ln)
					sp = sp.split()

					if len(sp) > 1:

						desc_attr = ' '.join(sp[1:])
						desc_attr = StringHelper.fullStrip(desc_attr)
						desc_attr = re.sub(r'^\-', '', desc_attr)
						desc_attr = desc_attr.strip()
					
						if len(desc) > 0:
							desc_attr = '\n' + desc_attr

						desc.append(desc_attr)
				
				else:

					# stop parsing
					if desc_found:
						desc_parse_stop = 1

			elif not desc_parse_stop and desc_found:
				
				desc_attr = StringHelper.fullStrip(ln)

				if len(desc) > 0:
					desc_attr = '\n' + desc_attr

				desc.append(desc_attr)
	
	ret = ' '.join(desc)
	return ret



# getParams
# Get the params
# 
# @param {List} arr Comments
# 
# @returns {String}
def _getParams(arr):
	params = []

	for i, ln in enumerate(arr):

		if re.match(r'\@(param|property|return)', ln, re.IGNORECASE):

			is_returns = re.match(r'\@return', ln, re.IGNORECASE)

			#clean it up
			sp = StringHelper.fullStrip(ln)
			sp = sp.split()
			
			if len(sp) > 2:

				# get param type
				idx = 1
				regex = re.compile(r'\{(.+?)\}', re.IGNORECASE)
				param_type = re.findall(regex, sp[idx])
				
				# if not there, try the next one
				if len(param_type) == 0:
					idx = 2
					param_type = re.findall(regex, sp[idx])
				
				# if found
				if len(param_type) > 0:
					param_type = param_type[0]
				else:
					param_type = 0

				if param_type:

					param_type = param_type.lower()

					param_var = sp[1] if idx == 2 else sp[2]

					#clean up param variable
					param_var = StringHelper.fullStrip(param_var)
					param_var = re.sub(r'-', '', param_var)
					
					# no param name for @return
					if is_returns:
						param_var = ''					


					# param description
					param_desc = ''
					if is_returns:

						if len(sp) > 2:
							param_desc = ' '.join(sp[2:])
					else:

						if len(sp) > 3:
							param_desc = ' '.join(sp[3:])
						
					# clean it up
					param_desc = StringHelper.fullStrip(param_desc)
					param_desc = re.sub(r'^\-', '', param_desc)
					param_desc = param_desc.strip()

					# param code
					param_code = '@return' if is_returns else '@param'
					
					obj = {
						'code': param_code,
						'type': param_type,
						'name': param_var,
						'desc': param_desc
					}

					params.append(obj)

	# group related params
	grouped = {}
	remain_arr = []
	for i, p in enumerate(params):

		# if param only and in dot.notation, check
		if p['code'] == '@param' and len(p['name'].split('.')) > 1:

			base_key = p['name'].split('.')[0]

			# create array if not yet created
			if not base_key in grouped:
				grouped[base_key] = []

			grouped[base_key].append(p)

		else:

			remain_arr.append(p)

	# put the grouped params in their respective parent key
	for i, p in enumerate(remain_arr):

		p_name = p['name']

		if p_name in grouped:

			remain_arr[i]['sub_params'] = grouped[p_name]
			# remove from grouped
			del grouped[p_name]

	# if there's anything left in grouped, put it back
	for i in grouped:

		for x, p in enumerate(group[i]):
			remain_arr.append(p)

	#re-assign back
	params = remain_arr

	return params


# getRequires
# Get the @requires
# 
# @param {List} arr Comment string
# 
# @returns {String}
def _getRequires(arr):
	requires = []

	for i, ln in enumerate(arr):

		if re.match(r'\@requires', ln, re.IGNORECASE):

			sp = ln.split(' ')
			if (sp > 1):
				requires.append(' '.join(ln.split(' ')[1:]))

	return requires


# buildDynamicMultiLevelDict
# Build dynamic multi-level dictionary!!!!!!
# 
# @param {List} arr Comments
# 
# @returns {dict}
def _buildDynamicMultiLevelDict(arr):

	constructors = {}

	for i, item in enumerate(arr):

		if 'parent_constructor' in item:

			temp = {}

			sp = item['parent_constructor'].split('.')

			for z, level in enumerate(sp):

				if z == 0 and not level in constructors:

					constructors[level] = {}

				elif z > 0:

					temp = constructors[sp[z-1]]

					if not level in temp:
						temp[level] = {}

					temp = temp[level]

	print constructors


# groupConstructors
# Groupings
# 
# @param {List} arr Comments
# 
# @return {dict}
def _groupContstructors(arr):

	# build constructor dictionary
	dict_arr = []
	constructors = {}

	# get the file overview (first in the list only)
	overview = 0
	first_item = arr[0]

	if first_item['type'] == 'overview':
		overview = first_item
		# remove from list
		del arr[0]

	# delete other overviews
	for i, item in enumerate(arr):

		if item['type'] == 'overview':
			del arr[i]

	tmp_arr = []

	# get all constructors that does not have a parent -- all top level
	for i, item in enumerate(arr):
		
		if 'name' in item:

			c_name = item['name']	
			i_type = item['type']

			if not 'parent_constructor' in item and any(i_type in st for st in ['constructor', 'namespace']):

				if not c_name in constructors.keys():

					constructors[c_name] = dict()
					#constructors = DictHelper.addKeyToDict(c_name, dict(), constructors)

					# add information about the constructor
					c_name = '.'.join([item['name'], '__info__'])
					constructors = DictHelper.addKeyToDict(c_name, item, constructors)

				else:
					_log('[warning] ' + c_name + ' constructor already exists!')

			else:

				tmp_arr.append(item)

			
	tmp_arr_2 = []
	# go through all the constructors that has dependencies
	for i, item in enumerate(tmp_arr):

		if 'name' in item:
			
			i_name = item['name']
			i_type = item['type']

			if 'parent_constructor' in item and any(i_type in st for st in ['constructor', 'namespace']):

				
				c_name = item['parent_constructor']
				key = '.'.join([c_name, i_name])

				print key

				# add
				constructors = DictHelper.addKeyToDict(key, dict(), constructors)

				# set up info
				key_info = '.'.join([key, '__info__'])
				constructors = DictHelper.addKeyToDict(key_info, item, constructors)

			else:

				tmp_arr_2.append(item)

	tmp_arr_other = []
	# go through all the rest that has dependencies
	for i, item in enumerate(tmp_arr_2):

		if 'name' in item:

			i_name = item['name']
			i_type = item['type']

			if 'parent_constructor' in item:
				
				c_name = item['parent_constructor']
				key = '.'.join([c_name, i_name])

				c_name = item['parent_constructor']
				key = '.'.join([c_name, i_name])

				# add
				constructors = DictHelper.addKeyToDict(key, item, constructors)

			else:

				tmp_arr_other.append(item)

	# build dict to pass
	obj = {}

	# store overview
	if overview:
		obj['overview'] = overview

	# store constructors
	obj['constructors'] = constructors

	# store others
	if len(tmp_arr_other) > 0:
		obj['others'] = tmp_arr_other



	return obj
	'''
	print constructors
	exit()
	# new array
	new_arr = []

	for i in constructors:
		new_arr.append(constructors[i])

	# remaining
	for i, item in enumerate(remain_arr):
		new_arr.append(item)
	
	return new_arr
	'''

# outputDoc
# Set output
# 
# @param {Object} config Config info
# @param {List} str Result list
def _outputDoc(config, data):

	output_type = config['output_type'].lower()
	folder_path = config['save_path']

	is_file_path = 0

	# check if save_path is already a file path
	sp = folder_path.split(path_sep)
	if len(sp[-1]) > 0 and len((sp[-1]).split('.')) > 1:
			
		file_name = sp[-1]
		folder_path = path_sep.join(sp[:-1]) + path_sep

		is_file_path = 1

	else:

		file_name = config['file_name'] if 'file_name' in config else 'feed'

		if len(file_name.split('.')) > 1:
			is_file_path = 1

	# make sure save_path has a trailing slash
	if folder_path[-1] != path_sep:
		folder_path = folder_path + path_sep
	
	headers = {}

	# build save path
	save_path = folder_path + file_name

	# remove multiple slashes
	sp = []
	for i, s in enumerate(save_path.split(path_sep)):
		if i == 0:
			sp.append(s)
		elif len(s.strip()) > 0:
			sp.append(s)

	# if not a relative path,
	save_path = '/'.join(sp)

	# json output
	if output_type == 'json':
		data_output = json.dumps(data)

		if not is_file_path:
			save_path = save_path + '.json'

		print 'Saving file: ' + save_path
		FileHelper.writeFile(data_output, save_path)

	elif output_type == 'html':

		print 'Saving HTML Files...'
		HTMLBuilder.generate(data, folder_path)

	else:

		print 'Output type not supported: ' + output_type



# logger
def _log(str):
	global log_arr
	log_arr.append(str)


# CLASS
class JSDoc_Constructor:


	# Initialze
	def __init__(self, config):

		self.__CONFIG = config
		self.__setParser()


	# Parser
	def __setParser(self):

		config = self.__CONFIG
		path = config['source_path']

		#get files
		files = FileHelper.getFilePaths(path, 'js')
		
		if len(files) > 0:

			file_str_arr = []
			for i, f in enumerate(files):
				parsed = self.__setParserFile(f)

				if parsed:
					file_str_arr.append(parsed)

			# type of output
			_outputDoc(config, file_str_arr)

		else:

			print 'No Javascript files to parse...'
			exit()



	# Parser File
	def __setParserFile(self, file_path):

		obj = 0
		file_str = FileHelper.getFileStr(file_path)
		file_name = file_path.split(path_sep)[-1]
		file_folder_path = path_sep.join(file_path.split(path_sep)[:-1])

		# ident
		md5 = hashlib.md5()
		md5.update(file_path)
		file_id = md5.hexdigest()

		# get doc comments
		comments = _getComments(file_str)
		comments_arr = []

		for i, comment_str in enumerate(comments):
			docu = _parseComment(comment_str, file_id)

			if docu:
				comments_arr.append(docu)

		if len(comments_arr) > 0:

			comments_arr = _groupContstructors(comments_arr)

			obj = {
				'id': file_id,
				'docu': comments_arr,
				'file_name': file_name,
				'file_path': file_folder_path
			}
			
		return obj


# EOF JSDoc_Constructor
