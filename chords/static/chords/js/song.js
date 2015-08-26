$('#song_content').on('mouseover', '.chord', function() {
    $(this).children('img').css('visibility', 'visible');
})

$('#song_content').on('mouseout', '.chord', function() {
    $(this).children('img').css('visibility', 'hidden');
})

$('#hide_chords').click(function() {
    $('.chordline').toggle();
    $('#hide_chords').text(
        $('#hide_chords').text() == 'Hide chords' ? 'Show chords' : 'Hide chords');
})

$('#semiton_change').change(function() {
    var semitonsMove = parseInt($(this).find(':selected').text(), 10);
    $('.chord').each(function() {
        //changeSemiton($(this), semitonsMove);
        $(this).text(changeSemiton($(this).attr('origchord'), semitonsMove));
    });
})


/**
 * Return the given chord, changed by semitonsMove semitons.
 *
 * @param {String} chord a string representing a chord, eg. "A#5"
 * @param {Number} semitonsMove an integer from -5 to 6
 * @return {String} the changed chord
 */
function changeSemiton(chord, semitonsMove) {
    var semitons = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    var regex = /([A-G][#b]?)((maj|m|aug|dim|sus)?[245679]?)/;

    var match = regex.exec(chord);
    var origSemiton = match[1];
    var restChord = match[2];

    var index = semitons.indexOf(origSemiton) + semitonsMove;
    if (index >= semitons.length)
        index = index % semitons.length;
    else if (index < 0)
        index = semitons.length + index;

    return semitons[index] + restChord;
}

/**
 * Each chord must be enclosed in a span tag of class "chord", and an
 * appropriate image must be assigned to it. Additionally, each line of
 * song content containing chords should be enclosed in div tags of class
 * "chordline"".
 */
function parseSong() {
    var content = $("#song_content");
    var result = content.html().replace(
        /([A-G][#b]?(maj|m|aug|dim|sus)?[245679]?)/g,
        '<span class="chord" origchord="$1">$1<img src="http://placehold.it/100x120"></span>'
    );

    var lines = result.split('\n');
    var newlines = "";

    for (i = 0; i < lines.length; i++) {
        if (lines[i].indexOf('<span class="chord"') != -1)
            newlines += '<div class="chordline">' + lines[i] + '</div>';
        else
            newlines += lines[i] + "\n";
    }
    content.html(newlines);
}

/**
 * Fills the semiton_change select object, with the values from -5 to 6
 * followed by the base chord of the song at the specific semiton.
 *
 * eg. -1 (D), 0 (D#), +1 (E)
 */
function fillSemitonChange() {
    var songBase = $('.chord').first().attr('origchord');
    for (i = 6; i >= -5; i--) {
        if (i != 0) {
            $('#semiton_change')
                .append($('<option></option>')
                .text((i>0 ? '+' : '') + i + ' (' + changeSemiton(songBase, i) + ')'));
        } else {
            $('#semiton_change')
                .append($('<option></option>')
                .attr('selected', 'selected')
                .text(i + ' (' + changeSemiton(songBase, i) + ')'));
        }
    }
}


$().ready(function() {
    parseSong();
    fillSemitonChange();
});
