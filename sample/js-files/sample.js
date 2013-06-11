/**
 * @fileOverview here
 *
 * @description
 * This is a description of what this file is
 * 
 */


/**
* @constructor Sample
*
* @description 
* An example to build out a simple js doc
*
* @version 1.0
* @author 
*/
window.Sample = (function($){
	
	return {

		/**
		 * @function Sample.foo sample foo
		 * 
		 *
		 */
		foo: function() {

		},

		/**
		 * @namespace Sample.tier2 - "Sample.bar" is the same as having a @memberOf Sample
		 * 
		 */
		tier2: {

			/**
			 * @function foobage "Foo beige"
			 * @memberOf Sample.tier2
			 * 
			 */
			foobage: function() {

			},

			/**
			 * @object tier3
			 * @memberOf Sample.tier2
			 * 
			 * @description 
			 * Third level
			 * 
			 */
			tier3: {

				/**
				 * @function foo level 3!
				 * @memberOf  Sample.tier2.tier3
				 * 
				 */
				foo: function() {

				},

				/**
				 * @object Sample.tier2.tier3.tier4 OMG  4th leva!!!
				 * 
				 */
				tier4: {

					/**
					 * @function foo Do you really go this deep?
					 * @memberOf Sample.tier2.tier3.tier4
					 *
					 * @param {string} holla
					 * 
					 */
					foo: function(holla) {

					}					


				}

			},

			/**
			 * @function Sample.tier2.fooTwo fooTwo Foo two, @memberOf part of the function name
			 *
			 */
			fooTwo: function() {

			}


		}



	}

	/**
	 * @function rogue A rogue function
	 * @private
	 *
	 */
	function rogue() {

	}
	
}(jQuery));