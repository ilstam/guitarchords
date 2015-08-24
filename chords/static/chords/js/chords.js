$('#song_content').on('mouseover', '.chord', function() {
    $(this).children('img').css('visibility', 'visible');
})

$('#song_content').on('mouseout', '.chord', function() {
    $(this).children('img').css('visibility', 'hidden');
})


/**
 * Each chord matching the following regex should be enclosed in a span tag
 * of class "chord", and an appropriate image must be assigned to it.
 */
function parseSong() {
    var content = $("#song_content");
    content.html(content.html().replace(
        /([A-G][#b]?(maj|m|aug|dim|sus)?[245679]?)/g,
        '<span class="chord">$1<img src="http://placehold.it/100x120"></span>')
    );
}

$(parseSong)
