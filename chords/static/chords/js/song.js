$(function() {

$('#song_content').on('mouseover', '.chord', function() {
    $(this).children('img').css('visibility', 'visible');
});

$('#song_content').on('mouseout', '.chord', function() {
    $(this).children('img').css('visibility', 'hidden');
});

$('#hide_chords').click(function() {
    $('.chordline').toggle();
    $('#hide_chords').text(
        $('#hide_chords').text() == 'Hide chords' ? 'Show chords' : 'Hide chords');
});

$('#hide_tabs').click(function() {
    $('.tabsline').toggle();
    $('#hide_tabs').text(
        $('#hide_tabs').text() == 'Hide tabs' ? 'Show tabs' : 'Hide tabs');
});

$('#semiton_change').change(function() {
    var semitonsMove = parseInt($(this).find(':selected').text(), 10);
    $('.chord').each(function() {
        var newSemiton = changeSemiton($(this).attr('origchord'), semitonsMove);
        $(this).children('.chordname').text(newSemiton);
        $(this).children('img').attr(
            'src', '/static/chords/img/chords/' +
            encodeURIComponent(alterFlatChords(newSemiton)) + '.png');
    });
});

$('#bookmark').click(function() {
    url = window.location.href;
    if (! url.match('\$'))
        url += '/';

    if ($(this).text().indexOf('Add') != -1)
        add_bookmark(url);
    else
        remove_bookmark(url);
});


/**
 * Perform an AJAX request to bookmark a song.
 *
 * @param url {String} url of the song to bookmark, always ends with '/'
 */
function add_bookmark(url) {
    url += 'add_bookmark/';
    $.get(url, function(data) {
        $('#bookmark').text('(-) Remove from bookmarks')
    })
}

/**
 * Perform an AJAX request to unbookmark a song.
 *
 * @param url {String} url of the song to unbookmark, always ends with '/'
 */
function remove_bookmark(url) {
    url += 'remove_bookmark/';
    $.get(url, function(data) {
        $('#bookmark').text('(+) Add to bookmarks')
    })
}

/**
 * If chord is a flat chord, return its non-flat equivalent.
 * Else, return the chord unchanged.
 *
 * eg. "Ab" -> "G#", "Cb" -> "B", "G" -> "G"
 *
 * @param chord {String} string representing a chord, eg. "Ab"
 */
function alterFlatChords(chord) {
    var regex = /([A-G]b)(.*)/;
    var match = regex.exec(chord);
    if (!match)
        return chord;

    var chordBase = match[1];
    var restChord = match[2];

    var map = {'Ab' : 'G#', 'Bb' : 'A#', 'Cb' : 'B', 'Db' : 'C#', 'Eb' : 'F#',
               'Fb' : 'E', 'Gb' : 'F#'};
    var chordBase = map[chordBase];

    return chordBase + restChord;
}

/**
 * Return the given chord, changed by semitonsMove semitons.
 *
 * @param chord {String} string representing a chord, eg. "A#5"
 * @param semitonsMove {Number} integer from -5 to 6
 * @return {String} the changed chord
 */
function changeSemiton(chord, semitonsMove) {
    if (semitonsMove === 0)
        return chord;

    var regex = /([A-G][#b]?)((maj|m|aug|dim|sus)?([245679]|11|13)?)/;
    var match = regex.exec(alterFlatChords(chord));
    var origSemiton = match[1];
    var restChord = match[2];

    var semitons = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    var index = semitons.indexOf(origSemiton) + semitonsMove;

    if (index >= semitons.length)
        index = index % semitons.length;
    else if (index < 0)
        index = semitons.length + index;

    return semitons[index] + restChord;
}

/**
 * Encloses each chord in a span tag of class "chord", and assigns an
 * appropriate image to it. Additionally, it encloses each line containing
 * chords in a div tag of class "chordline" and each line containing tabs
 * in a div tag of class "tabsline".
 *
 * eg. "Am" becomes ->
 * <div class="chordline">
 *     <span class="chord" origchord="Am">
 *         <span class="chordname">Am</span>
 *         <img src="Am.png">
 *     </span>
 * </div>
 */
function parseSong() {
    var content = $('#song_content').html();

    //parse comments
    content = content.replace(/&lt;em&gt;/g, '<em>').replace(/&lt;\/em&gt;/g, '</em>');

    // parse tabs
    var regex = /^[A-Ga-g]\|?[1-9-]{3,}/;
    var lines = content.split('\n');
    var newlines = [];
    for (i = 0; i < lines.length; i++) {
        if (regex.test(lines[i]))
            lines[i] = '<div class="tabsline">' + lines[i] + '</div>';
        else
            lines[i] += '\n'
        newlines.push(lines[i]);
    }

    // parse chords
    lines = newlines;
    var finallines = '';

    for (i = 0; i < lines.length; i++) {
        if (lines[i].indexOf('<div class="tabsline">') != -1) {
            // don't parse tab lines for chords
            finallines += lines[i];
            continue;
        }

        lines[i] = lines[i].replace(
            /([A-G][#b]?(maj|m|aug|dim|sus)?([245679]|11|13)?)/g,
            function($0, $1) {
                return '<span class="chord" origchord="' + $1 +
                    '"><span class="chordname">' + $1 + '</span>' +
                    '<img src="/static/chords/img/chords/' +
                    encodeURIComponent(alterFlatChords($1)) + '.png" alt=""></span>'
            }
        );

        if (lines[i].indexOf('<span class="chord"') != -1)
            finallines += '<div class="chordline">' + lines[i] + '</div>';
        else
            finallines += lines[i];
    }

    $('#song_content').html(finallines);
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

if ($('#song_content').length)
    parseSong();
if ($('#semiton_change').length)
    fillSemitonChange();

});
