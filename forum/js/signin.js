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
	av=input_obs[4].value;
	//ctx=canvas.getContext('2d');
	//alert('asd');
	//ctx.drawImage(av,0,0);
	//var dataURL=canvas.toDataURL('image/png');
	$.ajax({
		type:"post",
		url:url,
		dataType:'html',
		cache:false,
		data:{email:input_obs[0].value,password:input_obs[1].value,retype:input_obs[2].value,full_name:input_obs[3].value,avatar:av,course:input_obs[5].value,year:input_obs[6].value},
		success:function(data){
			alert('You are now registered to the forum');
		},
		error:function(){
			alert("Something went wrong");
		}


	});
}
