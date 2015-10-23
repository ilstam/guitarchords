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

/**
 * Perform an AJAX request to bookmark or unbookmark a song.
 */
$('#bookmark').click(function(event) {
    event.preventDefault();
    var url = $(this).attr('href');
    if ($(this).text().indexOf('Add') != -1)
        $.get(url + 'add_bookmark/', function(data) {
            $('#bookmark').text('(-) Remove from bookmarks')
        })
    else
        $.get(url + 'remove_bookmark/', function(data) {
            $('#bookmark').text('(+) Add to bookmarks')
        })
});

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
 * Replace html escaped <em> tags by real <em> tags.
 *
 * @param song {String} the whole song string
 * @return {String} parsed song
 */
function parseComments(song) {
    return song.replace(/&lt;em&gt;/g, '<em>').replace(/&lt;\/em&gt;/g, '</em>');
}

/**
 * Checks wether a song line contain tablatures.
 *
 * @param line {String} a song line
 * @return {Boolean}
 */
function isTabLine(line) {
    var regex = /^[A-Ga-g]:*\|{0,2}.*-.*-.*-.*-/;
    if (regex.test(line))
            return true;
    return false;
}

/**
 * Encloses each line of the given song string containing tabs, in a div tag
 * of class "tabsline".
 *
 * @param song {String} the whole song string
 * @return {Array of Strings} the parsed lines
 */
function parseTabs(song) {
    var lines = song.split('\n');
    var newlines = [];

    for (i = 0; i < lines.length; i++) {
        if (isTabLine(lines[i]))
            lines[i] = '<div class="tabsline">' + lines[i] + '</div>';
        else
            lines[i] += '\n'
        newlines.push(lines[i]);
    }

    return newlines;
}

/**
 * In the given song, encloses each chord in a span tag of class "chord",
 * and assigns an appropriate image to it. Additionally, it encloses each line
 * containing chords in a div tag of class "chordline".
 *
 * eg. "Am" becomes ->
 * <div class="chordline">
 *     <span class="chord" origchord="Am">
 *         <span class="chordname">Am</span>
 *         <img src="Am.png">
 *     </span>
 * </div>
 *
 * @param lines {Array of Strings} the initial song lines
 * @return {Array of Strings} the parsed lines
 */
function parseChords(lines) {
    var newlines = '';

    for (i = 0; i < lines.length; i++) {
        // Do not parse tab lines.
        if (lines[i].indexOf('<div class="tabsline">') != -1) {
            newlines += lines[i];
            continue;
        }

        // Enclose chords in span tags of class "chords".
        lines[i] = lines[i].replace(
            /([A-G][#b]?(maj|m|aug|dim|sus|add)?([245679]|11|13)?[#b]?([245679]|11|13)?)/g,
            function($0, $1) {
                return '<span class="chord" origchord="' + $1 +
                    '"><span class="chordname">' + $1 + '</span>' +
                    '<img src="/static/chords/img/chords/' +
                    encodeURIComponent(alterFlatChords($1)) + '.png" alt=""></span>'
            }
        );

        // Enclose chords lines in div tags of class "chordline".
        if (lines[i].indexOf('<span class="chord"') != -1) {
            var stripped = lines[i].replace(/<span class="chord".+<\/span>/g, '');
            var match = /[^\s\(\)\/\|x\d]/.exec(stripped)
            // Is it really a chord or does it simply look like one?
            if (!match)
                lines[i] = '<div class="chordline">' + lines[i] + '</div>';
            else
                // Remove span tags from "false" chords.
                lines[i] = lines[i].replace(/<span class="chord" origchord="(.+?)">.+?<img.+?<\/span>/g, '$1');
        }
        newlines += lines[i];
    }

    return newlines;
}

function parseSong() {
    var song = $('#song_content');
    song.html(parseChords(parseTabs(parseComments(song.html()))));
}

/**
 * Fills the semiton_change select object, with the values from -5 to 6
 * followed by the base chord of the song at the specific semiton.
 *
 * eg. -1 (D), 0 (D#), +1 (E)
 */
function fillSemitonChange() {
    var songBase = $('.chord').first().attr('origchord');
    if (! songBase)
        return;
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
