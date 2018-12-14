from Bank import Bank
from datetime import datetime
import hashlib
import json
import requests


class VTB24(Bank):

    def __init__(self, rec):
        super().__init__(rec)
        self.key1 = "dd21febcfb7f17b639e951804cefa873583559894aca91224b535d509bbcb1c1"
        self.key2 = "66b01b6ed9a89ea08989682b5e72c85c5c1b18087b65e9227589b56b672bc70d"

    def auth(self):
        now = datetime.now()
        date = now.strftime('%a, %d %b %Y %H:%M:%S Europe/Moscow')
        hash = hashlib.sha256((self.key2 + hashlib.sha256((self.key1 + date).encode()).hexdigest()).encode()).hexdigest()
        Token = "#" + self.key1 + "#" + hash

        url = "https://online.bm.ru/auth/ident"

        res = requests.post(url, headers={'Token': Token, "Date": date})

        response = json.loads(res.text)

        i = 0


    def is_allow_uncorrect_address(self):
        return True

    def is_in_odp(self, inn):
        return False

    def get_work_region_list(self):

        self.auth()

if __name__ == "__main__":

    bank = VTB24({"ID":1})
    bank.get_region_list()