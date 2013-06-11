import os, re, sys
import FileHelper, StringHelper
from string import Template

html_doc_path = './doc/html/'
html_doc_folder = 'docs/'
path_sep = os.path.sep

asset_files = {}

# remember, for css/js -- order matters!
asset_files['css'] = [
	'jsdocs-reset.css',
	'jsdocs-base.css'
]

asset_files['js'] = [
	'http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
	'jsdocs.js'
]

# generate
# Generate HTML
# 
# @param {list} data
# @param {string} folder_path
def generate(data, folder_path):
	global html_doc_path
	global html_doc_folder

	# check if folder path is the same as the jsdoc html path
	if not os.path.isdir(folder_path):
		os.makedirs(folder_path)

	if not os.path.samefile(html_doc_path, folder_path):

		pages = []
		
		# set up the pages
		for i, item in enumerate(data):
			file_name = '.'.join(item['file_name'].split('.')[:-1])
			pages.append({ 'html':_buildPage(item, folder_path), 'file':file_name })

		# if there are pages
		if len(pages) > 0:

			html_folder_path = folder_path + html_doc_folder
			if not os.path.isdir(html_folder_path):
				os.makedirs(html_folder_path)
				print '[HTMLBuilder] Created html base folder: ' + html_folder_path

			# copy asset
			_copyAssets(folder_path)

			# save the pages
			for i, page in enumerate(pages):
				save_path = html_folder_path + page['file'] + '.html'
				print 'Saving ' + save_path
				FileHelper.writeFile(page['html'], save_path)

			# create the index file
			_createIndexFile(folder_path)
		
		else:

			print '[HTMLBuilder] No pages to build...'

	else:

		print '[HTMLBuilder] Cannot generate HTML. Same path error.'
		

# createIndexFile
# Build the index file
# 
# @param {string} folder_path
def _createIndexFile(folder_path):
	global html_doc_folder
	
	doc_path = folder_path + html_doc_folder
	file_list = FileHelper._getFileLists(doc_path, 'html', 0)	
	save_path = folder_path + 'index.html'
	
	
	wrapper = [

		'<!DOCTYPE html5>',
		'<html>',
		'<head>',
		'$styles',
		'$scripts',
		'</head>',
		'<body id="index">',
		'<header><h1>Index</h1></header>',
		'<div id="content">',
		'	<div class="main">$content</div>',
		'</div>',
		'</body>',
		'</html>'

	]
	wrapper = '\n'.join(wrapper)

	list_templ = [

		'<li>'
		'	<h3><a href="$href">$name</a></h3>'
		'</li>'

	]
	list_templ = '\n'.join(list_templ)

	# docs
	docs = []

	t = Template(list_templ)
	for i, fl in enumerate(file_list):

		rp = {}
		rp['href'] = html_doc_folder + fl
		rp['name'] = '.'.join(fl.split('.')[:-1])
		docs.append(t.safe_substitute(rp))

	if len(docs) > 0:
		docs = '<ul>' + ''.join(docs) + '</ul>'
	else:
		docs = '<ul><li>No files.</li></ul>'

	d = {}
	# css styles
	d['styles'] = _setStyles(folder_path)
	# js files
	d['scripts'] = _setScripts(folder_path)
	d['content'] = docs

	t = Template(wrapper)
	print 'Saving Index file...'
	print 'Saving ' + save_path
	FileHelper.writeFile(t.safe_substitute(d), save_path)

		
# buildPage
# Build the page
# 
# @param {list} item Comment list
# 
# @return {string} markup string
def _buildPage(item, folder_path):

	wrapper = [

		'<!DOCTYPE html5>',
		'<html>',
		'<head>',
		'$styles',
		'$scripts',
		'</head>',
		'<body>',
		'<header>',
		'	$headline',
		'	<div class="to-index"><a href="$indexlink">[Back to index]</a></div>'
		'</header>',
		'<div id="content">',
		'	<div class="rail">$rail</div>',
		'	<div class="main">$content</div>',
		'</div>',
		'<footer>',
		'	<div class="to-top"><a href="#top">[back to top]</a></div>',
		'</footer>',
		'</body>',
		'</html>'

	] 	
	wrapper = '\n'.join(wrapper)
	
	d = {}
	# index file link
	d['indexlink'] = '..' + path_sep + 'index.html'
	# css styles
	d['styles'] = _setStyles(folder_path)
	# js files
	d['scripts'] = _setScripts(folder_path)
	# headline
	d['headline'] = _setHeadline(item)

	# constructor markup
	const_markup = _setConstructors(item)
	d['rail'] = const_markup['rail']
	d['content'] = const_markup['desc']

	t = Template(wrapper)
	markup = t.safe_substitute(d)

	return markup


# copyAssets
# Set up the assets
# 
# @param {string} folder_path
def _copyAssets(folder_path):
	global html_doc_path
	global asset_files

	print '[HTMLBuilder] Copying assets...'

	# copy assets
	for i in asset_files:

		src_folder = html_doc_path + i + path_sep
		dest_folder = folder_path + i + path_sep

		# if folder doesn't exist, create it
		if not os.path.exists(dest_folder):
			os.makedirs(dest_folder)
			print '[HTMLBuilder] Created asset folder: ' + dest_folder

		# copy files to target folder
		for z, st in enumerate(asset_files[i]):
			src = src_folder + st
			FileHelper.copyFile(src, dest_folder)
	
	# copy images
	src_folder = html_doc_path + 'img' + path_sep
	dest_folder = folder_path + 'img' + path_sep

	# if folder doesn't exist, create it
	if not os.path.exists(dest_folder):
		os.makedirs(dest_folder)
		print '[HTMLBuilder] Created asset folder: ' + dest_folder

	FileHelper.copyDir(src_folder, dest_folder)


# setStyles
# Generate the styles
# 
# @return {string}
def _setStyles(folder_path):
	global asset_files
	
	templ = '<link rel="stylesheet" href="$href" type="text/css" />'
	temp_arr = []

	for i, s in enumerate(asset_files['css']):

		t = Template(templ)
		temp_arr.append(t.safe_substitute({ 'href':'..' + path_sep + 'css' + path_sep + s }))

	return '\n'.join(temp_arr)


# setScripts
# Generate the javascripts
# 
# @return {string}
def _setScripts(folder_path):
	global asset_files
	
	templ = '<script src="$src"></script>'
	temp_arr = []

	for i, s in enumerate(asset_files['js']):
		t = Template(templ)

		if re.match(r'^http', s, re.IGNORECASE):
			src = s
		else:
			src = '..' + path_sep + 'js' + path_sep + s

		temp_arr.append(t.safe_substitute({ 'src':src }))
	
	return '\n'.join(temp_arr)


# setHeadline
# Generate the headline markup
# 
# @param {list} item Comment list
def _setHeadline(item):

	str = [

		'<h1>$title</h1>',
		'<p class="desc">$desc</p>'

	]
	str = '\n'.join(str)
	

	doc = item['docu']
	file_name = item['file_name']

	overview = doc['overview'] if 'overview' in doc else 0

	d = {}
	# title
	d['title'] = overview['name'] if overview and 'name' in overview else file_name
	# description
	d['desc'] = StringHelper.newLineToMarkup(overview['desc']) if overview and 'desc' in overview else 'No Description. hint: describe using @fileOverview'

	t = Template(str)
	return t.safe_substitute(d)


# generateConstructorRail
# Generates the navigation for the constructors
# 
# @param {dict} item Consructor item
def __generateConstructorRail(item):

	temp_arr = []

	if len(item.keys()) > 0:
		
		has_const = 0

		# if this is a constructor
		if '__info__' in item:
			info = item['__info__']

			temp_arr.append('<li data-id="r-' + info['id'] + '" class="constructor"><a href="#anc-' + info['id'] + '">' + info['name'] + '</a>\n')

			temp_arr.append('<ul>')

			for i in item:
				if i != '__info__':
					temp_arr.append(__generateConstructorRail(item[i]))

			temp_arr.append('</ul>')
			temp_arr.append('</li>')

		else:

			display_str = item['name']

			if item['type'] == 'function':
				display_str = display_str + '()'

			temp_arr.append('<li data-id="r-' + item['id'] + '"><a href="#anc-' + item['id'] + '">' + display_str + '</a></li>\n')				

	return ''.join(temp_arr)


# generateParams
# Generates the parameter information
# 
# @parma {list} params
def __generateParams(params, code = '@param'):

	templ = [

		'	</tr><tr>',
		'		<td><pre><code>$code</code></pre></td>',
		'		<td><pre><code>$name</code></pre></td>',
		'		<td>$type</td>',
		'		<td>$desc</td>',
		'		$sub_params'
		
	]
	templ = '\n'.join(templ)

	temp_arr = []

	for i, pr in enumerate(params):
		
		if pr['code'] == code:

			d = {}
			d['code'] = pr['code']
			d['name'] = pr['name'] if len(pr['name']) > 0 else '&nbsp;'
			d['type'] = pr['type']
			d['desc'] = StringHelper.newLineToMarkup(pr['desc'])

			if 'sub_params' in pr:
				d['hide'] = ''
				d['sub_params'] = __generateParams(pr['sub_params'])

			else:
				d['sub_params'] = ''

			t = Template(templ)
			temp_arr.append(t.safe_substitute(d))

	return ''.join(temp_arr)


# formatTypeName
# Format the constructor/function name in full path
# 
# @param {dict} item Constructor item
# 
# @return {string}
def __formatTypeName(item):
	c_str = item['parent_constructor'] if 'parent_constructor' in item else 0

	ret = []
	if c_str:
		ret.append('<span class="name-const">'+c_str+'</span>')
	
	ret.append(item['name'])

	return '.'.join(ret)

# generateConstructorDesc
# Generates the description for the constructor items
# 
# @param {dict} item Constructor item
def __generateConstructorDesc(item):

	const_templ = [

		'<article class="desc $maincss" data-id="desc-$id">',
		'	<a name="anc-$id"></a>',
		'	<h3>$name</h3>',
		'	<div class="summary">$desc</div>',
		'	$params',
		'	$examples',
		'</article>'

	]
	const_templ = '\n'.join(const_templ)

	fn_templ = [

		'<article class="fn" data-id="fn-$id">',
		'	<a name="anc-$id"></a>',
		'	<h3>$name</h3>',
		'	<div class="summary">$desc</div>',
		'	$params',
		'	$returns',
		'	$examples',
		'</article>'

	]
	fn_templ = '\n'.join(fn_templ)

	pr_templ = [
		
		'	<div class="params $code">',
		'		<h4>$code</h4>',
		'		<table border="2">',
		'		<thead>',
		'			<tr>',
		'				<td>code</td>',
		'				<td>name</td>',
		'				<td>type</td>',
		'				<td class="desc">description</td>',
		'			</tr>',
		'		</thead>',
		'		<tbody><tr class="first"><td colspan="4">&nbsp;</td>$prm</tr></tbody>',
		'		</table>'
		'	</div>'

	]
	pr_templ = '\n'.join(pr_templ)

	temp_arr = []

	if len(item.keys()) > 0:
		
		has_const = 0

		# if this is a constructor
		if '__info__' in item:
			info = item['__info__']

			d = {}
			d['id'] = info['id']
			
			c_name = __formatTypeName(info)
			d['name'] = '<span>' + info['type'] + ' :: </span>' + c_name

			# write the params
			if 'params' in info and len(info['params']) > 0:
				param_arr = []
				for z, prm in enumerate(info['params']):
					if (len(prm['name']) > 0 and prm['code'] == '@param'):
						param_arr.append(prm['name'])

				d['name'] += ' <em>(' + ', '.join(param_arr) + ')</em>'

			
			# if private scope, add to name
			if 'scope' in info and info['scope']:
				d['name'] += ' <span class="scope">['+ info['scope'] +']</span>'

			d['desc'] = StringHelper.newLineToMarkup(info['desc']) if 'desc' in info and info['desc'] else 'No Description.'
			d['maincss'] = 'c-main' if 'parent_constructor' not in info else ''

			# examples
			if 'ex' in info and info['ex']:
				print 'samples!!'
				d['examples'] = '<div class="ex"><h4>Example code:</h4><pre><code>' + StringHelper.newLineToMarkup(info['ex']) + '</code></pre></div>'
			else:
				d['examples'] = ''

			# params
			d['params'] = ''
			d['returns'] = ''
			if 'params' in info and len(info['params']) > 0:
				pr = Template(pr_templ)
				c_params = __generateParams(info['params'])
				r_params = __generateParams(info['params'], '@return')

				if len(c_params) > 0:
					d['params'] = pr.safe_substitute({ 'prm': c_params, 'code':'parameters' })					

				if len(r_params) > 0:
					d['returns'] = pr.safe_substitute({ 'prm': r_params, 'code':'returns' })	
				

			t = Template(const_templ)
			temp_arr.append(t.safe_substitute(d))

			for i in item:
				if i != '__info__' and 'parent_constructor' not in item[i]:
					temp_arr.append(__generateConstructorDesc(item[i]))

		if 'name' in item and 'type' in item:

			d = {}
			d['id'] = item['id']

			c_name = __formatTypeName(item)
			d['name'] = '<span>' + item['type'] + '</span> :: ' + c_name

			# write the params
			if 'params' in item and len(item['params']) > 0:
				param_arr = []
				for z, prm in enumerate(item['params']):
					if (len(prm['name']) > 0 and prm['code'] == '@param'):
						param_arr.append(prm['name'])

				d['name'] += ' <em>(' + ', '.join(param_arr) + ')</em>'

			# if private scope, add to name
			if 'scope' in item and item['scope']:
				d['name'] += ' <span class="scope">['+ item['scope'] +']</span>'

			d['desc'] = StringHelper.newLineToMarkup(item['desc']) if 'desc' in item and item['desc'] else 'No Description.'

			# examples
			if 'ex' in item and item['ex']:
				d['examples'] = '<div class="ex"><h4>Example code:</h4><pre><code>' + StringHelper.newLineToMarkup(item['ex']) + '</code></pre></div>'
			else:
				d['examples'] = ''

			# params
			d['params'] = ''
			d['returns'] = ''
			if 'params' in item and len(item['params']) > 0:
				pr = Template(pr_templ)
				c_params = __generateParams(item['params'])
				r_params = __generateParams(item['params'], '@return')

				if len(c_params) > 0:
					d['params'] = pr.safe_substitute({ 'prm': c_params, 'code':'parameters' })					

				if len(r_params) > 0:
					d['returns'] = pr.safe_substitute({ 'prm': r_params, 'code':'returns' })
			
			t = Template(fn_templ)
			temp_arr.append(t.safe_substitute(d))

		else:

			for i in item:
				c_item = item[i]
				if i != '__info__' and 'parent_constructor' in c_item and c_item['type'] == 'function':

					d = {}
					d['id'] = c_item['id']

					c_name = __formatTypeName(c_item)
					d['name'] = '<span>' + c_item['type'] + '</span> :: ' + c_name

					# write the params
					if 'params' in c_item and len(c_item['params']) > 0:
						param_arr = []
						for z, prm in enumerate(c_item['params']):
							if (len(prm['name']) > 0 and prm['code'] == '@param'):
								param_arr.append(prm['name'])

						d['name'] += ' <em>(' + ', '.join(param_arr) + ')</em>'

					# if private scope, add to name
					if 'scope' in c_item and c_item['scope']:
						d['name'] += ' <span class="scope">['+ c_item['scope'] +']</span>'

					d['desc'] = StringHelper.newLineToMarkup(c_item['desc']) if 'desc' in c_item and c_item['desc'] else 'No Description.'

					# examples
					if 'ex' in c_item and c_item['ex']:
						d['examples'] = '<div class="ex"><h4>Example code:</h4><pre><code>' + StringHelper.newLineToMarkup(c_item['ex']) + '</code></pre></div>'
					else:
						d['examples'] = ''

					# params
					d['params'] = ''
					d['returns'] = ''
					if 'params' in c_item and len(c_item['params']) > 0:
						pr = Template(pr_templ)
						c_params = __generateParams(c_item['params'])
						r_params = __generateParams(c_item['params'], '@return')

						if len(c_params) > 0:
							d['params'] = pr.safe_substitute({ 'prm': c_params, 'code':'parameters' })					

						if len(r_params) > 0:
							d['returns'] = pr.safe_substitute({ 'prm': r_params, 'code':'returns' })

					t = Template(fn_templ)
					temp_arr.append(t.safe_substitute(d))

	return ''.join(temp_arr)

# setConstructors
# Generate the constructor markup
# 
# @param {list} item Comment list
def _setConstructors(item):

	rail_wrapper = [

		'<section class="$type">',
		'	$info',
		'	<ul class="tree">$rlist</ul>',
		'</section>'

	]
	rail_wrapper = '\n'.join(rail_wrapper)

	desc_wrapper = [

		'<section class="$type c-desc">',
		'	$dlist',
		'</section>'

	]
	desc_wrapper = '\n'.join(desc_wrapper)

	doc = item['docu']
	constructors = doc['constructors'] if 'constructors' in doc else 0
	others = doc['others'] if 'others' in doc else 0

	rail_str = []
	desc_str = []
	
	#constructors
	levels = []
	desc = []

	if constructors:
		for i in constructors:
			levels.append(__generateConstructorRail(constructors[i]))
			desc.append(__generateConstructorDesc(constructors[i]))
	
		d = {}
		d['type'] = 'constructors'
		d['info'] = '<h4>Constructors</h4>'
		d['rlist'] = ''.join(levels) if len(levels) > 0 else ''
		d['dlist'] = ''.join(desc) if len(desc) > 0 else ''
		rt = Template(rail_wrapper)
		dt = Template(desc_wrapper)

		rail_str.append(rt.safe_substitute(d))
		desc_str.append(dt.safe_substitute(d))


	# others
	levels = []
	desc = []
	if others:
		for i, itm in enumerate(others):
			levels.append(__generateConstructorRail(itm))
			desc.append(__generateConstructorDesc(itm))

	if len(levels) > 0:

		d = {}
		d['type'] = 'others'
		d['info'] = '<h4>Others</h4>'
		d['rlist'] = ''.join(levels)
		d['dlist'] = ''.join(desc)
		rt = Template(rail_wrapper)
		dt = Template(desc_wrapper)

		rail_str.append(rt.safe_substitute(d))
		desc_str.append(dt.safe_substitute(d))

	obj = {}

	# rail
	obj['rail'] = '\n'.join(rail_str)
	# desc
	obj['desc'] = '\n'.join(desc_str)

	return obj
