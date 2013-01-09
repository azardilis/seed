function register_info(){
	var url=window.location.pathname;
	var password=document.forms['register']['ps'];
	var retype=document.forms['register']['retype'];
	var canvas=document.createElement('canvas');
	var av;

	url=url+"?reg=yes";
	if(password.value==null || password.value=='' || password.value=='Password' || retype.value==null || retype.value=='' || retype.value=='Retype Password'){
		alert('Mandatory information has not been completed');
	}
	var input_obs=document.forms['register'];
	$.ajax({
		type:"post",
		url:url,
		dataType:'html',
		cache:false,
		data:{email:input_obs[0].value,password:input_obs[1].value,retype:input_obs[2].value,full_name:input_obs[5].value,course:input_obs[3].value,year:input_obs[4].value},
		success:function(data){
			alert('You are now registered to the forum');
		},
		error:function(){
			alert("Something went wrong");
		}


	});
}
