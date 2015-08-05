from django.shortcuts import render

# Create your views here.
def index(request):
    context = {'hello_msg' : 'This is the index page'}
    return render(request, 'chords/index.html', context)
