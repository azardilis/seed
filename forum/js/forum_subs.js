function update_subs(sub,sub_code,profile){
	var container = document.getElementById('allsubs');
	var redirect_url = "";
	if (profile){
		redirect_url="/profile?mod="+sub;
	}else{
		redirect_url="/forum?mod="+sub;
	}
	
	$.ajax({
		
		url:redirect_url,
		cache:false,
		data:sub,
		dataType:'html',
		success:function(){
			alert("You have unsubscribed from the module with code "+sub_code);
			var mod=document.getElementById(sub_code);
			container.removeChild(mod);
		},
		error:function(){
			alert("Something went wrong and you could not unsubscrube from this module");
		}


	});
};

$(document).ready(function(){
    $("#rss").hide();
    $("#rss_button").click(function(e){
	$("#rss").slideToggle();
	$("#url").focus();
	$("#url").select();
	e.preventDefault();
    });
});
