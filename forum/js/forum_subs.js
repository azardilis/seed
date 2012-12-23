function update_subs(sub,sub_code){
	var container = document.getElementById('allsubs');

	$.ajax({
		url:"/forum?mod="+sub,
		cache:false,
		data:sub,
		dataType:'html',
		success:function(){
			alert("You have unsubscribed from the module wiht code "+sub_code);
			var mod=document.getElementById(sub_code);
			container.removeChild(mod);
		},
		error:function(){
			alert("Something went wrong and you could not unsubscrube from this module");
		}


	});
};
