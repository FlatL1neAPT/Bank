from Bank.Bank import Bank
import json
import requests


class TinkoffBank(Bank):

    def __init__(self, rec):
        super().__init__(rec)

    def is_allow_uncorrect_address(self):
        return True

    def is_in_odp(self, inn):
        from datetime import datetime

        print(datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S") + " " + str(inn))

        request = {"fields": {"inn": inn},
                   "inn_checked_status": 4,
                   "errors": {"inn": False}}

        url = "https://ats.tinkoff.ru/uif/partner/f8f513aefb7f3feb47e219995f7d3711/check_inn/"

        res = requests.post(url, json=request)
        response = json.loads(res.text)

        if response['result'] == "Duble":
            return True
        else:
            return False
