from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.template import loader
from django.conf import settings
from .settings import MEDIA_ROOT
from django.core.files.storage import FileSystemStorage
from django.core.files import File
from tempfile import TemporaryFile
from .models import User, Speech, Recording
from .analyzer import Analyzer
import re
from .utils import verify_id_token, get_context
import utils
from oauth2client import crypt

# This class contains view functions that take a Web request
# and returns a Web response. This can be the HTML contents
# of a Web page, error, etc.


def login(request):
    if request.method != 'POST':
        return redirect('index')

    token = request.COOKIES['id_token']
    try:
        idinfo = utils.verify_id_token(token)
    except crypt.AppIdentityError as e:
        return redirect('error')

    user = User.objects.filter(email=idinfo["email"])
    if not user:
        User(name=idinfo["name"], email=idinfo["email"]).save()

    return HttpResponse("OK")


def upload(request):
    if request.method != 'POST':
        return redirect('index')

    # create a temp file to store the blob
    tempfile = TemporaryFile()
    tempfile.write(request.body)
    file = File(tempfile)
    # save the file
    fs = FileSystemStorage()
    filename = fs.save("testfile.wav", file)
    uploaded_file_url = MEDIA_ROOT + "/" + filename
    tempfile.close()

    try:
        token = request.COOKIES['id_token']
        try:
            idinfo = utils.verify_id_token(token)
        except crypt.AppIdentityError as e:
            return redirect('error')
        users = User.objects.filter(email=idinfo['email'])
        if users:
            user = users[0]
    except KeyError:
        user = User(name="temp", email="temp")
        user.save()
    # create speech and recording
    num_speeches = len(Speech.objects.filter(user=user))
    speech_name = "speech" + str(num_speeches + 1)
    speech = Speech(name=speech_name, user=user)
    speech.save()
    try:
        recording = Recording.create(
            audio_dir=uploaded_file_url, speech=speech)
        recording.save()
    except Exception as e:
        # Delete empty speech if anything goes wrong
        speech.delete()
        return redirect('error')
    return HttpResponse(str(recording.id))


def index(request):
    template = loader.get_template('coach/index.html')

    try:
        token = request.COOKIES['id_token']
    except KeyError:
        return HttpResponse(template.render({}, request))
    try:
        context = utils.get_context(token)
    except crypt.AppIdentityError as e:
        return redirect('error')
    return HttpResponse(template.render(context, request))


def error(request):
    template = loader.get_template('coach/error.html')
    return HttpResponse(template.render({}, request))


def profile(request):
    template = loader.get_template('coach/profile.html')

    try:
        token = request.COOKIES['id_token']
        try:
            idinfo = utils.verify_id_token(token)
        except crypt.AppIdentityError as e:
            return redirect('error')
        users = User.objects.filter(email=idinfo['email'])
        if users:
            user = users[0]
        else:
            return redirect('index')
    except KeyError:
        return redirect('index')
    try:
        context = utils.get_context(token)
    except crypt.AppIdentityError as e:
        return redirect('error')
    context['user'] = user
    context['tones'] = user.get_avg_tone()
    return HttpResponse(template.render(context, request))


def result(request):
    # If there is no id_token, user is not logged in, so redirect to index
    try:
        token = request.COOKIES['id_token']
    except KeyError:
        return redirect('index')

    # If the id_token is invalid, return error
    try:
        idinfo = utils.verify_id_token(token)
    except crypt.AppIdentityError as e:
        return redirect('error')

    # If the user doesn't exist in the database, return error
    users = User.objects.filter(email=idinfo['email'])
    if users:
        user = users[0]
    else:
        return redirect('error')

    # If no recording id was provided as url parameter, return error
    rec_id = request.GET.get('rid', '')
    if not rec_id:
        return redirect('error')

    if rec_id == "-1":
        return redirect('error')

    # Check that current user has access to the requested recording, and that
    # the recording exists. Otherwise return error.
    valid_recs = Recording.objects.filter(speech__user=user, id=rec_id)
    if not valid_recs:
        return redirect('error')
    rec = valid_recs[0]

    # Populate context with sidebar data, transcript text and avg pace
    context = get_context(token)
    try:
        context = utils.get_context(token)
    except crypt.AppIdentityError as e:
        return redirect('error')

    transcript = "".join(rec.get_transcript_text())
    context['transcript'] = transcript
    context['pace'] = rec.get_avg_pace()
    context['pauses'] = rec.pauses

    analyzed_sentences = []
    tone_analysis = rec.get_analysis()
    for analysis_segment in tone_analysis:
        print analysis_segment
        analyzed_sentences.append((" ".join(transcript.split()[analysis_segment[0]:analysis_segment[1]]),
                                   analysis_segment[2][
                                       'Group11'].encode('utf-8'),
                                   analysis_segment[2][
                                       'Composite1'].encode('utf-8'),
                                   analysis_segment[2]['Composite2'].encode('utf-8')))
    context['analyzed_sentences'] = analyzed_sentences

    most_frequent_words = Analyzer.get_word_frequency(
        rec.get_transcript_text(), 5)
    most_frequent_words_escaped = []
    for word in most_frequent_words:
        most_frequent_words_escaped.append(word + (re.escape(word[0]),))

    context['most_frequent_words'] = most_frequent_words_escaped

    context['file_name'] = rec.audio_dir[(rec.audio_dir.find('media') - 1):]
    context['recording'] = rec

    template = loader.get_template('coach/results.html')
    return HttpResponse(template.render(context, request))


def userdocs(request):
    template = loader.get_template('coach/userdocs.html')
    try:
        token = request.COOKIES['id_token']
    except KeyError:
        return HttpResponse(template.render({}, request))
    try:
        context = utils.get_context(token)
    except crypt.AppIdentityError as e:
        return redirect('error')
    return HttpResponse(template.render(context, request))
