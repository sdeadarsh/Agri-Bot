import json
import settings
import pysolr
import app
import datetime


def solr_delta_import(data, clean):
    try:
        solr = pysolr.Solr(settings.solr_url, always_commit=True)
        ping = solr.ping()
        status = json.loads(ping)
        if status['status'] == 'OK':
            if clean is True:
                solr.delete(q='*:*')
            solr.add(data)
            return None
    except Exception as e:
        print(str(e))


def solr_insert(data):
    data['question'] = [data['question']]
    data['answer'] = [data['answer']]
    data['created_at'] = str(data['created_at'])
    data['question_en'] = [data['question_en']]
    data['_id'] = str(data['_id'])
    final_data = data
    solr_delta_import(final_data, clean=False)
    return None


def solr_full_import():
    collection = app.get_connection()
    limit = 10000
    offset = 0
    no_data = False
    final_data = []
    solr_delta_import(final_data, clean=True)
    while (no_data == False):
        data = list(collection.find().limit(limit).skip(offset))
        if len(data) == 0:
            no_data = True
            break
        final_data = []
        data_dict = {}
        for items in data:
            try:
                data_id = items.get('_id', None)
                final_data_id = None
                if data_id is not None:
                    final_data_id = str(data_id)
                created_at = items.get('created_at', datetime.datetime.now())
                current_date = created_at.strftime('%Y-%m-%dT%H:%M:%SZ')
                data_dict = {'question': [items.get('question', "")], 'answer': [items.get('answer', "")],
                             '_id': final_data_id,
                             'created_at': current_date,
                             'question_en': [items.get('question_en', "")], 'videos': [items.get('videos', "")]}
            except Exception as e:
                pass
            if data_dict['question'] not in ([""], None, ['']) or data_dict['_id'] is not None:
                final_data.append(data_dict)
        solr_delta_import(final_data, clean=False)
        limit += 10000
        offset += 10000
