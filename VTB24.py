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

        self.Token = None

        ad = self.auth_data()

        if ad is not None:
            self.Token = ad

    def auth(self):
        now = datetime.now()
        date = now.strftime('%a, %d %b %Y %H:%M:%S Europe/Moscow')
        hash = hashlib.sha256((self.key2 + hashlib.sha256((self.key1 + date).encode()).hexdigest()).encode()).hexdigest()
        Token = "#" + self.key1 + "#" + hash

        url = "https://mb-partner.bm.ru/auth/ident"

        res = requests.post(url, headers={'Token': Token, "Date": date})

        response = json.loads(res.text)

        self.save_auth_data(response["access_token"]["token"])
        return response["access_token"]["token"]

    def is_allow_uncorrect_address(self):
        return True

    def is_in_odp(self, inn):
        return False

    def get_work_region_list(self):

        if self.Token is None:
            self.Token = self.auth()

        url = "https://mb-partner.bm.ru/misc/regions"

        res = requests.get(url, headers={'Token': self.Token})
        response = json.loads(res.text)

        res = []

        for region in response["region_list"]:
            res.append({'ID': region['value'], 'name': region['name']})

        return res

    def get_work_region_city_list(self, region):
        if self.SID['id'] is None:
            self.SID['id'], self.SID['time'] = self._login("koromandeu@mail.ru", "09876qwE")

        url = "https://ppapi.dasreda.ru/api/v1/merchant_branch_city?merchant_id=39&" \
              "merchant_branch_region_id={}&profile_id=56&is_active=1".format(int(region))

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        response = json.loads(res.text)

        city_list = response['entries']

        res = []

        for city in city_list:
            res.append({'ID': city["id"], 'name': city["name"]})

        return res

    def get_work_region_city_office_list(self, region, city):

        if self.SID['id'] is None:
            self.SID['id'], self.SID['time'] = self._login("koromandeu@mail.ru", "09876qwE")

        url = "https://ppapi.dasreda.ru/api/v1/merchant_branch_address?merchant_id=39&" \
              "merchant_branch_city_id={}&profile_id=56&is_active=1".format(city)

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        response = json.loads(res.text)

        office_list = response['entries']

        res = []

        for office in office_list:
            res.append({'ID': office["id"], 'name': office["name"]})

        return res

if __name__ == "__main__":

    bank = VTB24({"ID":8})
    bank.get_work_region_list()