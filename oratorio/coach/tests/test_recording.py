from django.test import TestCase
from ..models import Recording, User, Speech

class RecordingTestCase(TestCase):
    """Tests for the Recording class in models.py"""

    def setup(self):
        """Sets up the database for the with a user and speech to which the recording is added"""
        user = User(name="TestUser", email="test@test.test")
        user.save()
        speech = Speech(user=user, name="Speech1")
        speech.save()

    def test_create(self):
        """Tests the creation of a recording"""
        self.setup()
        audio_dir = "dummy/dir"
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(
            speech=speech, audio_dir=audio_dir, transcript=[])
        self.assertNotEquals(recording, None)
        self.assertEquals(audio_dir, recording.audio_dir)

    def test_get_transcript_text(self):
        """Tests the get_transcript_text method"""
        self.setup()
        audio_dir = "dummy/dir"
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(speech=speech, audio_dir=audio_dir, transcript=[
            ("Hi I am a test", [], 0.92),
            ("Hi I am a test too", [], 0.95)
        ])
        transcript_text = recording.get_transcript_text()
        self.assertEquals(transcript_text.strip(),
                          "Hi I am a test. Hi I am a test too.")

    def test_get_word_count(self):
        """Tests the get_word_count method"""
        self.setup()
        audio_dir = "dummy/dir"
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(speech=speech, audio_dir=audio_dir, transcript=[
            ("Hi I am test", [("Hi", 0, 1), ("I", 1, 2),
                              ("am", 2, 3), ("test", 3, 4)], 0.92),
            ("Hi I am test", [("Hi", 0, 1), ("I", 1, 2),
                              ("am", 2, 3), ("test", 3, 4)], 0.95)
        ])
        word_count = recording.get_word_count()
        self.assertEquals(word_count, 8)

    def test_get_recording_length(self):
        """Tests the get_recording_length method"""
        self.setup()
        audio_dir = "dummy/dir"
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(speech=speech, audio_dir=audio_dir, transcript=[
            ("Hi I am test", [("Hi", 0, 1), ("I", 1, 2),
                              ("am", 2, 3), ("test", 3, 4)], 0.92),
            ("Hi I am test", [("Hi", 5, 6), ("I", 6, 7),
                              ("am", 7, 8), ("test", 8, 9)], 0.95)
        ])
        audio_length = recording.get_recording_length()
        self.assertEquals(audio_length, 9)

    def test_get_avg_pace(self):
        """Tests the get_avg_pace method"""
        self.setup()
        audio_dir = "dummy/dir"
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(speech=speech, audio_dir=audio_dir, transcript=[
            ("Hi I am test", [("Hi", 0, 1), ("I", 1, 2),
                              ("am", 2, 3), ("test", 3, 4)], 0.92),
            ("Hi I am test", [("Hi", 5, 6), ("I", 6, 7),
                              ("am", 7, 8), ("test", 8, 9)], 0.95)
        ])
        self.assertAlmostEqual(recording.get_avg_pace(), 53, delta=0.4)

    def test_get_tone(self):
        """Tests the get_tone method"""
        self.setup()
        audio_dir = "dummy/dir"
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(speech=speech, audio_dir=audio_dir, transcript=[
            ("Hi I am test", [("Hi", 0, 1), ("I", 1, 2),
                              ("am", 2, 3), ("test", 3, 4)], 0.92),
            ("Hi I am test", [("Hi", 5, 6), ("I", 6, 7),
                              ("am", 7, 8), ("test", 8, 9)], 0.95)
        ])
        recording.joy = 10
        recording.sadness = 20
        recording.anger = 30
        recording.fear = 40
        self.assertEquals(recording.get_tone(), 'fear');
        recording.anger = 50
        self.assertEquals(recording.get_tone(), 'anger');
        recording.sadness = 60
        self.assertEquals(recording.get_tone(), 'sadness');
        recording.joy = 70
        self.assertEquals(recording.get_tone(), 'joy');
        recording.disgust = 75
        self.assertEquals(recording.get_tone(), 'disgust');
        recording.confident = 76
        self.assertEquals(recording.get_tone(), 'confident');


    def test_empty_recording(self):
        """Tests all recording methods on an empty speech. This would be the object returned by Watson if the user does
        not say anything"""
        self.setup()
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(speech, "dummy/dir", [])
        self.assertEquals(recording.get_word_count(), 0)
        self.assertEquals(recording.get_transcript_text(), "")
        self.assertEquals(recording.get_recording_length(), 0)
        self.assertEquals(recording.get_avg_pace(), 0)

    def test_get_json_transcript(self):
        """Tests that the transcript is loaded from the database and converted from a json into a python dictionary
        correctly"""
        self.setup()
        audio_dir = "dummy/dir"
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(speech=speech, audio_dir=audio_dir, transcript=[
            ("Hi I am test", [("Hi", 0, 1), ("I", 1, 2),
                              ("am", 2, 3), ("test", 3, 4)], 0.92),
            ("Hi I am test", [("Hi", 5, 6), ("I", 6, 7),
                              ("am", 7, 8), ("test", 8, 9)], 0.95)
        ])
        self.assertEquals(recording.get_transcript(), [
            ["Hi I am test", [["Hi", 0, 1], ["I", 1, 2],
                              ["am", 2, 3], ["test", 3, 4]], 0.92],
            ["Hi I am test", [["Hi", 5, 6], ["I", 6, 7],
                              ["am", 7, 8], ["test", 8, 9]], 0.95]
        ])
