import sys, re

# buildMultiLevel
# Build a multi level dictionary using an array of sting in dot notation
# 
# @param {list} arr Array of strings
# 
# @return {dict}
def buildMultiLevel(arr):

	d = {}
	temp = {}

	for z, item in enumerate(arr):

		sp = item.split('.')

		for i, level in enumerate(sp):

			if i == 0 and not level in d:

				d[level] = {}

			elif i > 0:

				if sp[i-1] in d:

					temp = d[sp[i-1]]

					if not level in temp:
						temp[level] = {}

					temp = temp[level]

	return d


# inDict
# Find the key
# 
# @param {string} key Key in string dot notation
# @param {dict} dict_obj the dict you want to put it in
# 
# @return {boolean}
def inDict(key, dict_obj):

	temp = 0
	sp = key.split('.')

	for i, level in enumerate(sp):

		if i == 0:

			if level in dict_obj:

				temp = dict_obj[level]

			else:
				temp = 0
				break

		elif i > 0:
			
			if level in temp:

				temp = temp[level]

			else:

				temp = 0
				break

	
	if type(temp) is dict:
		ret = 1
	elif bool(temp) == True:
		ret = 1
	else:
		ret = 0

	return ret

# addKeyToDict
# Add a key dict 
# 
# @param {string} key The key attribute to define
# @param {data} val Any val you want it to instantiate to
# @param {dict} dict_obj the dictionary to update
# 
# @return {dict} The updated dictionary
def addKeyToDict(key, val, dict_obj):

	temp = 0
	sp = key.split('.')

	target_key = sp[-1]
	
	for i, level in enumerate(sp):

		if i == 0:

			if level in dict_obj:

				temp = dict_obj[level]

			else:
				temp = 0
				break

		elif i > 0:

			if level in temp:

				temp = temp[level]

			elif level != target_key:

				temp = 0
				break
	
	if not isinstance(temp, int):

		temp[target_key] = val

	return dict_obj


