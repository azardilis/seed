/*function that splits the serialized string of data that is
 sent to the server
 */
 function returnArray(str){
 	var arr = str.split("&");
 	for (i in arr){
 		arr[i] = arr[i].split("=");
 	}
 	return arr;
 }

 /*TODO - makes the toolbar for each post*/
 function makeToolbar(pid, pstrname){
 	var controlsSection = document.createElement('section');
 	controlsSection.setAttribute('id','controls')

 	var controlButtons = document.createElement('section');
 	controlButtons.setAttribute('class','controlButtons');

 	var score = document.createElement('p');
 	var reply = document.createElement('p');
 	var quote = document.createElement('p');
 	var vu = document.createElement('p');
 	var vd = document.createElement('p');
 	var sc = document.createTextNode('0');
 	
 	score.setAttribute('pid',pid);
 	score.setAttribute('class','score');
 	reply.setAttribute('pid',pid);
 	reply.setAttribute('class','reply');
 	quote.setAttribute('class','quote');
 	quote.setAttribute('pid',pid);
 	vu.setAttribute('pid',pid);
 	vu.setAttribute('class','voteup');
 	vd.setAttribute('pid',pid);
 	vd.setAttribute('class','votedown');

 	score.appendChild(sc);
 	controlButtons.appendChild(score);
 	controlButtons.appendChild(reply);
 	controlButtons.appendChild(quote);
 	controlButtons.appendChild(vu);
 	controlButtons.appendChild(vd);



 	var rf = document.createElement('form');
 	rf.setAttribute('id','rf'+pid);
 	rf.setAttribute('class','psreplyform');
 	rf.setAttribute('method','POST');
 	rf.setAttribute('action','/replypost');

 	var inpt = document.createElement('input');
 	inpt.setAttribute('type','hidden');
 	inpt.setAttribute('name','r2pid');
 	inpt.setAttribute('value',pid);

 	var inpt2 = document.createElement('input');
 	inpt2.setAttribute('type','hidden');
 	inpt2.setAttribute('name','poster');
 	inpt2.setAttribute('value',pstrname);

 	var intxt = document.createElement('textarea');
 	intxt.setAttribute('name','bd');
 	intxt.setAttribute('rows','5');
 	intxt.setAttribute('cols','50');

 	var insbmt = document.createElement('input');
 	insbmt.setAttribute('type','submit');
 	insbmt.setAttribute('value','Reply');

 	rf.appendChild(inpt);
 	rf.appendChild(inpt2);
 	rf.appendChild(intxt);
 	rf.appendChild(insbmt);

 	controlsSection.appendChild(controlButtons);
 	controlsSection.appendChild(rf);

 	return controlsSection ;
 }

 /*append a post to the body of the thread (at level 1)*/
 function appendPost(arr,newID){
 	var bd = '' ;
 	for (i in arr){
 		if (arr[i][0] === 'bd'){
 			bd = arr[i][1];
 		}
 	}

 	var sE = document.createElement('section');
 	sE.setAttribute('class','post');

 	var art = document.createElement('article');

 	var txt = document.createTextNode(bd+' (refresh page for actions).');
 	art.appendChild(txt);
 	sE.appendChild(art);

 	var rSection = document.getElementById('responses');
	//add node to the beginning of the posts
	rSection.insertBefore(sE,rSection.childNodes[0]);
}

/*appends to post at level n > 1*/
function appendToPost(arr,usrinfo, newID){

	var bd = '' ;
	var reply_to_post  = 0 ;
	var poster = '';
	var usrimg = '' ;
	var userdegree ;

	for (i in arr){
		if (arr[i][0] === 'bd'){
			bd = arr[i][1];
		}else if(arr[i][0] === 'r2pid'){
			reply_to_post = arr[i][1] ;
		}else if(arr[i][0] === 'poster'){
			poster = arr[i][1];
		}
	}
	
	var psts = document.getElementById('replies'+reply_to_post);

	if(!psts){
		psts = document.createElement('section');
		psts.setAttribute('class','posts');
		psts.setAttribute('id','replies'+reply_to_post);
	}
	var sE = document.createElement('section');
	sE.setAttribute('class','post');

	var usrdtls = document.createElement('section');
	usrdtls.setAttribute('class','userDetails');

	var uimg = document.createElement('img');
	uimg.setAttribute('src',usrimg);
	usrimg.setAttribute('class','pstimg');

	var uname = document.createElement('p');
	uname.setAttribute('class','username');
	uname.appendChild(document.createTextNode(poster));
	var ud = document.createElement('p');
	ud.setAttribute('class','degree');
	var uk = document.createElement('p');
	uk.setAttribute('class','karma');
	var urd = document.createElement('p');
	urd.setAttribute('class','replydate');

	var art = document.createElement('article');
	art.setAttribute('poster',poster);
	art.setAttribute('pid',reply_to_post);
	art.setAttribute('id','pst'+newID);

	var txt = document.createTextNode(bd+' (refresh page for actions).');
	art.appendChild(txt);


	sE.appendChild(art);
	psts.appendChild(sE);

	var appHere = $('#pst'+reply_to_post).parent();
	appHere.append(psts);
}


$(document).ready(function(){
	
	/*This is AJAX for replying to a THREAD*/
	$("#replyform").submit(function(event)
	{
		var $form = $(this);
		var $inputs = $form.find("input, button,textarea") ;
		serializedData = $form.serialize();
		console.log(serializedData);
		$inputs.attr("disabled", "disabled");

		$.ajax(
		{
			url: "/replythread",
			type: "POST",
			data: serializedData,
			contentType: 'application/x-www-form-urlencoded',
			dataType: 'html',
			success: function(data)
			{
				appendPost(returnArray(serializedData),data);
			},
			error: function(xmlhttp, textStatus, errorThrown)
			{
				console.log('There was an error while replying to thread.');
			},
			complete: function()
			{
				$inputs.removeAttr("disabled");
			}
		});
		event.preventDefault();
	});

	/*This toggles the reply box on for replying to a POST*/
	$('p.reply').click(function(){
		var e = $(this);
		var pid = e.attr('pid');
		$('#rf'+pid).slideDown();
	});

	/*This toggles the reply box on for replying to a POST and inputs the quote*/		
	$('p.quote').click(function(){
		var e = $(this);
		var pid = e.attr('pid');
		var poster = $('article#pst'+pid).attr('poster');
		var qs = "[quote="+poster+"]"+$('article#pst'+pid).html()+"[/quote]";
		$('#rf'+pid+' textarea').html(qs);
		$('#rf'+pid).slideDown();
	});

	/*This is AJAX for replying to a POST*/
	$('form.psreplyform').submit(function(event)
	{
		var $form = $(this);
		var $inputs = $form.find("input,textarea").not(':submit', ':hidden') ;
		var serializedData = $form.serialize();	
		console.log(serializedData);		
		$inputs.attr("disabled", "disabled");
		$.ajax(
		{
			url: "/replypost",
			type: "POST",
			data: serializedData,
			contentType: 'application/x-www-form-urlencoded',
			dataType: 'html',
			success: function(data, textStatus)
			{
				appendToPost(returnArray(serializedData), data);
				//$inputs.val('');
			},
			error: function(xmlhttp, textStatus, errorThrown)
			{
				alert('There was an error while replying to post.');
			},
			complete: function()
			{
				$inputs.removeAttr("disabled");
			}
		});
		event.preventDefault();
	});

	/*AJAX for voting up a post*/
	$('p.voteup').click(function(){
		var e = $(this);
		var pid = e.attr('pid');
		var dt = 'pid='+pid
		$.ajax(
		{
			url:'/vup' ,
			type:'POST',
			data : dt ,
			contentType : 'application/x-www-form-urlencoded',
			dataType : 'html',
			success:function(data,textStatus){
				e.siblings('p.score').html(data);
			},
			error: function(xmlhttp, textStatus, errorThrown)
			{
				console.log(textStatus);
			},
			complete: function()
			{
				console.log('request should have completed');
			}
		});
	});

	/*AJAX for voting down post*/
	$('p.votedown').click(function(){
		var e = $(this);
		var pid = e.attr('pid');
		var dt = 'pid='+pid
		$.ajax(
		{
			url:'/vdown' ,
			type:'POST',
			data : dt ,
			contentType : 'application/x-www-form-urlencoded',
			dataType : 'html',
			success:function(data,textStatus){
				e.siblings('p.score').html(data);
			},
			error: function(xmlhttp, textStatus, errorThrown)
			{
				console.log(textStatus);
			},
			complete: function()
			{
				console.log('request should have completed');
			}
		});
	});

	/*AJAX for marking an answer*/
	$('p.ans').click(function(){
		var e = $(this);
		var pid = e.attr('pid');
		var dt = 'pid='+pid;
		var trd = $('article#thread');
		var tid = trd.attr('tid');
		dt +='&tid='+tid;

		$.ajax(
		{
			url:'/solution' ,
			type:'POST',
			data : dt ,
			contentType : 'application/x-www-form-urlencoded',
			dataType : 'html',
			success:function(data){
				if(data === 'ok'){
					var par_section = e.parent().parent().parent();		
					
					if(par_section.attr('class') === 'ans'){
						par_section.attr('class','post');
					}else{
						$('section.ans').attr('class','post'); /*reset all other answers*/
						par_section.attr('class','ans');
					}
				}else{
					console.log('Some error occured, response :'+data)
				}
			},
			error: function(xmlhttp, textStatus, errorThrown)
			{
				console.log('Error in marking answer');
			},
			complete: function()
			{
				console.log('request should have completed');
			}
		});
	});
});