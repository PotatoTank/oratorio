from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

from django.conf import settings
from .settings import MEDIA_ROOT
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from tempfile import TemporaryFile
from .models import User, Speech, Recording
from .analyzer import Analyzer
import json

def upload(request):
    if request.method == 'POST':
        # create a temp file to store the blob
        tempfile = TemporaryFile()
        tempfile.write(request.body)
        file = File(tempfile)
        # save the file
        fs = FileSystemStorage()
        filename = fs.save("testfile.wav", file)
        uploaded_file_url = MEDIA_ROOT + "/" + filename
        tempfile.close()
        user = User.objects.filter(name="Joey")[0]
        num_speeches = len(Speech.objects.all())
        speech_name = "speech" + str(num_speeches + 1)
        speech = Speech(user=user, name=speech_name)
        speech.save()
        recording = Analyzer.create_recording(audio_dir=uploaded_file_url, speech=speech)
        recording.save()
        print json.dumps(recording.transcript)
        template = loader.get_template('coach/results.html')
        context = { 'transcript': recording.get_transcript_text(), }
        return HttpResponse(template.render(context, request))
    return redirect('index')

def index(request):
    template = loader.get_template('coach/index.html')
    context = {}
    return HttpResponse(template.render(context, request))

def profile(request):
    template = loader.get_template('coach/profile.html')
    context = {}
    return HttpResponse(template.render(context, request))

def result(request):
    template = loader.get_template('coach/results.html')
    context = {}
    return HttpResponse(template.render(context, request))

def userdocs(request):
    template = loader.get_template('coach/userdocs.html')
    context = {}
    return HttpResponse(template.render(context, request))
