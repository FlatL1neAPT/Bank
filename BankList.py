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

    @staticmethod
    def get_by_name(name):
        controller = DBController()
        cur = controller.get_cursor()

        cur.execute("""SELECT * From Bank WHERE Name = %s;""", (name,))

        bank_list = cur.fetchall()

        if len(bank_list) == 0:
            return None

        bank_rec = bank_list[0]

        module = __import__("Bank." + bank_rec["Module"])
        return getattr(getattr(module, bank_rec["Module"]), bank_rec["Module"])(bank_rec)


if __name__ == "__main__":
    for bank in BankList.get():
        res = bank.is_region_allow("629320,ЯМАЛО-НЕНЕЦКИЙ АВТОНОМНЫЙ ОКРУГ, ,НОВЫЙ УРЕНГОЙ ГОРОД, ,МИРА ПРОСПЕКТ,ДОМ 32, ,КВАРТИРА 129")
        bank.is_in_odp("390507916036")
