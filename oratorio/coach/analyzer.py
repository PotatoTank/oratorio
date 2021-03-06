from watson_developer_cloud import SpeechToTextV1, ToneAnalyzerV3
from settings import SPEECH_TO_TEXT_USER_NAME, SPEECH_TO_TEXT_PASSWORD, EMOTION_API_KEY, TONE_ANALYZER_USER_NAME, TONE_ANALYZER_PASSWORD
from collections import Counter
from sets import Set
import requests
import json
import re
import sys

# A pause is considered a pause if it is longer than (THREDSHOLD)s
THRESHOLD = 1.5

# STOP_WORDS will not be counted in the word frequency
STOP_WORDS = Set(["a", "am", "an", "and", "any", "are", "as", "at", "be", \
              "because", "been", "but", "by", "can", "cannot", "could", \
              "did", "do", "does", "every", "for", "from", "get", "got", \
              "had", "has", "have", "he", "her", "hers", "him", "his", \
              "how", "i", "in", "into", "is", "it", "its", "may", "me", \
              "might", "most", "must", "my", "neither", "no", "nor", "not", \
              "of", "off", "on", "or", "other", "our", "own", "she", \
              "should", "so", "some", "than", "that", "the", "their", \
              "them", "then", "there", "they", "this", "tis", "to", "too", \
              "twas", "us", "was", "we", "were", "what", "when", "where", \
              "which", "while", "who", "whom", "why", "will", "with", "would", \
              "you", "your"])

class Analyzer:
    """This class creates recordings and performs the analysis on a recording. It calls Watson's speech to text API to
    get the transcript and BeyondVerbal to get the tone of the speech, counts the frequently used words and pauses"""

    @staticmethod
    def get_transcript_json(audio_file, speech_to_text=None):
        """This method calls the IBM Watson's speech API and returns the json that this produces"""
        if speech_to_text is None:
            speech_to_text = SpeechToTextV1(username=SPEECH_TO_TEXT_USER_NAME, password=SPEECH_TO_TEXT_PASSWORD)
        # This is the call to IBM Watson's Speech to Text API
        # By default IBM Watson's Speech To Text API stops transcribing at the first long pause, setting continuous to
        # true overrides this behaviour. Setting time stamps to true gets the start and end time of each word
        json_transcript = speech_to_text.recognize(audio_file, content_type="audio/wav", continuous=True,
                                                   timestamps=True)
        return json_transcript['results']

    @staticmethod
    def clean_transcript(json_transcript):
        """Takes the json result returned by Watson and converts it into the format that the parameter requires (ie a
        list of sentences (as described above)). This method also removes any alternatives watson may return and only
        retains the alternative with the highest confidence."""
        transcript = []
        for sentence in json_transcript:
            # finalSentence is the sentence with the highest confidence
            # Watson is set up so that this is always the first alternative
            final_sentence = sentence["alternatives"][0]

            # Strip out the %HESITATION words from the data that Watson returns
            found_hesitation = False
            for word in final_sentence["timestamps"]:
                if word[0].startswith("%"):
                    final_sentence["timestamps"].remove(word)
                    found_hesitation = True
            # If a %HESITATION was found, rebuild the full sentence ignoring the %HESITATION
            if found_hesitation:
                sentence_transcript = ""
                for word in final_sentence["timestamps"][:-1]:
                    sentence_transcript += word[0] + " "
                sentence_transcript += final_sentence["timestamps"][-1][0]
                final_sentence["transcript"] = sentence_transcript

            transcript.append((final_sentence["transcript"], final_sentence["timestamps"],
                               final_sentence["confidence"]))
        return transcript


    @staticmethod
    def get_word_frequency(transcript_text, k):
        """Given transcript, returns k of the most frequently used words in transcript. (ignores STOP WORDS)"""
        if not transcript_text:
            return []
        word_frequencies = Counter()
        transcript_text = re.sub("[.]", "", transcript_text.lower().strip())
        for word in re.split("\s+", transcript_text):
            if word not in STOP_WORDS:
                word_frequencies[word] += 1
        return word_frequencies.most_common(k)

    @staticmethod
    def get_emotion(transcript_text, tone_analyzer=None):
        if tone_analyzer is None:
            tone_analyzer = ToneAnalyzerV3(username=TONE_ANALYZER_USER_NAME, password=TONE_ANALYZER_PASSWORD, version='2016-02-11')
        result = tone_analyzer.tone(text=transcript_text)["document_tone"]["tone_categories"]
        emotion_tone_result = result[0]["tones"]
        writing_tone_result = result[1]["tones"]
        tone_dictionary = {}
        for emotion_tone in emotion_tone_result:
            tone_dictionary[emotion_tone["tone_id"]] = int(emotion_tone["score"] * 100)
        for writing_tone in writing_tone_result:
            tone_dictionary[writing_tone["tone_id"]] = int(writing_tone["score"] * 100)
        return tone_dictionary

    @staticmethod
    def get_pauses(transcript):
        """Given transcript (with stop an end times, see Recording in models.py for format), returns the number of pauses
        and where they occur. Eg: If get_pauses(a_transcript) returns ([1, 0, 1, 1, 0], 3) This means that the speech
        has 3 pauses one after the 1st, 3rd and 4th word, there was no pause after words 2 and 5 (and there are 6 words)
        A pause is only counted as a pause if it is longer than the THRESHOLD"""
        start_end_times = []
        pauses = 0

        for list in [item[1] for item in transcript]:
            for item in list:
                start_end_times.append(item[1:]) # we only want start and end times

        pause_list = []

        for i in range(0, len(start_end_times)-1):
            if start_end_times[i+1][0] - start_end_times[i][1] >= THRESHOLD:
                pause_list.append(1)
                pauses += 1
            else:
                pause_list.append(0)

        return (pause_list, pauses)

    @staticmethod
    def get_tone_analysis_json(audio_file, response=None):
        url = "https://token.beyondverbal.com/token"
        headers = {"Content-Type" : "multipart/form-data"}
        data = {"apiKey" : EMOTION_API_KEY,
                "grant_type" : "client_credentials"}
        if response is None:
            response = requests.get(url, headers=headers, data=data)
        access_token = response.json()['access_token']
        authorization = "Bearer " + access_token

        url = "https://apiv3.beyondverbal.com/v3/recording/start"
        headers = {"Authorization" : authorization}

        data = {"dataFormat" : {"type": "WAV"},
                "metadata" : {},
                "displayLang" : "en-us"}

        response = requests.post(url, headers=headers, data=json.dumps(data))
        if (response.status_code == 200):
            url = "https://apiv3.beyondverbal.com/v3/recording/" + response.json()['recordingId']
            headers = {"Authorization" : authorization,
                       'content-type': 'application/json'}
            # data = {"Sample Data" : bytearray(audio_file.read())}
            response = requests.post(url, headers=headers, data=audio_file)
            analysis = response.json()['result'].get('analysisSegments')
            return analysis
        return []

    @staticmethod
    def clean_tone_analysis(tone_analysis, transcript):
        print tone_analysis
        if not tone_analysis:
            return []
        start_end_times = []
        tone_analysis_result = []

        for list in [item[1] for item in transcript]:
            for item in list:
                start_end_times.append(item[1:]) # we only want start and end times

        for x in tone_analysis:
            tone_map = {}
            tone_map["Group11"] = x['analysis']['Mood']['Group11']['Primary']['Phrase']
            tone_map["Composite1"] = x['analysis']['Mood']['Composite']['Primary']['Phrase']
            tone_map["Composite2"] = x['analysis']['Mood']['Composite']['Secondary']['Phrase']
            tone_map["Arousal"] = x['analysis']['Arousal']['Value']
            tone_map["Valence"] = x['analysis']['Valence']['Value']
            tone_map["Temper"] = x['analysis']['Temper']['Value']

            start = float(x['offset']) / 1000
            end = (float(x['offset']) + float(x['duration'])) / 1000

            start_word = 0
            for i in range(len(start_end_times) - 1):
                if start_end_times[i][0] <= start <= start_end_times[i + 1][0]:
                    start_word = i
                if start_end_times[i][0] <= end <= start_end_times[i+1][0] or i == len(start_end_times) - 2:
                    tone_analysis_result.append((start_word, i, tone_map))
                    break
        print tone_analysis_result
        return tone_analysis_result

