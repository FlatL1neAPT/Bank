from Bank.Bank import Bank
import requests
import json

class PromSvazBank(Bank):

    def __init__(self, rec):
        super().__init__(rec)

        try:
            pass
            #ad = rec["AuthData"]

            #if ad is not None:
            #    self.auth_data = json.loads(ad)
        except Exception as e:
            raise e

    def auth(self):
        url = "https://api.dev.rko.psb.finstar.online/fo/v1.0.0/user/login"

        r = requests.post(url, json={"email": "ceo@profitsale24.com", "password": "18Fghtkz"})

        r = json.loads(r.text)

        i = 0
        return r

    def get_work_region_city_list(self, region):

        self.auth()

        url = "http://api.dev.rko.psb.finstar.online/fo/v1.0.0/cities?access-token=profit_access"

        r = requests.get(url)

        r = json.loads(r.text)

        r.text


if __name__ == "__main__":
    bank = PromSvazBank(None)

    bank.get_work_region_city_list(None)
