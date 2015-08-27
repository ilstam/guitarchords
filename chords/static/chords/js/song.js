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

$('#hide_tabs').click(function() {
    $('.tabsline').toggle();
    $('#hide_tabs').text(
        $('#hide_tabs').text() == 'Hide tabs' ? 'Show tabs' : 'Hide tabs');
})

$('#semiton_change').change(function() {
    var semitonsMove = parseInt($(this).find(':selected').text(), 10);
    $('.chord').each(function() {
        $(this).children('.chordname').text(
            changeSemiton($(this).attr('origchord'), semitonsMove));
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
    if (semitonsMove === 0)
        return chord;

    var semitons = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

    var regex = /([A-G][#b]?)((maj|m|aug|dim|sus)?[245679]?)/;

    var match = regex.exec(chord);
    var origSemiton = match[1];
    var restChord = match[2];

    if (origSemiton.charAt(1) === 'b') {
        var map = {'Ab' : 'G#', 'Bb' : 'A#', 'Cb' : 'B', 'Db' : 'C#',
                   'Eb' : 'F#', 'Fb' : 'E', 'Gb' : 'F#'};
        var origSemiton = map[origSemiton];
    }

    var index = semitons.indexOf(origSemiton) + semitonsMove;
    if (index >= semitons.length)
        index = index % semitons.length;
    else if (index < 0)
        index = semitons.length + index;

    return semitons[index] + restChord;
}

/**
 * Encloses each chord in a span tag of class "chord", and assigns an
 * appropriate image to it. Additionally it encloses each line containing
 * chords in a div tag of class "chordline" and each line containing tabs
 * in a div tag of class "tabsline".
 */
function parseSong() {
    var content = $("#song_content");

    // parse tabs
    var regex = /^[A-Ga-g]\|?[1-9-]{3,}/;
    var lines = content.html().split('\n');
    var newlines = [];
    for (i = 0; i < lines.length; i++) {
        if (regex.test(lines[i]))
            lines[i] = '<div class="tabsline">' + lines[i] + '</div>';
        else
            lines[i] += '\n'
        newlines.push(lines[i]);
    }

    // parse chords
    var lines = newlines;
    var finallines = "";

    for (i = 0; i < lines.length; i++) {
        if (lines[i].indexOf('<div class="tabsline">') != -1) {
            // don't parse tab lines for chords
            finallines += lines[i];
            continue;
        }

        lines[i] = lines[i].replace(
            /([A-G][#b]?(maj|m|aug|dim|sus)?[245679]?)/g,
            '<span class="chord" origchord="$1"><span class="chordname">$1</span>' +
            '<img src="http://placehold.it/100x120"></span>'
        );

        if (lines[i].indexOf('<span class="chord"') != -1)
            finallines += '<div class="chordline">' + lines[i] + '</div>';
        else
            finallines += lines[i];
    }

    content.html(finallines);
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
