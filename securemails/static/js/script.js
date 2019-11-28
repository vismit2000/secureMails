var userPubKey;
var userPrivKey;
var otherUserPubKey;
var otherUserMail;
var myMail;
var sessionKey = 'xxxxxxxxxx';
var msgAvail;
var mssgContent;

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
		// console.log(csrftoken);
        // Add csrf token
        request.setRequestHeader("X-CSRFToken", csrftoken);
        request.setRequestHeader("Content-Type", "application/json; charset=utf-8");
        // Send the request
        console.log(data);
        request.send(JSON.stringify(data));
    });

}

function encrypt()
{
    var session =  {
        'userA' : myMail,
        'userB' : otherUserMail
    };
    sendRequest("/mailapp/getSessionKey/","POST",session)
        .then(function (response) {
            response = JSON.parse(response);
            // console.log(response['error']);
            console.log("Success in saving session key!",response);
            sessionKey = response['sessionKey'];
            
            if(sessionKey == 'xxxxxxxxxx')
            {
                // Generate symmetric key (8 4-byte words = 256 bits)
                // 10 is maximum paranoia level
                var symmetric_key = sjcl.codec.base64.fromBits(sjcl.random.randomWords(8, 10));

                // Encrypt it using my public key
                var sk_sym_1 = sjcl.encrypt(userPubKey, symmetric_key);
                
                // Encrypt it using receiver’s public key
                var sk_sym_2 = sjcl.encrypt(otherUserPubKey, symmetric_key);

                var dict = {
                    'keyEncA' : sk_sym_1,
                    'keyEncB' : sk_sym_2,
                    'userA'   : myMail,
                    'userB'   : otherUserMail
                };

                sendRequest("/mailapp/saveSessionKey/","POST",dict)
                .then(function (response) {
                    response = JSON.parse(response);
                    // console.log(response['error']);
                    console.log("Success in saving session key!",response);
                    sessionKey = dict['keyEncA'];
                    // sessionKey = JSON.parse(sessionKey);
                    encMain(sessionKey);
                })
                .catch(function (error) {
                    console.log("Something went wrong", error);
                });       
                
            }
            else
            {
                // sessionKey = JSON.parse(sessionKey);
                encMain(sessionKey);
            }
            console.log('Got session Key successfully : ', sessionKey)

            
        })
    //     .catch(function (error) {
    //         console.log("Something went wrong", error);
    // });       

}

function encMain(sessionKey){
            console.log('inside encMain()')
            console.log(sessionKey);
            var data = document.getElementsByClassName('messageBox')[0].value;
            console.log(['msg', data]);
            console.log(['privKey', userPrivKey]);
            console.log(['sessionKey', sessionKey ]);

            // userPrivKey = new sjcl.ecc.elGamal.secretKey(
            //     sjcl.ecc.curves.c256,
            //     sjcl.ecc.curves.c256.field.fromBits(sjcl.codec.base64.toBits(userPrivKey))
            // );

            var symmetric_key = sjcl.decrypt(userPrivKey, sessionKey);
            console.log(['sym key', symmetric_key]);
            var encrypted = sjcl.encrypt(symmetric_key, data);
            console.log(['encMsg', encrypted]);
            var parsedEncData = JSON.parse(encrypted    );
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
                msgContent = '127.0.0.1:8000/mailapp/getparams/?ivsaltsender='+parsedEncData['iv']+'|@@@@@|'+parsedEncData['salt']+'|!!!!!|'+myMail;

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

function decrypt(data, keyEnc)
{
    console.log(data,',...............,',keyEnc);
    var symmKey = sjcl.decrypt(userPrivKey, keyEnc);
    data = JSON.stringify(data);
    console.log(data);
    var decrypted = sjcl.decrypt(symmKey, data);
    document.getElementsByClassName('messageBox')[0].value = decrypted;
}

function getkey(status, key, sec)
{
    console.log(status, key);
    console.log(status, sec);

    var pair; 
    var pub;

    if(status === 'False'){
        console.log('Generating key pair..');
        console.log(sjcl);
        // console.log(sjcl.ecc);
        pair = sjcl.ecc.elGamal.generateKeys(256);

        pub = pair.pub.get(), sec = pair.sec.get()
        
        // Serialized public key:
        pub = sjcl.codec.base64.fromBits(pub.x.concat(pub.y))
        // uQuXH/yeIpQq8hCWiwCTIMKdsaX...

        // Unserialized public key:
        userPubKey = new sjcl.ecc.elGamal.publicKey(
            sjcl.ecc.curves.c256, 
            sjcl.codec.base64.toBits(pub)
        );
        
        // Serialized private key:
        sec = sjcl.codec.base64.fromBits(sec)
        // IXkJSpYK3RHRaVrd...
        userPrivKey = sec;

        if (typeof(Storage) !== "undefined") {
            // Code for localStorage/sessionStorage.
            localStorage.setItem('userPrivKey_'+myMail,userPrivKey);
        }
        // // Unserialized private key:
        // sec = new sjcl.ecc.elGamal.secretKey(
        //     sjcl.ecc.curves.c256,
        //     sjcl.ecc.curves.c256.field.fromBits(sjcl.codec.base64.toBits(sec))
        // )
        var dict = {};
        dict['key'] = pub;
        dict['sec'] = sec;

        sendRequest("/mailapp/savekey/","POST",dict)
        .then(function (response) {
            response = JSON.parse(response);
            // console.log(response['error']);
            console.log("Success!",response);
            if(msgAvail == 'true')
            {
                userPrivKey = new sjcl.ecc.elGamal.secretKey(
                        sjcl.ecc.curves.c256,
                        sjcl.ecc.curves.c256.field.fromBits(sjcl.codec.base64.toBits(userPrivKey))
                    );
                
                decrypt(mssgContent,sessionKey);
            }
        })
        .catch(function (error) {
            console.log("Something went wrong", error);
        });       
    }
    else{
        //decode the key
        userPubKey = new sjcl.ecc.elGamal.publicKey(
                sjcl.ecc.curves.c256, 
                sjcl.codec.base64.toBits(key)
        );
        userPrivKey = new sjcl.ecc.elGamal.secretKey(
            sjcl.ecc.curves.c256,
            sjcl.ecc.curves.c256.field.fromBits(sjcl.codec.base64.toBits(sec))
        )
        console.log(userPubKey,'..........................', userPrivKey);
        if(msgAvail == 'true')
        {    
            console.log('hah?');
            console.log('sessionKey', sessionKey);
            decrypt(mssgContent,sessionKey);
        }
    }
}

function getOtherUserKey(elem)
{
    console.log(elem);
    var index = elem.indexOf('|@@@@@|');
    otherUserMail = elem.substring(0,index);
    otherUserPubKey = elem.substring(index+7);
    otherUserPubKey = new sjcl.ecc.elGamal.publicKey(
        sjcl.ecc.curves.c256, 
        sjcl.codec.base64.toBits(otherUserPubKey)
    );
    // console.log([otherUserMail, otherUserPubKey])
}

function saveMail(mail)
{
    myMail = mail;
    // console.log(myMail);
}

function saveSender(sender)
{
    otherUserMail = sender;
}

function setmsgstatus(status, data, sesKey)
{
    msgAvail = status;
    mssgContent = data;
    sessionKey = sesKey;
}

function savePrivKey(key)
{
    userPrivKey = key;
}