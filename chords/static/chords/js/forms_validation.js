$(function() {

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

$('#new_password1').keyup(function() {
    var pass1 = $('#new_password1');
    applyValidationGlyphicon(pass1, pass1.val().length >= 5);
});

$('#new_password2').keyup(function() {
    var pass2 = $('#new_password2');
    applyValidationGlyphicon(pass2, pass2.val().length >= 5 && pass2.val() == $('#new_password1').val());
});

$('#password_change_form').submit(function(event) {
    var pass1 = $('#new_password1');
    var pass2 = $('#new_password2');
    var oldpass = $('#old_password');

    if (oldpass.val() == "") {
        oldpass.parent().addClass('has-error');
        event.preventDefault();
    } else {
        oldpass.parent().removeClass('has-error');
    }

    if (! applyValidationGlyphicon(pass1, pass1.val().length >= 5))
        event.preventDefault();
    if (! applyValidationGlyphicon(pass2, pass2.val().length >= 5 && pass2.val() == $('#new_password2').val()))
        event.preventDefault();
});

});
