python-js-doc
=============

Javascript documentation which strictly uses comment tagging only
&nbsp;

JSDoc.py Documentation
======================
Supports most of the key JS Doc tags. 

See: [JS Doc Tag Reference](https://code.google.com/p/jsdoc-toolkit/wiki/TagReference)


Those supported are listed out below.

##### Note:
As with the in-house nature of the scope of this parser, this does not function like the other proprietary JS Doc parser. 
This parser will not go through your code and translate it for you. 
It will all depend on the accuracy of your documentation comment blocks.

Although it follows most of the key JS Doc tags to the tee, 
there are some variations in order to adapt to our in-house coding styles.

The file output for the parsed documentation is currenlty
only available in **JSON**, and **HTML** format.

**Example executions:**
	
*With default config in the file*

	python parse.py


*With arguments*

	# use a different config (in config.ini)
	python parse.py --config=default
	
	# overrides - DEPRECATED. All custom variables should now be set up in the config.ini file
	python parse.py --path=/path/to/files --dest=/path/to/save/file.json --output=json

&nbsp;

---

Requirement
------------
Only multi-line comment blocks declared as a **@fileOverview**, **@constructor**, **@object**, **@name**, or a **@namespace** will be parsed. It should also be the first tag declaration within the comment block.
So only the important parts of a script. All others will be ignored. A need for applying more will be added as necessary.

For example, this will be parsed:

	/**
	 * @constructor MyConstructor
	 * @public
	 * @description My Construtor is public!
	 *
	 */

This will not:

	/**
	 * @public
	 * @description This should be my constructor
	 */

Or this:

	/**
	 * @public
	 * @constructor MyConstructor
	 * @description Looks like I need my @constructor declaration first
	 */

Definitely not this non-multiline format:
	
	// @constructor MyConstructor
	// @public
	// @description I think this will not work...

&nbsp;

---

Supports:
---------

**@fileOverview** - information regarding the javascript file

	@fileOverview
	
	/**
	 * @fileOverview
	 * @description
	 * This file is about...
	 */

**@constructor** - define a constructor

	@constructor [constructor_name] [description]
	
	/**
	* @constructor MyConstructor A sample constructor
	*/

**@description**

	@description [your description - can be multi-line]
	
	/**
	 * @description my description
	 */
	
	/**
	 * @description
	 * My description in
	 * multiple lines
	 * over here
	 */

**@example** - example code, will be put in a &lt;code&gt; block
	
	@example [your example]
	
	/**
	 * @example myfunction.load()
	 */
	
	/**
	 * @example
	 * An option:
	 * myfunction.load()
	 * Another option could be..
	 * myfunction.reload()
	 */

**@object** - Also treated as a constructor

	@object [object_name] [description]
	
	/**
	* @object MySampleObject A sample object
	*/	


**@name** - DEPRECATED. Use **@fileOverview** instead

	@name [name_of_the_js_file] [description]
	
	/**
	 * @name jQuery jQuery here
	 */


**@namespace**

	@namespace [property_namespace] [description]
	
	/**
	 * @namespace some_property property of something
	 */


**@function**

	@function [function_name] [description]
	
	/**
	 * @function MyFunction My Function
	 */

**@memberOf** - dependency of the function/constructor/object
	
	@memberOf [Constructor_Or_Object]
	
	/**
	 * @function MyFunction My Function
	 * @memberOf SomeConstructorOrObject
	 */

**@requires** - note what are needed to run the code

	@requires [whatever or (@constructor or @name)]
	
	/**
	 * @requires JQuery
	 * @requires Some other Foo Bar
	 */


*TODO:*

Linking to a @constructor:

	/**
	 * @requires @constructor MyConstructor
	 */

Linking to a JS File:

	/**
	 * @requires @name jQuery
	 */


**@param**

	@param {[type]} [variable_name] [description]
	
	/**
	 * @param {String} my_string A string is born
	 */

	/**
	 * @param {Object} an_object An Object with parameters
	 * @param {Object} an_object.param1 Param 1
	 * @param {Object} an_object.param2 Param 2
	 */
	 
	/**
	 * @param {String|Array} pass_var A var that may be String or Array
	 */


**@returns**

	@returns {[type]} [description]
	
	/**
	 * @erturns {String} A String
	 */
	 
	/**
	 * @returns {String|Boolean} A string or boolean value
	 */


**@version**

	@version [version info]
	
	/**
	 * @version release 1.1.2
	 */


**@private**

	@private
	
	/**
	 * @function MyFunction My Function
	 * @private
	 */


**@public**

	@public
	
	/**
	 * @function MyFunction My Function
	 * @public
	 */

&nbsp;

---

Dev Notes/Recommendations
------------------------

- Sublime has a pretty robust js doc comment generator plugin. Initial development of this parser was tested using Sublime 2 Text editor, with the plugin.
- Python v2.6.1
- Run on \*NIX only. Sorry Windows no love for you. (needs to run os.path.* that are UNIX only)


