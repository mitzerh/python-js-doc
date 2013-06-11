(function($){

	$(function(){

		var sections = $(".main > section"), articles = sections.find("> article"), rail = $(".rail"), toTop = $("footer > .to-top"),
			railOffset = rail.offset().top;

		/**
		 * @function setHighlight
		 * @private
		 * 
		 */
		var setHighlight = function() {
			var hash = window.location.hash.substr(1) || "", id = false;
			articles.removeClass("highlight");
			rail.find("li").removeClass("highlight");
			
			setTimeout
			if (hash.length > 2) {
				var id = hash.split("-")[1] || false;
				if (id) {
					sections.find("> article[data-id*='"+id+"']").addClass("highlight");
					rail.find("li[data-id*='"+id+"']").addClass("highlight");
				}

			}
		};

		/**
		 * @function setRailFloat
		 * @private
		 * 
		 */
		var setRailFloat = function() {
			var diff = railOffset - $(this).scrollTop();
			if (diff < 0 && !rail.hasClass("float")) {
				toTop.addClass("show");
				rail.addClass("float");
			} else if (diff > 0 && rail.hasClass("float")) {
				toTop.removeClass("show");
				rail.removeClass("float");
			}
		};

		/**
		 * hash listener
		 */
		$(window).bind("hashchange", function(){
			setHighlight();
		});

		/**
		 * on scroll
		 */
		$(window).bind("scroll", function(){
			setRailFloat();
		});

		/**
		 * on load
		 */
		setHighlight();
		setRailFloat();
		
	});
	

}(jQuery));