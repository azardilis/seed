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
 	
 	score.setAttribute('pid',pid);
 	score.setAttribute('class','score');
 	score.appendChild(document.createTextNode(0));
 	reply.setAttribute('pid',pid);
 	reply.setAttribute('class','reply');
 	reply.appendChild(document.createTextNode('Reply'));
 	quote.setAttribute('class','quote');
 	quote.setAttribute('pid',pid);
 	quote.appendChild(document.createTextNode('Quote'));
 	vu.setAttribute('pid',pid);
 	vu.setAttribute('class','vote');
 	vu.setAttribute('url','/vup');
 	vu.appendChild(document.createTextNode('Vote-Up'));
 	vd.setAttribute('pid',pid);
 	vd.setAttribute('class','vote');
 	vd.setAttribute('url','/vdown');
 	vd.appendChild(document.createTextNode('Vote-Down'));

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
 function appendPost(arr){
 	
 	elems = makePostSection(arr);
 	var threadRepliesSection = document.getElementById('responses');
	//add node to the beginning of the posts
	threadRepliesSection.insertBefore(elems[1],threadRepliesSection.childNodes[0]);
}

/*appends to post at level n > 1*/
function appendToPost(arr){

	var elems = makePostSection(arr);
	var reply_to_post = elems[0] ; //the post to reply to	
	var replies = document.getElementById('replies'+reply_to_post);

	if(!replies){
		replies = document.createElement('section');
		replies.setAttribute('class','posts');
		replies.setAttribute('id','replies'+reply_to_post);
	}

	replies.appendChild(elems[1]); //the post section

	var appHere = $('#pstsec'+reply_to_post);
	appHere.append(replies);
}

/*a really ugly function for making the dom elements that a post consists of*/
function makePostSection(arr){

	var bd = '' ;
	var reply_to_post  = 0 ;
	var poster = '';
	var usrimg = '' ;
	var usrdegree = '' ;
	var usrkarma = '' ;
	var usrrdate = '' ;
	var usrsig = '' ; 
	var newID = '' ;

	for (i in arr){
		if (arr[i][0] === 'bd'){
			bd = arr[i][1];
		}else if(arr[i][0] === 'r2pid'){
			reply_to_post = arr[i][1] ;
		}else if(arr[i][0] === 'poster'){
			poster = arr[i][1];
		}else if(arr[i][0] === 'usrkarma'){
			usrkarma = arr[i][1];
		}else if(arr[i][0] === 'usrdegree'){
			usrdegree = arr[i][1];
		}else if(arr[i][0] === 'usrimg'){
			usrimg = arr[i][1];
		}else if(arr[i][0] === 'usrrdate'){
			usrrdate = arr[i][1];
		}else if(arr[i][0] === 'usrsig'){
			usrsig = arr[i][1];
		}else if(arr[i][0] === 'newID'){
			newID = arr[i][1];
		}
	}

	var postsec = document.createElement('section');
	postsec.setAttribute('class','post');

	var usrdtls = document.createElement('section');
	usrdtls.setAttribute('class','userDetails');

	var uimg = document.createElement('img');
	uimg.setAttribute('src',usrimg);
	uimg.setAttribute('class','pstimg');

	var uname = document.createElement('p');
	uname.setAttribute('class','username');
	uname.appendChild(document.createTextNode(poster));
	
	var ud = document.createElement('p');
	ud.setAttribute('class','degree');
	ud.appendChild(document.createTextNode(usrdegree));

	var uk = document.createElement('p');
	uk.setAttribute('class','karma');
	uk.appendChild(document.createTextNode('Karma : '+usrkarma));
	
	var urd = document.createElement('p');
	urd.setAttribute('class','replydate');
	urd.appendChild(document.createTextNode(usrrdate));

	usrdtls.appendChild(uimg);
	usrdtls.appendChild(uname);
	usrdtls.appendChild(ud);
	usrdtls.appendChild(uk);
	usrdtls.appendChild(urd);

	var pstbd = document.createElement('section');
	pstbd.setAttribute('class','pstbd');

	var art = document.createElement('article');
	art.setAttribute('poster',poster);
	art.setAttribute('pid',reply_to_post);
	art.setAttribute('id','pst'+newID);
	art.appendChild(document.createTextNode(bd));

	pstbd.appendChild(art);

	var sigsec = document.createElement('section');
	sigsec.setAttribute('class','signature');

	var sigart = document.createElement('article');
	sigart.setAttribute('class','signature');
	sigart.appendChild(document.createTextNode(usrsig));
	sigsec.appendChild(sigart);


	postsec.appendChild(usrdtls);
	postsec.appendChild(pstbd);
	postsec.appendChild(sigsec);
	var tbar = makeToolbar(newID,poster);
	
	postsec.appendChild(tbar);

	return [reply_to_post,postsec];
}

/*Event listeners*/
$(document).ready(function(){
	
	/*This is AJAX for replying to a THREAD*/
	$(document).delegate('#replyform','submit',function(event)
	{
		var $form = $(this);
		var $inputs = $form.find("input, button,textarea") ;
		serializedData = $form.serialize();
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
				appendPost(returnArray(data));
			},
			error: function(xmlhttp, textStatus, errorThrown)
			{
				console.log('There was an error while replying to thread.');
			},
			complete: function()
			{
				$inputs.removeAttr("disabled");
				console.log('Replying to thread completed');
			}
		});
		event.preventDefault();
	});

	/*This is AJAX for replying to a POST*/
	$(document).delegate('.psreplyform','submit',function(event)
	{
		var $form = $(this);
		var $inputs = $form.find("input,textarea").not(':submit', ':hidden') ;
		var serializedData = $form.serialize();	
		$inputs.attr("disabled", "disabled");
		$.ajax(
		{
			url: "/replypost",
			type: "POST",
			data: serializedData,
			contentType: 'application/x-www-form-urlencoded',
			dataType: 'html',
			success: function(data)
			{
				appendToPost(returnArray(data));
			},
			error: function(xmlhttp, textStatus, errorThrown)
			{
				console.log('There was an error while replying to post.');
			},
			complete: function()
			{
				$inputs.removeAttr("disabled");
				console.log('Replying to post completed');
			}
		});
		event.preventDefault();
	});

	/*This toggles the reply box on for replying to a POST*/
	$(document).delegate('p.reply','click',function(){
		var e = $(this);
		var pid = e.attr('pid');
		$('#rf'+pid).slideDown();
	});

	/*This toggles the reply box on for replying to a POST and inputs the quote*/		
	$(document).delegate('p.quote','click',function(){
		var e = $(this);
		var pid = e.attr('pid');
		var poster = $('article#pst'+pid).attr('poster');
		var qs = "[quote="+poster+"]"+$('article#pst'+pid).html()+"[/quote]";
		$('#rf'+pid+' textarea').html(qs);
		$('#rf'+pid).slideDown();
	});

	/*AJAX for voting up/down a post*/
	$(document).delegate('p.vote','click',function(){
		var e = $(this);
		var pid = e.attr('pid');
		var voteurl = e.attr('url');
		var dt = 'pid='+pid
		$.ajax(
		{
			url: voteurl ,
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
				console.log('request completed');
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