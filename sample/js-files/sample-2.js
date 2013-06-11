/**
 * @constructor MultiFeedParser
 * @public
 * @requires jQuery
 * @requires A whole lotta understanding
 *
 * @param {object} config Configuration file
 * @param {object} config.feeds - (required) Feed Information
 * @param {boolean} config.logging - (optional) enable/disable console logging (default is false)
 * @param {boolean} config.initOnLoad - (optional) when enabled, it will load the feeds on initialization; when disabled, you will have to call event.reload() to initiate (default is true)
 * @param {integer} config.cacheTime - (optional) define the browser cache buster in minutes (default is nothing)
 * 
 */
window.MultiFeedParser = (function($){
	
	var CONST = {
		logName: "[Feed Parser]",
		jsonpParam: "callback",
		minRefreshRate: 0.50 // minimum refresh rate - 0.5 mins === 30 seconds
	};
	
	var App = function(config) {
		
		config = config || {}; // empty object
		
		var self = this;
		self.__vars = {};
		
		var v = self.__vars;
		
		// set up variables
		v._config = config; // user initial config
		v._fn = {}; // function holder
		v._data = {}; // data holder
		v._xhr = {}; // xhr requests holder
		v._callStack = {}; // function call stack for types
		v._initExe = {}; // feed initial execution boolean for types
		v._refreshObj = {};
		
		// add public calls
		
		/**
		 * @namespace event
		 * @memberOf MultiFeedParser
		 *
		 * @description
		 * Uses the Events constructor (see the constructor for details)
		 * 
		 */
		self.event = new Events(self);
		
		// logging?
		v._fn.log = (v._config.logging) ? log : function(){};
		
		// initialize - 
		var initOnLoad = (typeof v._config.initOnLoad === "boolean" && !v._config.initOnLoad) ? false : true; // by default, true if not defined
		
		var i, feeds = (v._config && v._config.feeds) ? v._config.feeds : false;
		
		if (initOnLoad && feeds) {
			for (i in feeds) {
				loadFeed(v,i);
				
				// set up refresh rates
				if (feeds[i].refresh) {
					setRefreshRate(self,i,feeds[i]);
				}
				
			}
		}
		
	};
	
	/**
	 * @constructor Events
	 * @private
	 * 
	 * @description 
	 * All the accessible public event methods
	 * 
	 */
	var Events = (function(){
		
		var Event = function(root) {
			this.__vars = {};
			var v = this.__vars;
			v.root = root;
		};
		
		/**
		 * @function reload 
		 * @memberOf Events
		 *
		 * @description
		 * Reloads the feed types 
		 * 
		 * @example
		 * event.reload();
		 * event.reload("feed1");
		 * event.reload("feed1 feed2");
		 * 
		 * @param {String} types (optional) feed type name/s; if defined, it will only load the specific ones; if undefined it will reload all types 
		 * 
		 */
		Event.prototype.reload = function(types) {
			var i, x, hasLoad = false, self = this, root = self.__vars.root, v = root.__vars, feeds = (v._config && v._config.feeds) ? v._config.feeds : false, arr = [];
			
			if (!feeds) { return false; }
			
			// check if there is a refresh already set
			var setRefresh = function(type) {
				if (!v._refreshObj[type]) {
					setRefreshRate(root,type,feeds[type]);
				}
			};
			
			// types
			if (typeof types === "string") {
				types = (trimStr(types)).replace(/\s+/g," "); 
				arr = types.split(" ");
			}
			
			if (arr.length > 0) { // types
				for (x = 0; x < arr.length; x++) {
					if (feeds[arr[x]]) { 
						v._fn.log(CONST.logName + " Reloading {type}: '" + arr[x] + "'");
						loadFeed(v,arr[x]);
						setRefresh(arr[x]);
						hasLoad = true;
					}
				}
			} else { // no types passed, reload all feeds
				v._fn.log(CONST.logName + " Reloading all feed {type}");
				for (i in feeds) {
					loadFeed(v,i);
					setRefresh(i);
				}
				hasLoad = true;
			}
			
		};
		
		/**
		 * @function addFeed
		 * @memberOf Events
		 *
		 * @description
		 * Adds a feed after initialization of the script
		 *
		 * @example
		 * Argument options:
		 * 
		 * 1. Simple (using two {string} arguments)
		 * event.addFeed("feed1","http://foo.bar.com");
		 * &nbsp;
		 * 2. Advanced (using an {object} argument)
		 * event.addFeed({ type:"feed1", url:"http://foo.bar.com", refresh:60 });
		 *
		 * @param {string} argument[0] feed type name
		 * @param {string} argument[1] url of the feed
		 *
		 */
		Event.prototype.addFeed = function() {
			var self = this, root = self.__vars.root, v = root.__vars, feeds = (v._config && v._config.feeds) ? v._config.feeds : {}, args = arguments;
			
			var config = { type:false, url:false };
			
			if (typeof args[0] === "string" && typeof args[1] === "string") {
				config.type = args[0];
				config.url = args[1];
			} else if (typeof args[0] === "object" && args[0].type && args[0].url) {
				config = args[0];
			}
			
			if (!config.type || !config.url) { // check if no type
				v._fn.log(CONST.logName + " Cannot fire event.addFeed(). Missing config {type} or {url}.");
				return false; 
			} else if (feeds[config.type]) { // check if type already exists
				v._fn.log(CONST.logName + " Cannot fire event.addFeed() for {type}: '" + config.type + "'. This type already exists.");
				return false;
			}
			
			// store
			var i, cfg = {};
			for (i in config) {
				if (i !== "type") { cfg[i] = config[i]; }
			}
			
			root.__vars._config.feeds[config.type] = cfg;
			loadFeed(v,config.type);
			
			// set up refresh rates
			if (config.refresh) {
				setRefreshRate(root,config.type,cfg);
			}
		};
		
		/**
		 * @function removeFeed
		 * @memberOf Events
		 *
		 * @description
		 * Remove a feed and all its instances and dependencies
		 * 
		 * @example
		 * event.removeFeed("feed1");
		 * event.removeFeed("feed1 feed2 feed3");
		 *
		 * @param {string} type Type id of the feed; you can remove multiple feeds by splitting with spaces
		 * 
		 */
		Event.prototype.removeFeed = function(type) {
			var self = this, root = self.__vars.root, v = root.__vars, hasFeeds = (root.__vars._config && root.__vars._config.feeds) ? true : false;
			
			if (!hasFeeds || typeof type !== "string") { return false; }
			
			var removeType = function(val) {
				if (!root.__vars._config.feeds[val]) { return false; }
				
				// nullify
				root.__vars._config.feeds[val] = null;
				root.__vars._initExe[val] = null;
				root.__vars._callStack[val] = null;
				root.__vars._refreshObj[val] = null;
				
				// attempt to delete
				try {
					delete root.__vars._config.feeds[val];
					delete root.__vars._initExe[val];
					delete root.__vars._callStack[val];
					delete root.__vars._refreshObj[val];
				} catch(err) {
					// do nothing
				}
				
				v._fn.log(CONST.logName + " Notice: Feed removed for {type}: '" + val + "'");
			};
			
			// if multiples
			type = (trimStr(type)).replace(/\s+/g," "); 
			var arr = [], sp = type.split(" ");
			
		};
		
		/**
		 * @function onLoad
		 * @memberOf Events
		 * 
		 * @description
		 * Bind a function to the onload event of a type
		 * Different from event.getData() - this will trigger on event.reload();
		 *
		 * @example
		 * Argument options:
		 * 1. Simple:
		 * event.onLoad("feed1",function(data) { alert(data); });
		 * &nbsp;
		 * 2. Advanced:
		 * event.onload({ type:"feed1", callback:function(data) { alert(data); });
		 * 
		 * @param {string} args[0] feed type name
		 * @param {function} args[1] callback function to bind
		 * 
		 */
		Event.prototype.onLoad = function() {
			var self = this, root = self.__vars.root, v = root.__vars, feeds = (v._config && v._config.feeds) ? v._config.feeds : {}, args = setLoaderArgs(arguments);
			
			if (!args.type || !args.callback || !feeds[args.type]) { return false; }
			var type = args.type, callback = args.callback;
			
			// stack up callbacks
			if (!v._callStack[type]) { v._callStack[type] = []; }
			v._callStack[type].push(callback);
			
			if (v._initExe[type]) { // if called after initial feed load, run it!
				callback(v._data[type]);
			}
			
		};
		
		/**
		 * @function getData
		 * @memberOf Events
		 *
		 * @description
		 * Bind a function to get the latest type's data. 
		 * Different from event.onLoad() - this will only trigger only when explicitly called
		 *
		 * @example
		 * Argument options:
		 * 1. Simple:
		 * event.getData("feed1",function(data) { alert(data); });
		 * &nbsp;
		 * 2. Advanced:
		 * event.getData({ type:"feed1", callback:function(data) { alert(data); });
		 * 
		 * @param {string} args[0] feed type name
		 * @param {function} args[1] callback function to bind
		 * 
		 */
		Event.prototype.getData = function() {
			var self = this, root = self.__vars.root, v = root.__vars, feeds = (v._config && v._config.feeds) ? v._config.feeds : {}, args = setLoaderArgs(arguments);
			
			if (!args.type || !args.callback) { return false; }
			var type = args.type, callback = args.callback;
			
			// attempt
			var cntr = 0, max = 20, timeoutObj;
			
			var attempt = function() {
				if (typeof v._data[type] !== "undefined") {
					callback(v._data[type]);
				} else if (cntr <= max) {
					clearTimeout(timeoutObj);
					timeoutObj = setTimeout(function(){
						attempt();
					},250);
					cntr++;
				}
			};
			attempt();
		};
		
		return Event;
		
	}());
	
	/*** PRIVATE ***/
	/**
	 * @function setRefreshRate
	 * @private
	 *
	 * @description
	 * Refresh rate helper function
	 * Sets the refresh rate in seconds
	 * 
	 * @param {object} self Prototype of the feed instance
	 * @param {string} type Feed type name
	 * @param {object} info Config information of the type
	 * 
	 */
	var setRefreshRate = function(self,type,info) {
		// check refresh rate
		var refresh = (!isNaN(info.refresh) && parseFloat(info.refresh) >= CONST.minRefreshRate) ? (info.refresh).toFixed(2) : false;
		if (!refresh) { 
			log(CONST.logName + " Warning: Cannot set refresh for {type}: '" + type + "' refresh rate less than minimum rate allowed.");
			return false; 
		}
		
		// refresh in seconds
		refresh = refresh * 60000;
		
		clearInterval(self.__vars._refreshObj[type]);
		self.__vars._refreshObj[type] = setInterval(function(){
			if (self.event && typeof self.event.reload === "function") {
				self.event.reload(type);
			} else {
				log(CONST.logName + " Warning: Cannot find event.reload(). Reload for {type}: '" + type + "' not fired.");
			}
		},refresh);
	};
	
	/**
	 * @function loadFeed
	 * @private
	 *
	 * @description
	 * Feed loader helper
	 * Loads the feed via jQuery.ajax()
	 * 
	 * @param {object} vars Variables of the feed instance
	 * @param {string} type Feed type name
	 * 
	 */
	var loadFeed = function(vars,type) {
		var feeds = vars._config.feeds, info = feeds[type] || false;
		
		// make sure there's information about the type
		if (!info) { return false; }
		
		// get the feed url
		var url = (function(){
			var ret = false;
			
			if (typeof info === "string") {
				ret = info;
			} else if (info.url) {
				ret = info.url;
			}
			
			return ret;
		}());
		
		// make sure there's a url
		if (!url) { log(CONST.logName + " URL not defined for feed {type}: '" + type + "'"); return false; }
		
		// check what data type it is
		var dataType = (function(){
			var ret = "json", jsonpCallback = getJSONP(url);
			
			if (typeof info.jsonpCallback === "string" || jsonpCallback) {
				ret = "jsonp";
			} else if (info.type && inDataType(info.type)) {
				ret = info.type;
			}
			
			ret = ret.toLowerCase();
			return ret;
		}());
		
		// set up configs for $.ajax
		var ajaxConfig = {};
		
		switch (dataType) {
			
			case "json":
				ajaxConfig = {
					dataType: "json",
					cache: true,
					async: true,
					success: function(data) {
						commonSuccessFN(data);
					}
				};
				break;
			
			case "jsonp":
				var urlCallback = getJSONP(url), callback = useJSONPCallback(type, ((typeof info.jsonpCallback === "string") ? info.jsonpCallback : false), urlCallback);
				
				window[callback.name] = function(data) {
					commonSuccessFN(data);
				};
			
				ajaxConfig = {
					dataType: "script",
					async: true,
					cache: true
				};
				
				// jsonp callback
				if (!urlCallback) {
					ajaxConfig.data = {};
					ajaxConfig.data[callback.param] = callback.name;
				}
				
				
				break;
				
			case "xml":
				// TODO:
				break;
				
			case "script":
				// TODO:
				break;
				
			case "text":
				// TODO:
				break;
		}
		
		// url
		ajaxConfig.url = url;
		
		// set up browser cache buster
		(function(){
			var cacheTime = (vars._config.cacheTime && !isNaN(vars._config.cacheTime)) ? parseFloat(vars._config.cacheTime) : false;
			if (cacheTime) {
				if (!ajaxConfig.data) { ajaxConfig.data = {}; }
				ajaxConfig.data["cb"] = cacheBuster(cacheTime);
			}
		}());
		
		
		// try to abort any existing ajax calls
		if (dataType !== "jsonp" && vars._xhr[type]) {
			try {
				if (typeof vars._xhr[type].abort === "function") {
					vars._xhr[type].abort();
				}
			} catch(err) {
				// do nothing
			}
		}
		
		vars._xhr[type] = $.ajax(ajaxConfig);
		
		// INTERNAL PRIVATE FUNCTIONS
		function commonSuccessFN(data) {
			// normalize
			var normFN = getNormalizationFN(info.normalize, feeds), normalized = (normFN) ? normFN(data) : data;
			
			// store
			vars._data[type] = normalized;
			
			if (!vars._initExe[type]) { vars._initExe[type] = true; }
			
			triggerStack(vars._callStack[type],vars._data[type]);
		}
		
	};
	
	/**
	 * @function triggerStack
	 * @private
	 *
	 * @description
	 * Function Stack trigger helper
	 * Runs the stack of functions
	 * 
	 */
	var triggerStack = function(stack,data) {
		if (!isArray(stack)) { return false; }
		for (var x = 0; x < stack.length; x++) {
			if (typeof stack[x] === "function") { stack[x](data); }
		}
	};
	
	/**
	 * @function setLoaderArgs
	 * @private
	 *
	 * @description
	 * Loader Arguments helper
	 * common arguments parser for event.getData and event.onLoad
	 * 
	 */
	var setLoaderArgs = function(args) {
		var type = false, callbackFN = false;
		
		// type
		if (typeof args[0] === "string") {
			type = args[0];
		} else if (typeof args[0] === "object" && !isArray(args[0])) {
			type = (args[0].type) ? args[0].type : false;
		}
		
		// callbackFN
		if (typeof args[1] === "function") {
			callbackFN = args[1];
		}
		
		var obj = { type:type, callback:callbackFN };
		return obj;
		
	};
	
	/**
	 * @function getNormalizationFN
	 * @private
	 * 
	 * @description
	 * Normalization function helper
	 * Checks to see if there is a normalization function to a feed type
	 * 
	 */
	var getNormalizationFN = function(val,feeds) {
		var i, ret = false;
		
		if (typeof val === "function") {
			ret = val;
		} else if (typeof val === "string") {
			
			for (i in feeds) {
				if (val === i && typeof feeds[i].normalize === "function") {
					ret = feeds[i].normalize; break;
				}
			}
			
		}
		
		return ret;
	};
	
	/**
	 * @function useJSONPCallback
	 * @private
	 *
	 * @description
	 * JSONP callback helper
	 * Checks whether to use option1 or option2 callback parameters
	 * 
	 */
	var useJSONPCallback = function(type, opt1,opt2) {
		var ret = { param:"callback" };
		
		if (opt1 && opt1.split("=").length === 2) { // check if the string is a param pair
			var sp = opt1.split("=");
			ret.param = sp[0];
			ret.name = sp[1];
		} else if (opt1) { // if not a param pair, assume the query param is callback
			ret.name = opt1;
		} else if (opt2) {
			ret.name = opt2;
		} else {
			ret.name = "jsonp" + type;
		}
		
		return ret;
	};
	
	/**
	 * @function inDataType
	 * @private
	 * 
	 * @description
	 * Ajax types helper
	 * Checks whether the ajax data type is supported
	 * 
	 */
	var inDataType = function(type) {
		var x, ret = false, types = ["jsonp","json","xml","html","text","script"];
		for (x = 0; x < types.length; x++) {
			if (types[x] === type.toLowerCase()) { ret = true; break; }
		}
	};
	
	/**
	 * @function getJSONP
	 * @private
	 *
	 * @description
	 * JSONP callback helper
	 * Gets the jsonp callback parameter from the url
	 * 
	 */
	var getJSONP = function(url) { // check for default param "callback"
		var x, ret = false, sp = url.split("?"), search = sp[1];
		
		if (search) {
			var arr = ((search.toLowerCase()).indexOf(CONST.jsonpParam + "=") > -1) ? search.split("&") : [];
			for (x = 0; x < arr.length; x++) {
				var pair = arr[x].split("=");
				if (pair[0].toLowerCase() === CONST.jsonpParam) {
					ret = decodeURI(pair[1]); break;
				}
			}
		}
		
		return ret;
	};
	
	// logger
	var log = function() {
		var loggerON = true;
		if (loggerON && window.console) {
			try {
				return console.log.apply(console, arguments);
			} catch(err) {
				console.log(arguments);
			}
		}
	};
	
	// cachebuster
	var cacheBuster = function(freq) {
		freq = freq || false;
		var date = new Date(), str = date.getFullYear().toString() + (date.getMonth()+1).toString() + date.getDate().toString(),
			hr = date.getHours()+1, min = date.getMinutes();
		str += hr.toString() + ((freq && !isNaN(freq)) ? (Math.floor(min/parseFloat(freq))).toString() : "");
		return str;
	};
	
	// array check
	var isArray = function(val) {
		val = val || false;
		return Object.prototype.toString.call(val) === "[object Array]"; 
	};
	
	// right/left trim
	var trimStr = function(val) {
		val = (val || "").replace(/^\s+|\s+$/g,"");
		return val;
	};
	
	return App;
	
}(jQuery));