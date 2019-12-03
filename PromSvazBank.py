from Bank.Bank import Bank
import requests
import json

class PromSvazBank(Bank):

    def __init__(self, rec):
        super().__init__(rec)

        try:
            ad = rec["AuthData"]

            if ad is not None:
                self.auth_data = json.loads(ad)
        except Exception as e:
            raise e

        #self.url = "http://api.dev.rko.psb.finstar.online/fo/v1.0.0/"
        self.url = "https://api.finstar.online/fo/v1.0.0/"

    def auth(self):

        if "token" in self.auth_data and self.auth_data["token"]:
            return

        url = "{}user/login".format(self.url)

        r = requests.post(url, json=self.auth_data)

        r = json.loads(r.text)

        self.auth_data["token"] = r["data"]["access_token"]
        self.save_auth_data(json.dumps(self.auth_data))

    def is_in_odp_full(self, inn):
        return self.is_in_odp(inn)

    def is_in_odp(self, inn):

        #return False

        def impl():
            self.auth()

            url = "{}orders/check-inn?access-token={}".format(self.url, self.auth_data["token"])

            res = requests.post(url, json={"inn": inn}, headers={"accept": "application/json",
                                                                 "Content-Type": "application/json"})
            response = json.loads(res.text)

            if "message" in response and response["message"] == 'Заявка с таким ИНН уже есть в системе':
                return True

            return False

        try:
            return impl()
        except:
            self.auth_data["token"] = None
            return impl()

    def get_work_region_list(self):

        def impl():
            self.auth()

            url = "{}cities?access-token={}".format(self.url, self.auth_data["token"])

            res = requests.get(url)
            response = json.loads(res.text)

            res = []

            for region in response["data"]:
                if {'ID': region['region'], 'name': region['region']} not in res:
                    res.append({'ID': region['region'], 'name': region['region']})

            return res

        try:
            return impl()
        except:
            self.auth_data["token"] = None
            return impl()

    def get_work_region_city_list(self, region):

        def impl():
            self.auth()

            url = "{}cities?access-token={}".format(self.url, self.auth_data["token"])

            res = requests.get(url)
            response = json.loads(res.text)

            res = []

            for city in response["data"]:
                if city['region'] == region:
                    res.append({'ID': city['city_id'], 'name': city['city_name']})

            return res

        try:
            return impl()
        except:
            self.auth_data["token"] = None
            return impl()

    def send_org(self, org_data, log):

        def impl():
            self.auth()

            url = "{}orders?access-token={}".format(self.url, self.auth_data["token"])

            comment = org_data["Комментарий"]
            city_id = ""
            email = ""

            if comment is not None and comment.find("#ОфисБанка:") != -1:
                start_pos = comment.find("#ОфисБанка:")
                end_pos = comment.find("#", start_pos + 1)

                add_data = comment[start_pos + 11:end_pos].split(":")
                email = add_data[0]
                city_id = add_data[1]
                comment = comment[:start_pos] + comment[end_pos+1:]

            if not email:
                email = "test@test.ru"

            data = {
                "inn": org_data["ИНН"],
                "name": org_data["Название"],
                "need_s_schet": False,
                "need_r_schet": True,
                "fio": "{} {} {}".format(org_data["Фамилия"], org_data["Имя"], org_data["Отчество"]),
                "phone": org_data["Телефон"].split("|")[0],
                "city_id": city_id,
                "email": email,
                "comment": comment
            }

            res = requests.post(url, json=data)
            response = json.loads(res.text)

            if "errors" in response:
                return [{"error":response["errors"]["message"]}]

            return []

        try:
            return impl()
        except:
            self.auth_data["token"] = None
            return impl()


if __name__ == "__main__":
    bank = PromSvazBank(None)

    bank.get_work_region_city_list(None)
