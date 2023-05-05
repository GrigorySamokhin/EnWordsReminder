import pycurl
import certifi
import json
import configparser

from io import BytesIO

import requests


class DictProcessor(object):

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")
        self.dict_token = self.config["ya"]["dict"]
        self.lang = "en-ru"
        self.dict_url = "https://dictionary.yandex.net/api/v1/dicservice.json/lookup"
        self.dict_url_ex = "https://dictionary.yandex.net/dicservice.json/queryCorpus"

    def get_dict_translate(self, text: str):
        params = {
            "key": self.dict_token,
            "lang": self.lang,
            "text": text
        }

        response = requests.get(url=self.dict_url, params=params)
        assert response.status_code == 200

        ts = ''
        if "ts" in response.json()["def"][0]:
            ts = response.json()["def"][0]["ts"]

        tr = [tr["text"] for tr in response.json()["def"][0]["tr"]]

        return ts, tr

    def get_dict_examples(self, text: str):
        ts, tr = self.get_dict_translate(text)
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self.dict_url_ex
                 + '?srv=tr-text&lang={}&src={}'.format(self.lang, text))
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.CAINFO, certifi.where())
        c.perform()
        c.close()
        body = buffer.getvalue()
        body_decoded = body.decode('utf-8')
        res = json.loads(body_decoded)["result"]

        tr_list = []
        for example in res:
            if "text" not in example["translation"]:
                continue
            tr_list.append(example["translation"]["text"])

        en_word = res[0]['text']
        res_head = '✅ *' + en_word + '* \[' + ts + '\] — _' + ', '.join(tr_list) + '_\n\n'

        for j, example in enumerate(res):
            if "text" not in example["translation"]:
                continue
            res_head += '▶️ *' + en_word + '* — _' + example["translation"]["text"] + '_\n'
            for i, ex in enumerate(example['examples']):
                ex_0 = ex['src'].replace('<', '*').replace('>', '*').replace('-', '\-').replace('.', '\.').replace('!', '\!')
                ds_0 = ex['dst'].replace('<', '*').replace('>', '*').replace('-', '\-').replace('.', '\.').replace('!', '\!')

                if ds_0[0] == "\\" and ds_0[1] == "-":
                    ds_0 = ds_0[3:]
                if ex_0[0] == "\\" and ex_0[1] == "-":
                    ex_0 = ex_0[3:]
                if ds_0[0] == "—" and ds_0[1] == " ":
                    ds_0 = ds_0[2:]
                if ex_0[0] == "—" and ex_0[1] == " ":
                    ex_0 = ex_0[2:]

                res_head += '\- ' + ex_0 + '\n\- ' + ds_0 + '\n\n'

                if i == 1:
                 break

            # if j == 2:
            #     break

        return res_head


if __name__ == "__main__":
    from rich.markdown import Markdown
    import markdown
    dict_proc = DictProcessor()
    # ts, tr = dict_proc.get_dict_translate("insist")
    res = dict_proc.get_dict_examples("interesting")

    print(res)