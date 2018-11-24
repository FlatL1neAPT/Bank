from DataBase.DBController import DBController


class BankList:

    @staticmethod
    def get():
        controller = DBController()
        cur = controller.get_cursor()

        cur.execute("""SELECT * From Bank;""")

        bank_list = cur.fetchall()

        res = []

        for bank_rec in bank_list:
            module = __import__("Bank." + bank_rec["Module"])
            res.append(getattr(getattr(module, bank_rec["Module"]), bank_rec["Module"])(bank_rec))

        return res


if __name__ == "__main__":
    for bank in BankList.get():
        res = bank.is_region_allow("629320,ЯМАЛО-НЕНЕЦКИЙ АВТОНОМНЫЙ ОКРУГ, ,НОВЫЙ УРЕНГОЙ ГОРОД, ,МИРА ПРОСПЕКТ,ДОМ 32, ,КВАРТИРА 129")
        bank.is_in_odp("390507916036")
