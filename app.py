import json
from helper import solr_insert, solr_full_import
from flask import Flask, render_template, request
import openai
from serpapi import GoogleSearch
from gtts import gTTS
import base64
import requests
from googletrans import Translator
import threading
from scipy.io.wavfile import write
from werkzeug.utils import secure_filename
from apiclient import discovery
import pydub
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import datetime
import time
import filetype
import os
from google.cloud import texttospeech, texttospeech_v1, translate_v2
from pymongo import MongoClient
import settings
from flask import Flask
from flask_crontab import Crontab
from flask import jsonify, abort
from bson import ObjectId

# from middleware import middleware


MONGO_DB_CONNECTION_STRING = ''


def get_connection():
    client = MongoClient(MONGO_DB_CONNECTION_STRING)
    collection = client['upajmitra']['content']
    return collection


app = Flask(__name__)
crontab = Crontab(app)

UPLOAD_FOLDER = "./"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.credential_path


#
# # calling the middleware
# app.wsgi_app = middleware(app.wsgi_app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/send', methods=['POST'])
def send_msg():
    try:
        if request.method == 'POST':
            text = request.json.get('query', None)
            tags = request.json.get('tags', None)
            language = request.json.get('language', 'en')
            response_data = check_from_solr(text, language, tags)
            if len(response_data['result']) != 0:
                response_data["source"] = "solr"
                print('solr')
                return jsonify(response_data), 200
            response_data = response_dataset(text, method='text', tags=tags)
            print('gpt')
            return jsonify(response_data), 200
    except Exception as e:
        print(str(e))
        return {"error": True, "message": str(e)}, 200


@app.route('/sendVoice', methods=('GET', 'POST'))
def get_voice_result():
    if request.method == 'POST':
        file = request.files['data']
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.seek(0)
        file.save(filepath)
        filepath = convert_ogg_to_mp3(filepath, filetype.guess(file).extension)
        openai.api_key = settings.open_ai_key
        file = open(filepath, "rb")
        transcription = openai.Audio.transcribe("whisper-1", file)
        text = transcription['text']
        tags = request.json.get('tags', None)
        language = request.json.get('language', 'en')
        original_text = text
        dym_response = None
        response_data = check_from_solr(text, language, tags)
        if len(response_data['result']) != 0:
            response_data["source"] = "solr"
            print('solr')
            return jsonify(response_data), 200
        response_data = response_dataset(text, method='voice', tags=tags)
        return jsonify(response_data), 200


@app.route('/translatemsg', methods=('GET', 'POST'))
def translate_msg():
    combined_result = {}
    quest = request.json.get('query', None)
    tags = request.json.get('tags', None)
    ans = request.json.get('data', None)
    language = request.json.get('language', "en")
    translation_client = translate_v2.Client()
    quest_result = translation_client.translate(quest, target_language=language)
    trans_quest = quest_result['translatedText']
    response_data = check_from_solr(quest, language, temp_tags=None)
    if len(response_data['result']) != 0:
        response_data["source"] = "solr"
        print('solr')
        return jsonify(response_data), 200

    ans_result = translation_client.translate(ans, target_language=language)
    trans_ans = ans_result['translatedText']
    response_video = get_videos(trans_quest, combined_result)
    videos = response_video['videos']
    response = get_audio(trans_ans, language)
    enc = base64.b64encode(response.audio_content)
    enc = enc.decode('utf-8')
    return {"data": trans_ans, "audio": enc.decode(), "videos": videos, "source": "chatgpt",
            "tags": tags, "error": False, "message": None}, 200


def convert_ogg_to_mp3(ogg_filepath, extension):
    mp3_filepath = os.path.join(app.config["UPLOAD_FOLDER"], "test" + ".mp3")
    audio = pydub.AudioSegment.from_file(ogg_filepath, format=extension)
    audio.export(mp3_filepath, format="mp3")
    return mp3_filepath


def get_images(text, combined_result):
    sec_key = settings.image_sec_key
    google_params = {
        "q": text,
        "tbm": "isch",
        "ijn": "0",
        "api_key": sec_key
    }

    google_search = GoogleSearch(google_params)

    i = 1
    link_list = []
    result = google_search.get_dict()
    if 'images_results' in result:
        for image_result in result['images_results']:
            if i < 7:
                link = image_result["original"]
                try:
                    link_list.append({f'Image_{i}': link})
                except:
                    pass
                i += 1
    combined_result['images'] = link_list


def get_resp(text, combined_result, source):
    openai.api_key = settings.open_ai_key
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user",
                   "content": text + ". Please provide answer only if the question is related to agriculture, food, pests, diseases and commodities for Indian context, otherwise prompt the user to ask questions only related to it"}]
    )
    text = completion['choices'][0]['message']['content']
    translation_client = translate_v2.Client()
    final_text = translation_client.translate(str(text), target_language=str(source))
    combined_result['text'] = final_text['translatedText']


def get_audio(resp, source):
    client = texttospeech_v1.TextToSpeechClient()
    synthesis_input = texttospeech_v1.SynthesisInput(text=resp)

    voice = texttospeech_v1.VoiceSelectionParams(language_code=source + "-IN",
                                                 ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech_v1.AudioConfig(audio_encoding=texttospeech_v1.AudioEncoding.MP3)
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    return response


def get_videos(text, combined_result):
    try:
        yt_key = settings.youtube_key
        youtube = discovery.build('youtube', 'v3', developerKey=yt_key)

        req = youtube.search().list(q=text, part='snippet', type='video')
        result = req.execute()
        vid_list = []
        for i in result['items']:
            vid_list.append(f"https://www.youtube.com/embed/{i['id']['videoId']}")
        combined_result['videos'] = vid_list
        return combined_result
    except:
        return None


def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text.lower())
    # Remove stop words
    filtered_tokens = [token for token in tokens if token not in stopwords.words('english')]
    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    # Join the tokens back into a string
    processed_text = ' '.join(lemmatized_tokens)
    return processed_text


def response_dataset(text, method, tags):
    original_text = text
    combined_result = {}
    source = 'en'
    try:
        translation_client = translate_v2.Client()
        result = translation_client.translate(text, target_language='en')
        text = result['translatedText']
        source = result['detectedSourceLanguage']
    except Exception as e:
        pass
    # t1 = threading.Thread(target=getImages, args=(text, combined_result))
    t2 = threading.Thread(target=get_resp, args=(original_text, combined_result, source))
    t3 = threading.Thread(target=get_videos, args=(text, combined_result))

    # t1.start()
    t2.start()
    t3.start()

    # t1.join()
    t2.join()
    t3.join()
    response_data = {"count": 1, "error": False, "message": None, "result": []}
    info = {}
    resp = combined_result['text']
    info["data"] = resp
    info["videos"] = combined_result['videos']
    response = get_audio(resp, source)
    audio = base64.b64encode(response.audio_content)
    info["audio"] = audio.decode('utf-8')
    data = {"question": original_text, "question_en": text, "answer": resp, "videos": info["videos"],
            'created_at': datetime.datetime.now(), 'source_language': source, 'method': method, 'approved': False,
            "tags": tags}
    collection = get_connection()

    chat_data = collection.insert_one(data)
    info["id"] = str(chat_data.inserted_id)
    info["source"] = "chatgpt"
    response_data["result"].append(info)
    solr_insert(data)
    return response_data


def check_from_solr(question, language, temp_tags):
    resp = None
    enc = None
    videos = None
    tags = None
    try:
        final_url = settings.solr_query_url
        if temp_tags is not None:

            tag_msg = None
            if temp_tags is not None:
                count = 0
                tag_msg = ""
                for tag in temp_tags:
                    tag_msg += f"{tag}"
                    if len(temp_tags) == count + 1:
                        break
                    tag_msg += " OR "

                    count += 1
            final_url += settings.solr_tag_list.format(tag_msg)
        if question is not None:
            question = question.replace(' ', '%20')
            final_url += settings.solr_question.format('%22'+question+'%22')
        response = requests.get(url=final_url)
        answer = json.loads(response.text)
        response_data = {"count": 0, "result": []}
        data = {}
        if len(answer['response']['docs']) > 0:
            response_data["count"] = [answer['response']['numFound']]
            for response in answer['response']['docs']:
                resp = response['answer'][0]
                raw_data = resp.replace('\n', '').replace(".", "")
                data["data"] = str(raw_data)
                audio_data = get_audio(raw_data, language)
                audio = base64.b64encode(audio_data.audio_content)
                data["audio"] = audio.decode('utf-8')
                data["videos"] = response.get('videos', None)
                data["tags"] = response.get('tags', None)
                solr_id = response.get('_id', None)
                if solr_id is not None:
                    data['id'] = solr_id[0]
                    response_data["result"].append(data)
                    # print("length", len(response_data))
        return response_data
    except Exception as e:
        return resp, enc, videos, tags

# def solr_dym(question, language):
#     try:
#         query_string = word_tokenizer(question, language)
#         final_url = settings.solr_dym_url + query_string
#         response = requests.get(url=final_url)
#         answer = response.json()
#         dym_list = []
#         if answer.get('spellcheck', None):
#             dym_list = answer['spellcheck']['collations']
#         final_list = []
#         i = 1
#         for dym in dym_list:
#             if type(dym) == dict:
#                 final_list.append(str(dym['collationQuery']))
#                 i += 1
#         return final_list
#     except Exception as e:
#         print(str(e))
#         return None


# def word_tokenizer(question, language):
#     try:
#         text_tokens = word_tokenize(question)
#         query_string = ''
#         for i in text_tokens:
#             print('print the i ')
#             query_string += '%20' + i
#         return query_string
#     except Exception as e:
#         print(str(e))
#         print('print the error')


@app.route('/saved_msg', methods=('GET', 'POST'))
def saved_msg():
    try:
        question = None
        tags = request.json.get('tags', None)
        language = request.json.get('language', 'en')
        response_data = check_from_solr(question, language, tags)
        if len(response_data['result']) != 0:
            response_data["source"] = "solr"
            print('solr')
            return jsonify(response_data), 200
    except Exception as e:
        return {"error": True, "message": str(e)}, 200


@app.route('/update_msg', methods=('GET', 'POST'))
def update_msg():
    try:
        id = request.json.get("id", None)
        if id is None:
            return "Id not found", 404
        data = request.get_json()
        data.pop('id')        
        collection = get_connection()
        collection.update_one({"_id": ObjectId(str(id))}, {"$set": request.json})
        return "Success", 200
    except Exception as e :
        return {"error": True, "message": str(e)}, 200


@app.route('/chat_gpt_api', methods=('GET', 'POST'))
def chat_gpt_api():
    text = request.json.get("query", None)
    combined_result = {}
    client = translate_v2.Client()
    result = client.detect_language(text)
    source = str(result['language'])
    t2 = threading.Thread(target=get_resp, args=(text, combined_result, source))
    t2.start()
    t2.join()
    resp = combined_result['text']
    response_data = {"count": 1, "error": False, "message": None, "result": resp}
    return jsonify(response_data), 200
