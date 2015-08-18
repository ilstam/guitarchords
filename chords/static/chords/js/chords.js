$('.chord').mouseover(function() {
	$(this).children('img').css('visibility', 'visible');
});

$('.chord').mouseout(function() {
	$(this).children('img').css('visibility', 'hidden');
});
