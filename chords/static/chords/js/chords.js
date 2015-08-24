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
        '<span class="chord">$1<img src="http://placehold.it/100x120"></span>'
    );

    var lines = result.split('\n');
    var newlines = "";

    for (i = 0; i < lines.length; i++) {
        if (lines[i].indexOf('<span class="chord">') != -1)
            newlines += '<div class="chordline">' + lines[i] + '</div>';
        else
            newlines += lines[i] + "\n";
    }
    content.html(newlines);
}

$(parseSong)
