from django.test import TestCase
from ..models import Recording, User, Speech

class UserTestCase(TestCase):
    """Tests for the User class in models.py"""

    def setup(self):
        """Sets up test database with a user with two speeches, each with one recording"""
        self.user = User(name="TestUser", email="test@test.test")
        self.user.save()
        audio_dir = "dummy/dir"
        speech1 = Speech(user=self.user, name="Speech1")
        speech1.save()
        speech2 = Speech(user=self.user, name="Speech2")
        speech2.save()
        rec1 = Recording.create(speech=speech1, audio_dir=audio_dir, transcript=[
            ("Hi I am rec1", [("Hi", 0, 1), ("I", 3, 4),
                              ("am", 4, 5), ("rec1", 5, 6)], 0.92),
        ])
        rec2 = Recording.create(speech=speech2, audio_dir=audio_dir, transcript=[
            ("Hi I am rec2", [("Hi", 0, 1), ("I", 3, 4),
                              ("am", 4, 5), ("rec2", 7, 8)], 0.92)
        ])
        rec1.joy = 10
        rec1.sadness = 20
        rec1.anger = 30
        rec1.fear = 40
        rec1.disgust = 50
        rec1.confident = 60
        rec2.joy = 20
        rec2.sadness = 30
        rec2.anger = 40
        rec2.fear = 50
        rec2.disgust = 60
        rec2.confident = 70
        rec1.save()
        rec2.save()

    def test_get_avg_pace(self):
        """Tests the get_avg_pace method"""
        self.setup()
        self.assertEqual(self.user.get_avg_pace(), 35)

    def test_get_avg_tone(self):
        """Tests the get_avg_tone method"""
        self.setup()
        res = { 'joy': 15, 'sadness': 25, 'anger': 35, 
                'fear': 45, 'disgust': 55, 'confident': 65 } 
        self.assertEqual(self.user.get_avg_tone(), res)

    def test_get_avg_pauses(self):
        """Tests the get_avg_pauses method"""
        self.setup()
        self.assertEqual(self.user.get_avg_pauses(), 1.5)
