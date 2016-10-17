/**
 * Created by harikishen on 13/9/16.
 */
var BACKEND = "http://localhost:8000";

function onSignIn(googleUser) {
    var id_token = googleUser.getAuthResponse().id_token;
    var xhr = new XMLHttpRequest();
    xhr.open('POST', BACKEND + '/tokensignin');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onload = function() {
        console.log('Sign in : ' + xhr.responseText);
        if(xhr.responseText === 'success'){
            var profile = googleUser.getBasicProfile();
            console.log('ID: ' + profile.getId());
            console.log('Name: ' + profile.getName());
            console.log('Image URL: ' + profile.getImageUrl());
            console.log('Email: ' + profile.getEmail());
        }
    };
    xhr.send('idtoken=' + id_token);
}

function signOut() {
    var auth2 = gapi.auth2.getAuthInstance();
    auth2.signOut().then(function () {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', BACKEND + '/signout');
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onload = function() {
        console.log('User signed out.');
        }
        xhr.send();
    });
}