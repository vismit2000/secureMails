var encrypted;
function getCookie(name) {
  var v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
  return v ? v[2] : null;
}

function sendRequest(url,type,data){
    let request = new XMLHttpRequest();
    let csrftoken = getCookie("csrftoken");
    return new Promise(function(resolve, reject){
        request.onreadystatechange = () => {
            if (request.readyState !== 4) return;
            // Process the response
			if (request.status >= 200 && request.status < 300) {
                // If successful
				resolve(request.responseText);
			} else {
				// If failed
				reject({
					status: request.status,
					statusText: request.statusText
				});
			}
        };
        // Setup our HTTP request
		request.open(type || "GET", url, true);
		console.log(csrftoken);
        // Add csrf token
        request.setRequestHeader("X-CSRFToken", csrftoken);
        request.setRequestHeader("Content-Type", "application/json; charset=utf-8");
        // Send the request
        request.send(JSON.stringify(data));
    });

}

function getPassword()
{
    var pwd = prompt("Please enter password!!");
    var status = ((pwd === undefined) || (pwd === null)) ? -1 : 1;
    if(status == -1)
    {
        getPassword();
    }
    else
    {
        return pwd;
    }
}
function encrypt()
{

    var pwd = getPassword();
    var data = document.getElementsByClassName('messageBox')[0].value;
    encrypted = sjcl.encrypt(pwd, data);
    var parsedEncData = JSON.parse(encrypted);
    var content = parsedEncData['ct'];
    var key = parsedEncData['iv']+'|@|'+parsedEncData['salt'];
    var dict = {};
    dict['key'] = key;
    dict['value'] = encrypted;
    console.log(dict);

    sendRequest("/mailapp/savedata/","POST",dict)
	.then(function (response) {
        response = JSON.parse(response);
        // console.log(response['error']);
        console.log("Success!",response);

        document.getElementsByClassName('messageBox')[0].value = content;
        msgContent = 'https://bitsf463.pythonanywhere.com//mailapp/getparams/?ivsalt='+parsedEncData['iv']+'|@@@@@|'+parsedEncData['salt'];

        if (confirm("Enciphered!! do you want to mail it?")) {
            window.location.href = 'https://mail.google.com/mail/?view=cm&fs=1&tf=1&body='+encodeURIComponent(msgContent);
        }
        else {
            console.log('cancelled!!');
        }
    })
	.catch(function (error) {
		console.log("Something went wrong", error);
    });
}

function decrypt(data)
{
    var pwd = getPassword();
    // data = JSON.stringify(data);
    console.log(data);
    var decrypted = sjcl.decrypt(pwd, data);
    document.getElementsByClassName('messageBox')[0].value = decrypted;
}