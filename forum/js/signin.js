var last_input="";
var last_value="";
function fade(){
   var inp=document.activeElement;
   last_input=inp;
   last_value=inp.value;
   inp.value="";
   if(inp==document.getElementById('ps') || inp==document.getElementById('retype')){
	inp.type="password";
	}
   }
function rewrite(){
   if(last_input.value==""){//if the user has not written anything yet
	if(last_input==document.getElementById('ps') || last_input==document.getElementById('retype')){
   		last_input.type="text";
	}
	last_input.value=last_value;
   }
}

function register_info(){
	url=window.location.pathname;
	url=url+"?reg=yes";
	var password=document.forms['register']['ps'];
	var retype=document.forms['register']['retype'];
	if(password.value==null || password.value=='' || password.value=='Password' || retype.value==null || retype.value=='' || retype.value=='Retype Password'){
		alert('Mandatory information has not been completed');
	}
	var input_obs=document.forms['register'];
	var form_info=new Array();
	for(var i=0;i<input_obs.length;i++){
		form_info[i]=input_obs[i].value;
	}
	$.ajax({
		type:"post",
		url:url,
		dataType:'html',
		cache:false,
		data:{email:form_info[0],password:form_info[1],retype:form_info[2],full_name:form_info[3],avatar:form_info[4],course:form_info[5],year:form_info[6]},
		success:function(data){
			alert('You are now registered to the forum');
		},
		error:function(){
			alert("Something went wrong");
		}


	});
//	window.location="http://localhost:8080"+url;
}
