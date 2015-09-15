$(function() {

/**
 * Split the list of songs into 3 chunks.
 * Chunks will be of equal size if possible, else the first chunks will have
 * an extra element. Then append these chunks into the appropriate column.
 */
function splitSongsInColumns3() {
    var list = $('#present_songs li');
    var x = Math.ceil(list.length / 3);
    var y = Math.ceil((list.length - x) / 2);

    var l1 = list.slice(0, x);
    var l2 = list.slice(x, x+y);
    var l3 = list.slice(x+y);

    $('#col1 ul').append(l1);
    $('#col2 ul').append(l2);
    $('#col3 ul').append(l3);
}

if ($('#present_songs li').length)
    splitSongsInColumns3();

});
