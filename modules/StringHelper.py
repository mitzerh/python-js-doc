import os, re, sys, getopt

# fullStrip
# Strip all mutil character white spaces
# 
# @param {String} str String
# 
# @return {String}
def fullStrip(str, newlines_only = None):
	sp = []

	if newlines_only:
		str = str.strip(' \n\r')
	else:
		str = str.strip(' \t\n\r')
		
	for i, s in enumerate(str.split(' ')):
		if len(s) > 0:
			sp.append(s)

	return ' '.join(sp)


# newLineToMarkup
# Replace new lines with <br />
# 
# @param {string} str String
# 
# @return {string}
def newLineToMarkup(str, n = 1):

	br = '<br />'
	br_arr = []

	for i in range(n):
		br_arr.append(br)

	br = ''.join(br_arr)

	return br.join(str.split('\n'))
	

# newLineToPara
# Replace new lines with <p> tags
# 
# @param {string} str String
# 
# @return {string}
def newLineToPara(str):

	str_arr = str.split('\n')

	for i, st in enumerate(str_arr):

		str_arr[i] = '<p>' + st.strip() + '</p>'

	return ''.join(str_arr)