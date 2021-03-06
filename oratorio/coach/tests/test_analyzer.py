from ..models import Speech, Recording, User
from .. import analyzer
from ..analyzer import Analyzer
from django.test import TestCase
from mock import Mock, MagicMock
import requests

class AnalyzerTestCase(TestCase):
    """Tests for the Analyzer class in analyzer.py"""

    # Tests for getting transcript
    def test_get_transcript_json(self):
        """Tests the get_transcript_json works correctly when IBM Watson's SpeechToText analyzer mocked out"""
        mock_stt = Mock()
        mock_stt.recognize = Mock(return_value={'results': "mock result"})
        analyzer.SPEECH_TO_TEXT = mock_stt
        self.assertEquals(Analyzer.get_transcript_json("dumy-file", mock_stt), "mock result")

    def test_clean_transcript(self):
        """Test the clean_transcript method"""
        test_transcript = [
            {
                'alternatives': [
                    {
                        'timestamps': [
                            [
                                'this',
                                0,
                                1
                            ],
                            [
                                'is',
                                1,
                                2
                            ]
                        ],
                        'confidence': 0.664,
                        'transcript': 'this is'
                    }
                ],
                'final': True
            },
            {
                'alternatives': [
                    {
                        'timestamps': [
                            [
                                'a',
                                2,
                                3
                            ],
                            [
                                'test',
                                3,
                                4
                            ]
                        ],
                        'confidence': 0.664,
                        'transcript': 'a test'
                    }
                ],
                'final': True
            }
        ]
        self.assertEquals(Analyzer.clean_transcript(test_transcript), [
            ('this is', [['this', 0, 1], ['is', 1, 2]], 0.664),
            ('a test', [['a', 2, 3], ['test', 3, 4]], 0.664)
        ])

    def test_clean_hesitations(self):
        """Test the clean_transcript method"""
        test_transcript = [
            {
                'alternatives': [
                    {
                        'timestamps': [
                            [
                                'this',
                                0,
                                1
                            ],
                            [
                                'is',
                                1,
                                2
                            ]
                        ],
                        'confidence': 0.664,
                        'transcript': 'this is'
                    }
                ],
                'final': True
            },
            {
                'alternatives': [
                    {
                        'timestamps': [
                            [
                                '%HESITATION',
                                2,
                                3
                            ],
                            [
                                'a',
                                3,
                                4
                            ],
                            [
                                'test',
                                4,
                                5
                            ]
                        ],
                        'confidence': 0.664,
                        'transcript': '%HESITATION a test'
                    }
                ],
                'final': True
            }
        ]
        self.assertEquals(Analyzer.clean_transcript(test_transcript), [
            ('this is', [['this', 0, 1], ['is', 1, 2]], 0.664),
            ('a test', [['a', 3, 4], ['test', 4, 5]], 0.664)
        ])


    def setup(self):
        """Sets up the database for the analyzer"""
        user = User(name="TestUser", email="test@test.test")
        user.save()
        speech = Speech(user=user, name="Speech1")
        speech.save()

    # The following tests test the analysis of the most frequently used words

    def test_get_5_most_frequent_words(self):
        """tests that only the 5 most frequent words are returned"""
        self.setup()
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(speech, "dummy/dir", transcript=[
            (
            "Hiss ab Hiss Ix Hiss", [("Hiss", 0, 1), ("ab", 1, 2), ("Hiss", 2, 3), ("Ix", 3, 4), ("Hiss", 4, 5)], 0.92),
            ("Ix Ix Ix Hiss", [("Ix", 5, 6), ("Ix", 6, 7), ("Ix", 7, 8), ("Hiss", 8, 9)], 0.95),
            ("mam mam test", [("mam", 9, 10), ("mam", 10, 11), ("test", 12, 13)], 0.95),
            ("ab Hiss", [("ab", 13, 14), ("Hiss", 15, 16), ], 0.95),
            ("mam test", [("mam", 13, 14), ("test", 14, 15)], 0.95),
            ("xxx", [("xxx", 15, 16)], 0.95)
        ])
        frequent_words = Analyzer.get_word_frequency(recording.get_transcript_text(), 5)
        self.assertEquals(len(frequent_words), 5)
        self.assertEquals(frequent_words[0], ("hiss", 5))
        self.assertEquals(frequent_words[1], ("ix", 4))
        self.assertEquals(frequent_words[2], ("mam", 3))
        self.assertEquals(frequent_words[3], ("ab", 2))
        self.assertEquals(frequent_words[4], ("test", 2))
        self.assertNotIn("xxx", [item[0] for item in frequent_words])

    def test_get_most_frequent_words_less_than_5(self):
        """tests that if the transcript contains less than 5 words then only these are added"""
        self.setup()
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(speech, "dummy/dir", transcript=[
            (
            "Hiss ab Hiss Ix Hiss", [("Hiss", 0, 1), ("ab", 1, 2), ("Hiss", 2, 3), ("Ix", 3, 4), ("Hiss", 4, 5)], 0.92),
        ])
        frequent_words = Analyzer.get_word_frequency(recording.get_transcript_text(), 5)
        self.assertEquals(len(frequent_words), 3)
        self.assertEquals(frequent_words[0], ("hiss", 3))
        self.assertEquals(frequent_words[1], ("ix", 1))
        self.assertEquals(frequent_words[2], ("ab", 1))

    def test_stop_words(self):
        """tests that the stop words are not counted and do not effect the counting of other words"""
        self.setup()
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(speech, "dummy/dir", transcript=[])
        frequent_words = Analyzer.get_word_frequency(recording.get_transcript_text(), 5)
        self.assertEquals(frequent_words, [])

    def test_get_frequency_empty_transcript(self):
        self.setup()
        speech = Speech.objects.get(name="Speech1")

    # The following tests, test the analysis of pauses in a speech.
    # The threshold for a pause in our system is 1.5 (ie if a pause >= 1.5s it is counted as a pause)

    def test_no_pauses(self):
        """tests a speech which has a pause that is just under the threshold"""
        self.setup()
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(speech, "dummy/dir", transcript=[
            ("I am his her", [("I", 0, 1), ("am", 1, 2), ("his", 2, 3), ("her", 4.49999999, 4)], 0.92),
        ])
        pauses = Analyzer.get_pauses(recording.get_transcript())
        self.assertEquals(pauses[1], 0)
        self.assertEquals(pauses[0], [0] * 3)

    def test_pause(self):
        """tests a speech which has a pause that is just at the threshold"""
        self.setup()
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(speech, "dummy/dir", transcript=[
            ("I am his her", [("I", 0, 1), ("am", 1, 2), ("his", 2, 3), ("her", 4.5, 5)], 0.92),
        ])
        pauses = Analyzer.get_pauses(recording.get_transcript())
        self.assertEquals(pauses[1], 1)
        self.assertEquals(pauses[0], [0, 0, 1])

    def test_bounds(self):
        """tests that pauses are counted correctly at the beginning and ends of speeches"""
        self.setup()
        speech = Speech.objects.get(name="Speech1")
        # with pauses at beginning and end
        recording = Recording.create(speech, "dummy/dir", transcript=[
            ("I am his her", [("I", 0, 1), ("am", 2.5, 3), ("his", 3, 4), ("her", 5.5, 6)], 0.92),
        ])
        pauses = Analyzer.get_pauses(recording.get_transcript())
        self.assertEquals(pauses[1], 2)
        self.assertEquals(pauses[0], [1, 0, 1])
        # without pauses at beginning and end
        recording = Recording.create(speech, "dummy/dir", transcript=[
            ("I am his her", [("I", 0, 1), ("am", 2.49999999, 3), ("his", 3, 4), ("her", 5.49999999, 6)], 0.92),
        ])
        pauses = Analyzer.get_pauses(recording.get_transcript())
        self.assertEquals(pauses[1], 0)
        self.assertEquals(pauses[0], [0] * 3)

    def test_multisentence_speech(self):
        """checks that pauses are counted correctly across multiple sentences (even when a pause occurs across a sentence)"""
        self.setup()
        speech = Speech.objects.get(name="Speech1")
        recording = Recording.create(speech, "dummy/dir", transcript=[
            ("I am his her", [("I", 0, 1), ("am", 2.5, 3), ("his", 4.5, 4), ("her", 5.5, 6)], 0.92),
            ("I am a", [("I", 7.5, 8), ("am", 9, 10), ("a", 11.5, 12)], 0.12),
        ])
        pauses = Analyzer.get_pauses(recording.get_transcript())
        self.assertEquals(pauses[1], 5)
        self.assertEquals(pauses[0], [1, 1, 1, 1, 0, 1])
        recording = Recording.create(speech, "dummy/dir", transcript=[
            ("I am his her", [("I", 0, 1), ("am", 2.5, 3), ("his", 4.5, 4), ("her", 5.5, 6)], 0.92),
            ("I am a", [("I", 7.4999999, 8), ("am", 9, 10), ("a", 11.5, 12)], 0.12),
        ])
        pauses = Analyzer.get_pauses(recording.get_transcript())
        self.assertEquals(pauses[1], 4)
        self.assertEquals(pauses[0], [1, 1, 1, 0, 0, 1])

    def test_emotion_analyzer_joy(self):
        mock_tone = Mock()
        mock_tone.tone = Mock(return_value={"document_tone" : {"tone_categories" : [
            {'tones': [
                {"tone_name": "Anger","score": 0.1, "tone_id": "anger"},
                {"tone_name": "Disgust","score": 0.2, "tone_id": "disgust"},
                {"tone_name": "Fear", "score": 0.3, "tone_id": "fear"},
                {"tone_name": "Joy", "score": 0.4, "tone_id": "joy"},
                {"tone_name": "Sadness", "score": 0.5, "tone_id": "sadness"},
                       ]},
            {'tones': [
                {"tone_name": "Analytical", "score": 0.6, "tone_id": "analytical"},
                {"tone_name": "Confident", "score": 0.6, "tone_id": "confident"},
                {"tone_name": "Tentative", "score": 0.6, "tone_id": "tentative"}
            ]}
        ]}})
        tone_dictionary = Analyzer.get_emotion("I am a test", mock_tone)
        self.assertEquals(len(tone_dictionary), 8)
        self.assertEqual(tone_dictionary['anger'], 10)
        self.assertEqual(tone_dictionary['disgust'], 20)
        self.assertEqual(tone_dictionary['fear'], 30)
        self.assertEqual(tone_dictionary['joy'], 40)
        self.assertEqual(tone_dictionary['sadness'], 50)
        self.assertEqual(tone_dictionary['confident'], 60)

    def test_get_tone_analysis_json(self):
        """Tests get_tone_analysis_json"""
        mock_response = Mock()
        mock_response.json = Mock(return_value={
            "access_token" : "abc123",
            "recordingId" : "123",
            "result" : {"analysisSegments" : "test result"}
        })
        mock_response.status_code = 200
        requests.post = MagicMock(return_value=mock_response)

        result = Analyzer.get_tone_analysis_json("dummy-dir", mock_response)
        self.assertEquals(result, "test result")

    def test_get_tone_analysis_json_empty(self):
        """Tests get_tone_analysis_json"""
        mock_response = Mock()
        mock_response.json = Mock(return_value={
            "access_token": "abc123",
            "recordingId": "123",
            "result": {"analysisSegments": "test result"}
        })
        mock_response.status_code = 400
        requests.post = MagicMock(return_value=mock_response)

        result = Analyzer.get_tone_analysis_json("dummy-dir", mock_response)
        self.assertEquals(result, [])

    def test_clean_tone_analysis_empty(self):
        self.assertEquals(Analyzer.clean_tone_analysis([], "test transcript"), [])

    def test_clean_tone_analysis(self):
        test_result = [(0, 2, {'Group11': 'Sadness, Sorrow', 'Composite2': 'Dreams and fear of unfulfilled aspirations.', 'Arousal': '57.76', 'Composite1':'Fear under control. Possibly hidden despair.', 'Valence': '35.83', 'Temper': '22.81'})]
        test_param = [{'duration': 13080, 'analysis': {'Mood': {'Group11': {'Primary': {'Phrase': 'Sadness, Sorrow'
        }}, 'Composite': {'Primary': {'Phrase': 'Fear under control. Possibly hidden despair.'},
                         'Secondary': {'Phrase': 'Dreams and fear of unfulfilled aspirations.'}}},
                         'Arousal': {'Group': 'neutral', 'Value': '57.76'}, 'Valence': {'Group': 'neutral', 'Value': '35.83'}, 'Temper': {'Group': 'low', 'Value': '22.81',
                         }}, 'offset': 786}]
        transcript = [('this is a', [['this', 0, 2], ['is', 4, 6], ['a', 7, 10], ['test', 10, 13]], 0.664)]
        result = Analyzer.clean_tone_analysis(test_param,transcript)
        print result
        self.assertEquals(result, test_result)
