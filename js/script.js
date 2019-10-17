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
    var encrypted = JSON.parse(sjcl.encrypt(pwd, data));
    var content = encrypted['ct'];
    content += '&nbsp;&nbsp;&nbsp;&nbsp; &lt;a href="https://harpinderjotsingh.github.io/secureMails/"&gt;&lt;/a&gt;';
    console.log(encrypted);
    if (confirm("Enciphered!! do you want to mail it?")) {
        window.location.href = 'https://mail.google.com/mail/?view=cm&fs=1&tf=1&body='+content;
    } 
    else {
        console.log('cancelled!!');
    }
    // document.getElementsByClassName('messageBox')[0].value = encrypted['ct'];
    // console.log(data);
}

function decrypt()
{
    var pwd = getPassword();
    var data = document.getElementsByClassName('messageBox')[0].value;
    var decrypted = sjcl.decrypt(pwd, data);
    var content = decrypted;
    document.getElementsByClassName('messageBox')[0].value = content;
}