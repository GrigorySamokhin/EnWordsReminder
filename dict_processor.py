import os
import shutil

import certifi
import json
import configparser
import wget

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

        if not len(response.json()["def"]):
            return None, None


        ts = ''
        if "ts" in response.json()["def"][0]:
            ts = response.json()["def"][0]["ts"]

        tr = [tr["text"] for tr in response.json()["def"][0]["tr"]]

        return ts, tr

    def reformat_for_md(self, text, chars):
        for chr in chars:
            text = text.replace(chr, '\\' + chr)
        return text

    def get_dict_examples(self, text: str):
        ts, tr = self.get_dict_translate(text)
        if not ts and not tr:
            return None, None
        url = "\"" + self.dict_url_ex + '?srv=tr-text&lang={}&src={}'.format(self.lang, text) + "\""
        url_comm = 'wget -X GET ' + url + ' -O query.json'
        print(url_comm)
        os.system(url_comm)
        with open("query.json", 'rb') as f:
            res = json.load(f)['result']
            os.remove('query.json')
        print(res)
        tr_list = []
        for example in res:
            if "text" not in example["translation"]:
                continue
            tr_list.append(example["translation"]["text"])

        if not len(res):
            return None, None

        en_word = res[0]['text']
        res_head = '✅ *' + en_word + '* \[' + ts + '\] — _' + ', '.join(tr_list) + '_\n\n'

        for j, example in enumerate(res):
            if "text" not in example["translation"]:
                continue
            res_head += '▶️ *' + en_word + '* — _' + example["translation"]["text"] + '_\n ____'
            for i, ex in enumerate(example['examples']):
                ex_0 = self.reformat_for_md(ex['src'].replace('<', '*').replace('>', '*'), ['-', '.', '!', '(', ')'])
                ds_0 = self.reformat_for_md(ex['dst'].replace('<', '*').replace('>', '*'), ['-', '.', '!', '(', ')'])

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

            if j == 4:
                break

        return res_head, ', '.join(tr_list)

    def get_dict(self, text: str):
        ts, tr = self.get_dict_translate(text)
        if not ts and not tr:
            return None, None

        url = "\"" + self.dict_url_ex + '?srv=tr-text&lang={}&src={}'.format(self.lang, text) + "\""
        url_comm = 'wget -X GET ' + url + ' -O query.json'
        print(url_comm)
        os.system(url_comm)
        with open("query.json", 'rb') as f:
            res = json.load(f)['result']
            os.remove('query.json')

        tr_list_n = []
        tr_list_adj = []
        tr_list_vrb = []
        tr_list_adv = []
        for example in res:
            if "text" not in example["translation"]:
                continue
            if example["pos"]["code"] == "nn":
                tr_list_n.append(example["translation"]["text"])
            if example["pos"]["code"] == "adj":
                tr_list_adj.append(example["translation"]["text"])
            if example["pos"]["code"] == "adv":
                tr_list_adv.append(example["translation"]["text"])
            if example["pos"]["code"] == "vrb":
                tr_list_vrb.append(example["translation"]["text"])

        if not len(res):
            return None, None

        en_word = res[0]['text']
        if ts == "":
            ts = en_word
        res_head = '✅ *' + en_word + '* \[' + ts + '\]\n'

        len_sort_pref = sorted({
            'adj': len(tr_list_adj),
            'adv': len(tr_list_adv),
            'vrb': len(tr_list_vrb),
            'noun': len(tr_list_n)})

        val_sort_pref = {
            'adj': tr_list_adj,
            'adv': tr_list_adv,
            'vrb': tr_list_vrb,
            'noun': tr_list_n}

        for pref in reversed(len_sort_pref):
            if len(val_sort_pref[pref]):
                res_head += '\n`{0}`\n_'.format(pref) + ', '.join(val_sort_pref[pref]) + '_\n'


        # if len(tr_list_n):
        #     res_head += '\n\n`noun`\n_' + ', '.join(tr_list_n) + '_\n'
        # if len(tr_list_adj):
        #     res_head += '\n\n`adj`\n_' + ', '.join(tr_list_adj) + '_\n'
        # if len(tr_list_adv):
        #     res_head += '\n\n`adv`\n_' + ', '.join(tr_list_adv) + '_\n'
        # if len(tr_list_vrb):
        #     res_head += '\n\n`vrb`\n_' + ', '.join(tr_list_vrb) + '_\n'

        return res_head, ', '.join(tr_list_n)

if __name__ == "__main__":
    from rich.markdown import Markdown
    import markdown
    dict_proc = DictProcessor()
    # ts, tr = dict_proc.get_dict_translate("insist")
    res = dict_proc.get_dict_examples("interesting")

    print(res)