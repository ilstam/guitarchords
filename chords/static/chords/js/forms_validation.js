$(function() {

function applyValidationError(obj, validates) {
    if (validates)
        obj.closest('.form-group').removeClass('has-error');
    else
        obj.closest('.form-group').addClass('has-error');
    return validates;
}

function applyValidationGlyphicon(obj, validates) {
    if (validates) {
        obj.closest('.form-group').addClass('has-success has-feedback');
        obj.closest('.form-group').removeClass('has-error');
        obj.siblings('span.glyphicon').addClass('glyphicon-ok');
        obj.siblings('span.glyphicon').removeClass('glyphicon-remove');
        obj.siblings('span.sr-only').text('(success)');
    } else {
        obj.closest('.form-group').addClass('has-error has-feedback');
        obj.closest('.form-group').removeClass('has-success');
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

    var v1 = (! applyValidationError(oldpass, oldpass.val() != ''))
    var v2 = (! validatePassword1(pass1, pass2))
    var v3 = (! validatePassword2(pass1, pass2))

    if (v1 || v2 || v3)
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

    var v1 = (! applyValidationError(username, /^[\w@+-.]{1,30}$/.test(username.val())))
    var v2 = (! applyValidationError(email, email.val() != ''))
    var v3 = (! validatePassword1(pass1, pass2))
    var v4 = (! validatePassword2(pass1, pass2))

    if (v1 || v2 || v3 || v4)
        event.preventDefault();
});

$('#add_song_form').submit(function(event) {
    var title = $('#id_title');
    var artist = $('#id_artist_txt');
    var content = $('#id_content');

    if (! applyValidationError(content, content.val() != '')) {
        event.preventDefault();
        var _top = content.position().top;
        $(window).scrollTop(_top);
    }

    if (! applyValidationError(artist, artist.val() != '')) {
        event.preventDefault();
        var _top = artist.parent().siblings('label').position().top;
        $(window).scrollTop(_top);
    }

    if (! applyValidationError(title, title.val() != '')) {
        event.preventDefault();
        var _top = title.parent().siblings('label').position().top;
        $(window).scrollTop(_top);
    }
});


/**
 * After validating the form, perform an AJAX POST request in order to save
 * the new comment in the database and append it to the page.
 */
$('#comment_form').submit(function(event) {
    event.preventDefault();

    var content = $('#id_content');
    if (! applyValidationError(content, content.val() != ''))
        return;

    var url = window.location.protocol + '//' + window.location.host + '/chords/add_comment/';
    var data = {
        username : $('#id_user').attr('value'),
        song_slug : $('#id_song').attr('value'),
        content : $('#id_content').val(),
        csrfmiddlewaretoken : $('[name="csrfmiddlewaretoken"]').attr('value'),
    };

    $.post(url, data, function(data) {
        $('#comments_row').append(data);
        content.val('');
    }).fail(function() {
        // empty
    });
});

});
