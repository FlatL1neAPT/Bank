from Bank.Bank import Bank
from DataBase.Region import Region
import requests
import json
import time
import random
import string


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

    def send_org(self, org, log):

        region = Region.find_region_by_address(org["Адрес"])

        if region is None:
            err = "По адресу {} не найден регион".format(org["Адрес"])
            log.write(err)
            raise Exception(err)

        if self.SID['id'] is None:
            self.SID['id'], self.SID['time'] = SberBank._login("koromandeu@mail.ru", "09876qwE")

        url = "https://ppapi.dasreda.ru/api/v1/merchant_branch_city?merchant_id=39&" \
              "merchant_branch_region_id={}&profile_id=56&is_active=1".format(int(region.get_number())+1)

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        response = json.loads(res.text)

        if res.status_code == 401:
            if response["errors"][0]["_error"] == "authorization_required":
                pass

        city_list = response['entries']
        our_city = None

        for city in city_list:
            if org["Адрес"].upper().find(city['name'].upper()) != -1:
                our_city = city
                break

        if our_city is None:
            err = "По адресу {} в регионе {} не найден город среди {}".format(org["Адрес"], region.get_name(),
                                                                              str(city_list))
            log.write(err)
            raise Exception(err)

        url="https://ppapi.dasreda.ru/api/v1/merchant_branch_address?merchant_id=39&" \
            "merchant_branch_city_id={}&profile_id=56&is_active=1".format(city["id"])

        res = requests.get(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                         "UserTime": self.SID['time'], "Source": "ui"})

        response = json.loads(res.text)

        office = response['entries'][0]

        url = "https://ppapi.dasreda.ru/api/v1/order"

        boundary = "----WebKitFormBoundary" + \
                   ''.join(random.choices(string.ascii_uppercase + string.digits, k=16)).lower()

        body = "--" + boundary  + "\n"
        body += """Content-Disposition: form-data; name="[data][merchant_branch_id]"

{}
""".format(office["id"])

        body += "--" + boundary  + "\n"
        body += """Content-Disposition: form-data; name="[data][merchant_branch_city_id]"

{}
""".format(city["id"])

        body += "--" + boundary  + "\n"
        body += """Content-Disposition: form-data; name="[data][vat_number]"

{}
""".format(org["ИНН"])

        body += "--" + boundary  + "\n"
        body += """Content-Disposition: form-data; name="[data][company_name]"

{}
""".format(org["Название"])

        body += "--" + boundary  + "\n"
        body += """Content-Disposition: form-data; name="[data][last_name]"

{}
""".format(org["Фамилия"])

        body += "--" + boundary  + "\n"
        body += """Content-Disposition: form-data; name="[data][first_name]"

{}
""".format(org["Имя"])

        body += "--" + boundary  + "\n"
        body += """Content-Disposition: form-data; name="[data][middle_name]"

{}
""".format(org["Отчество"])

        body += "--" + boundary  + "\n"
        body += """Content-Disposition: form-data; name="[data][email]"


"""

        body += "--" + boundary  + "\n"
        body += """Content-Disposition: form-data; name="[data][mobile_phone]"

{}
""".format(org["Телефон"])

        body += "--" + boundary  + "\n"
        body += """Content-Disposition: form-data; name="[data][add_info]"


"""

        body += "--" + boundary  + "\n"
        body += """Content-Disposition: form-data; name="[data][merchant_branch_region_id]"

{}
""".format(int(region.get_number())+1)

        body += "--" + boundary  + "\n"
        body += """Content-Disposition: form-data; name="[data][product_profile_id]"

56
"""

        body += "--" + boundary  + "\n"
        body += """Content-Disposition: form-data; name="[data][merchant_id]"

39
"""

        body += "--" + boundary + "--\n"

        res = requests.post(url, headers={'Authorization': "Token token=" + self.SID['id'], "UserId": "10965",
                                          "UserTime": self.SID['time'], "Source": "ui",
                                          "Content-Type": "multipart/form-data; boundary=" + boundary})
