$(function() {

/**
 * Perform an AJAX GET request to get sorted search results.
 */
$('#search_table th a').click(function() {
    var orderByOld = $('#id_orderBy').attr('value');
    var orderBy = $(this).text();

    if (orderBy == 'Name') {
        if (orderByOld == 'nameAsc')
            var orderByNew = 'nameDesc';
        else
            var orderByNew = 'nameAsc';
    } else if (orderBy == 'Artist') {
        if (orderByOld == 'artistAsc')
            var orderByNew = 'artistDesc';
        else
            var orderByNew = 'artistAsc';
    } else if (orderBy == 'Genre') {
        if (orderByOld == 'genreAsc')
            var orderByNew = 'genreDesc';
        else
            var orderByNew = 'genreAsc';
    } else if (orderBy == 'Tabs') {
        if (orderByOld == 'tabsAsc')
            var orderByNew = 'tabsDesc';
        else
            var orderByNew = 'tabsAsc';
    }

    $('#id_orderBy').attr('value', orderByNew);

    url = window.location.href;
    $.get(url, {orderBy : orderByNew}, function(data) {
        $('#search_table tbody').html(data);
    });
});

});
