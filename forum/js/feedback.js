var enabledPopup = null;

$(document).ready(function(){

	//LOAD POPUP
	if ($("#hiddenRatingId").text().length){
		loadPopup($("#hiddenRatingId").text());
	}

	//CLOSE POPUP
	$(".popupClose").click(function(){	//Click the x event!
		disablePopup();
	});
	$("#backgroundPopup").click(function(){	//Click out event!
		disablePopup();
	});
	$(document).keypress(function(e){ 
		if(e.keyCode==27 && enabledPopup){ //Press Escape event!
			disablePopup();
		}
	});

});

function loadPopup(popupId){
	
	centerPopup(popupId);
	
	if(!enabledPopup){
		$("#backgroundPopup").css({"opacity": "0.7"});

		$("#backgroundPopup").fadeIn("slow");
		$(popupId).fadeIn("slow");
		
		enabledPopup = popupId;
	}
}

function disablePopup(){
	if(enabledPopup){

		$("#backgroundPopup").fadeOut("slow");
		$(enabledPopup).fadeOut("slow");

		enabledPopup = null;
	}
}

function centerPopup(popupId){
	//request data for centering
	var windowWidth = document.documentElement.clientWidth;
	var windowHeight = document.documentElement.clientHeight;
	var popupHeight = $(popupId).height();
	var popupWidth = $(popupId).width();
	
	//centering
	$(popupId).css({
		"position": "absolute",
		"top": windowHeight/2-popupHeight,
		"left": windowWidth/2-popupWidth
	});
	//only need force for IE6

	$("#backgroundPopup").css({
		"height": windowHeight
	});
}

