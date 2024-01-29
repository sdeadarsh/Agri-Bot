import json
import requests
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
import pandas as pd

import settings
nltk.download('punkt')
nltk.download('stopwords')

connection = ''
cursor = ''

header = {'Content-Type': 'application/json'}
try:

    data = pd.read_csv("igrow_chat_data.csv")

    for i in data['message']:
        string_value = str(i)
        text_tokens = word_tokenize(string_value)
        if len(text_tokens) > 3:
            tokens_without_sw = [word for word in text_tokens if not word in stopwords.words('english')]
            if len(tokens_without_sw) > 3:
                filtered_sentence = (" ").join(tokens_without_sw)
                final_string = str(filtered_sentence)
                if final_string not in (None, 'null', ''):
                    data = {'query': final_string}
                    data = json.dumps(data)
                    print(data)
                    response = requests.post(url=settings.chat_url, data=data, headers=header)
                    print(response.status_code)

except Exception as e:
    print(str(e))
