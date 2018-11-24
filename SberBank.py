from Bank.Bank import Bank
import requests
import json
import time


class SberBank(Bank):

    def __init__(self, rec):
        self.SID = {"id": None, "time": None}
        super().__init__(rec)

    @staticmethod
    def _login(username, password):
        request = {"data": {
            "username": username,
            "password": password
        }}
        url = "https://ppapi.dasreda.ru/api/v1/login"

        headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://partners.dasreda.ru',
            'UseraAgent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                           Chrome/65.0.3325.181 Safari/537.36',
            'Content-Type': 'application/json;charset=UTF-8',
            'Referer': 'https://partners.dasreda.ru/auth',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'}

        res = requests.post(url, json=request, headers=headers)

        response = json.loads(res.text)

        if "eo_token" in response:
            guid = response["eo_token"]

            ts = int(time.time() * 1000)
            cts = ts % 0x2710

            res = ""
            for i in range(0, len(guid)):
                res += guid[cts % (i + 0x1)]

            return res, str(ts)

        return "", ""

    def is_in_odp(self, inn):

        if self.SID['id'] is None:
            self.SID['id'], self.SID['time'] = SberBank._login("koromandeu@mail.ru", "09876qwE")

        url = "https://ppapi.dasreda.ru/api/v1/order/new?merchant_id=39&product_" \
              "type=2&product_profile_id=53&vat_number=" + inn

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                         "UserTime": self.SID['time'], "Source": "ui"})
        response = json.loads(res.text)

        if res.status_code == 401:
            if response["errors"][0]["_error"] == "authorization_required":
                self.SID['id'], self.SID['time'] = SberBank._login("koromandeu@mail.ru", "09876qwE")
                res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                                 "UserTime": self.SID['time'], "Source": "ui"})

        response = json.loads(res.text)

        if "errors" in response:
            if 'blocked' in response["errors"]["blocked_by_other"]:
                return True

        return False
