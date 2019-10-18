var encrypted;
let request = obj => {
    return new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();
        xhr.open(obj.method || "GET", obj.url);
        if (obj.headers) {
            Object.keys(obj.headers).forEach(key => {
                xhr.setRequestHeader(key, obj.headers[key]);
            });
        }
        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(xhr.response);
            } else {
                reject(xhr.statusText);
            }
        };
        xhr.onerror = () => reject(xhr.statusText);
        xhr.send(obj.body);
    });
};

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
    
    var content = JSON.parse(encrypted)['ct'];    
    var key = encrypted['iv']+'|'+encrypted['salt'];
    var dict = {};
    dict['key'] = key;
    dict['value'] = encrypted;
    
    var reqObj = {
        'method' : 'POST',
        'url' : '/mailapp/savedata/',
        'body' : JSON.stringify(dict)
    };
    
    request(reqObj).
    then(data => {
        console.log(data);
        document.getElementsByClassName('messageBox')[0].value = content;
        content += '&nbsp;&nbsp;&nbsp;&nbsp; &lt;a href="https://harpinderjotsingh.github.io/secureMails/"&gt;&lt;/a&gt;';
        
        if (confirm("Enciphered!! do you want to mail it?")) {
            window.location.href = 'https://mail.google.com/mail/?view=cm&fs=1&tf=1&body='+content;
        } 
        else {
            console.log('cancelled!!');
        }
    })
    .catch(error => {
        console.log(error);
    });
}

function decrypt()
{
    var pwd = getPassword();
    var data = document.getElementsByClassName('messageBox')[0].value;
    var decrypted = sjcl.decrypt(pwd, JSON.parse(encrypted)['ct']);
    document.getElementsByClassName('messageBox')[0].value = decrypted;
}