$(function() {

function applyValidationError(obj, validates) {
    if (validates)
        obj.parent().removeClass('has-error');
    else
        obj.parent().addClass('has-error');
    return validates;
}

function applyValidationGlyphicon(obj, validates) {
    if (validates) {
        obj.parent().addClass('has-success has-feedback');
        obj.parent().removeClass('has-error');
        obj.siblings('span.glyphicon').addClass('glyphicon-ok');
        obj.siblings('span.glyphicon').removeClass('glyphicon-remove');
        obj.siblings('span.sr-only').text('(success)');
    } else {
        obj.parent().addClass('has-error has-feedback');
        obj.parent().removeClass('has-success');
        obj.siblings('span.glyphicon').addClass('glyphicon-remove');
        obj.siblings('span.glyphicon').removeClass('glyphicon-ok');
        obj.siblings('span.sr-only').text('(error)');
    }
    return validates;
}


/**
 * @param {String} password
 * @return True if password is valid, else False
 */
function passwordIsValid(password) {
    return password.length >= 5;
}

/**
 * @param {Object} pass1
 * @return True if password is valid, else False
 */
function validatePassword1(pass1, pass2) {
    validatePassword2(pass1, pass2);
    return applyValidationGlyphicon(pass1, passwordIsValid(pass1.val()));
}

/**
 * @param {Object} pass1
 * @param {Object} pass2
 * @return True if passwords are valid, else False
 */
function validatePassword2(pass1, pass2) {
    return applyValidationGlyphicon(pass2, passwordIsValid(pass1.val()) && pass1.val() == pass2.val());
}

$('#new_password1').keyup(function() {
    validatePassword1($(this), $('#new_password2'));
});

$('#new_password2').keyup(function() {
    validatePassword2($('#new_password1'), $(this));
});

$('#password1').keyup(function() {
    validatePassword1($(this), $('#password2'));
});

$('#password2').keyup(function() {
    validatePassword2($('#password1'), $(this));
});

$('#password_change_form').submit(function(event) {
    var pass1 = $('#new_password1');
    var pass2 = $('#new_password2');
    var oldpass = $('#old_password');

    if (! applyValidationError(oldpass, oldpass.val() != ''))
        event.preventDefault();

    if (! validatePassword1(pass1, pass2))
        event.preventDefault();

    if (! validatePassword2(pass1, pass2))
        event.preventDefault();
});

$('#password_reset_confirm_form').submit(function(event) {
    var pass1 = $('#new_password1');
    var pass2 = $('#new_password2');

    if (! validatePassword1(pass1, pass2))
        event.preventDefault();

    if (! validatePassword2(pass1, pass2))
        event.preventDefault();
});

$('#registration_form').submit(function(event) {
    var username = $('#username');
    var email = $('#email');
    var pass1 = $('#password1');
    var pass2 = $('#password2');

    if (! applyValidationError(username, /^[\w@+-.]{1,30}$/.test(username.val())))
        event.preventDefault();

    if (! applyValidationError(email, email.val() != ''))
        event.preventDefault();

    if (! validatePassword1(pass1, pass2))
        event.preventDefault();

    if (! validatePassword2(pass1, pass2))
        event.preventDefault();
});

});
