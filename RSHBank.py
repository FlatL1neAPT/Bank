from Bank.Bank import Bank
import json
import requests


class RSHBank(Bank):

    def __init__(self, rec):
        super().__init__(rec)

        try:
            ad = rec["AuthData"]

            if ad is not None:
                self.auth_data = json.loads(ad)
        except Exception as e:
            raise e

        self.rgs = {
	'Республика Адыгея': ['г. Майкоп',
	'г. Адыгейск',
	'а. Кошехабль',
	'а. Тахтамукай',
	'с. Красногвардейское',
	'п. Тульский'],
	'Алтайский край': ['г. Барнаул',
	'с. Завьялово',
	'г. Бийск',
	'р.п. Благовещенка',
	'с. Шипуново',
	'г. Славгород',
	'г. Рубцовск',
	'г. Белокуриха',
	'с. Романово',
	'г. Камень-на-Оби',
	'с. Павловск',
	'с. Советское',
	'с. Родино',
	'с. Хабары',
	'с. Волчиха',
	'с. Чарышское',
	'с. Краснощеково',
	'г. Новоалтайск',
	'с. Ребриха',
	'р.п. Тальменка',
	'с. Поспелиха',
	'с. Угловское',
	'с. Тогул',
	'с. Кулунда',
	'с. Мамонтово',
	'с. Усть-Калманка',
	'г. Горняк',
	'г. Алейск'],
	'Республика Алтай': ['г. Горно-Алтайск',
	'с. Кош-Агач',
	'с. Онгудай',
	'с. Шебалино',
	'с. Усть-Кокса',
	'с. Чемал'],
	'Амурская область': ['г. Благовещенск',
	'п. Архара',
	'с. Тамбовка',
	'с. Екатеринославка',
	'с. Ивановка',
	'с. Константиновка',
	'п. Серышево',
	'с. Поярково',
	'г. Свободный',
	'п. Новобурейский',
	'с. НовокиевскийУвал',
	'г. Белогорск',
	'г. Зея',
	'г. Завитинск',
	'г. Шимановск'],
	'Архангельская область': ['г. Архангельск',
	'г. Котлас',
	'г. Вельск',
	'п. Октябрьский',
	'п. Плесецк',
	'с. Ильинско-Подомское',
	'г. Онега',
	'п. Коноша',
	'г. Северодвинск',
	'с. Холмогоры',
	'г. Каргополь'],
	'Республика Башкортостан': ['г. Уфа',
	'с. Верхнеяркеево',
	'с. Буздяк',
	'г. Баймак',
	'с. Чекмагуш',
	'г. Туймазы',
	'с. Месягутово',
	'г. Стерлитамак',
	'с. Толбазы',
	'г. Мелеуз',
	'г. Янаул',
	'г. Дюртюли',
	'с. Караидель',
	'г. Белебей',
	'с. Раевский',
	'с. Староболтачево',
	'с. Большеустьикинское',
	'с. Киргиз-Мияки',
	'г. Учалы',
	'с. Кармаскалы',
	'с. Мраково',
	'с. Языково',
	'с. Исянгулово',
	'г. Давлеканово',
	'с. Бакалы',
	'с. ВерхниеТатышлы',
	'с. Аскарово',
	'с. Малояз',
	'с. Кушнаренково',
	'с. Зилаир',
	'г. Стерлибашево',
	'с. Ермолаево',
	'с. Акъяр',
	'с. Бижбуляк',
	'с. Иглино',
	'г. Бирск',
	'г. Ишимбай',
	'с. Бураево',
	'с. Шаран',
	'г. Салават',
	'р.п. Чишмы',
	'г. Октябрьский',
	'г. Нефтекамск'],
	'Белгородская область': ['г. Белгород',
	'г. Бирюч',
	'г. Грайворон',
	'п. Волоконовка',
	'п. Ивня',
	'п. Ровеньки',
	'п. Вейделевка',
	'п. Прохоровка',
	'п. Ракитное',
	'г. Алексеевка',
	'п. Чернянка',
	'г. Губкин',
	'г. СтарыйОскол',
	'г. НовыйОскол'],
	'Брянская область': ['г. Брянск',
	'г. Дятьково',
	'г. Новозыбково',
	'г. Клинцы',
	'г. Трубчевск',
	'пгт. Погар',
	'г. Жуковка',
	'г. Стародуб',
	'г. Унеча',
	'г. Почеп'],
	'Республика Бурятия': ['г. Улан-Удэ',
	'с. Мухоршибирь',
	'г. Закаменск',
	'с. Петропавловка',
	'с. Кабанск',
	'г. Кяхта',
	'с. Хоринск',
	'с. Сосново-Озерское',
	'с. Курумкан',
	'с. Баргузин',
	'с. Кырен',
	'г. Гусиноозерск',
	'п. Заиграево',
	'с. Турунтаево',
	'с. Кижинга'],
	'Владимирская область': ['г. Владимир',
	'г. Ковров',
	'г. Муром',
	'г. Киржач',
	'г. Лакинск',
	'г. Вязники',
	'г. Юрьев-Польский',
	'г. Меленки',
	'г. Кольчугино',
	'г. Гусь-Хрустальный',
	'г. Судогда',
	'г. Камешково',
	'п. КраснаяГорбатка',
	'г. Покров',
	'г. Александров',
	'г. Петушки'],
	'Волгоградская область': ['г. Волгоград',
	'г. Новоаннинский',
	'г. Урюпинск',
	'ст. Алексеевская',
	'г. Фролово',
	'р.п. Даниловка',
	'г. Серафимович',
	'г. Жирновск',
	'р.п. Новониколаевский',
	'г. Котельниково',
	'г. Котово',
	'г. Михайловка',
	'р.п. Иловля',
	'г. Палласовка',
	'г. Калач-наДону',
	'р.п. Елань',
	'г. Камышин',
	'с. Ольховка',
	'ст. Клетская',
	'р.п. Рудня',
	'г. Волжский',
	'г. Суровикино',
	'с. СтараяПолтавка',
	'ст. Кумылженская',
	'г. Николаевск',
	'р.п. СредняяАхтуба'],
	'Астраханская область': ['г. Астрахань',
	'с. Началово',
	'г. Ахтубинск',
	'с. Икряное',
	'с. ЧерныйЯр',
	'п. Лиман',
	'г. Камызяк',
	'с. КрасныйЯр',
	'п. Володарский',
	'г. Харабали',
	'г. Нариманов'],
	'Воронежская область': ['г. Воронеж',
	'г. Богучар',
	'г. Россошь',
	'г. Бутурлиновка',
	'г. Калач',
	'г. Бобров',
	'г. Павловск',
	'г. Лиски',
	'г. Борисоглебск',
	'с. Терновка',
	'г. Новохоперск',
	'пгт. Анна',
	'с. ВерхнийМамон',
	'р.п. Таловая',
	'р.п. Рамонь',
	'г. Эртиль',
	'г. Поворино',
	'г. Семилуки',
	'р.п. Ольховатка'],
	'Республика Дагестан': ['г. Махачкала',
	'г. Каспийск',
	'с. Унцукуль',
	'с. Карабудахкент',
	'с. Новолакское',
	'с. Хив',
	'г. Хасавюрт',
	'г. Дербент',
	'г. Кизилюрт',
	'г. Кизляр',
	'с. Кумух',
	'с. Новокаякент',
	'с. Гуниб',
	'с. Хебда',
	'с. Хунзах',
	'с. Бабаюрт',
	'с. Уркарах',
	'с. Дылым',
	'с. Терекли-Мектеб',
	'с. Касумкент'],
	'Ивановская область': ['г. Иваново',
	'г. Пучеж',
	'г. Гаврилов-Посад',
	'г. Приволжск',
	'г. Родники',
	'г. Кинешма',
	'г. Шуя',
	'г. Вичуга',
	'г. Фурманов',
	'г. Тейково'],
	'Республика Ингушская': ['г. Назрань'],
	'Иркутская область': ['г. Иркутск',
	'п. Усть-Ордынский',
	'п. Куйтун',
	'р.п. Усть-Уда',
	'п. Кутулик',
	'г. Тайшет',
	'с. Еланцы',
	'с. Оса',
	'г. Черемхово',
	'п. Чунский',
	'г. Братск',
	'г. Нижнеудинск',
	'г. Тулун',
	'п. Залари',
	'г. Усолье-Сибирское',
	'г. Ангарск',
	'г. Усть-Илимск'],
	'Республика Кабардино-Балкарская': ['г. Нальчик',
	'г. Прохладный',
	'с. Анзорей',
	'г. Нарткала',
	'г. Баксан',
	'пгт. Залукокоаже',
	'пгт. Кашхатау',
	'г. Тырныауз',
	'г. Терек',
	'г. Чегем',
	'г. Майский'],
	'Калининградская область': ['г. Калининград',
	'г. Гурьевск',
	'г. Гусев',
	'г. Славск',
	'г. Зеленоградск',
	'г. Полесск',
	'г. Гвардейск',
	'г. Багратионовск',
	'г. Советск'],
	'Калужская область': ['г. Калуга',
	'г. Жуков',
	'г. Таруса',
	'г. Кондрово',
	'г. Балабаново',
	'г. Людиново',
	'г. Малоярославец',
	'г. Козельск',
	'г. Обнинск',
	'г. Медынь',
	'г. Мещовск'],
	'Камчатский край': ['г. Петропавловск-Камчатский',
	'г. Елизово',
	'г. Вилючинск',
	'г. Петропавловск-Камчатский'],
	'Кемеровская область': ['г. Кемерово',
	'г. Ленинск-Кузнецкий',
	'г. Мариинск',
	'г. Белово',
	'р.п. Промышленная',
	'г. Анжеро-Судженск',
	'г. Новокузнецк',
	'г. Прокопьевск',
	'г. Юрга',
	'р.п. Яшкино',
	'пгт. Тисуль',
	'г. Киселевск'],
	'Кировская область': ['г. Киров',
	'пгт. Подосиновец',
	'г. Слободской',
	'г. Зуевка',
	'г. Советск',
	'г. Уржум',
	'г. Котельнич',
	'г. Яранск',
	'г. БелаяХолуница',
	'г. Малмыж',
	'г. Нолинск',
	'пгт. Кильмезь',
	'п. Кумены',
	'г. Орлов',
	'г. Мураши',
	'пгт. Суна',
	'г. ВятскиеПоляны',
	'пгт. Пижанка',
	'г. Омутнинск',
	'с. Лойно',
	'п. Даровской',
	'г. Кирово-Чепецк'],
	'Республика Коми': ['г. Сыктывкар',
	'с. Корткерос',
	'г. Емва',
	'с. Айкино',
	'г. Ухта'],
	'Костромская область': ['г. Кострома',
	'г. Галич',
	'п. Островское',
	'г. Мантурово',
	'г. Буй',
	'г. Нерехта',
	'г. Шарья'],
	'Краснодарский край': ['г. Краснодар',
	'г. Кропоткин',
	'ст. Крыловская',
	'ст. Полтавская',
	'ст. Выселки',
	'ст. Брюховецкая',
	'ст. Отрадная',
	'г. Темрюк',
	'г. Славянск-на-Кубани',
	'г. Кореновск',
	'г. Белореченск',
	'г. Ейск',
	'г. Армавир',
	'г. Сочи',
	'ст. Ленинградская',
	'г. Усть-Лабинск',
	'г. Тихорецк',
	'г. Лабинск',
	'ст. Павловская',
	'ст. Кущевская',
	'г. Тимашевск',
	'ст. Каневская',
	'г. Крымск',
	'г. Курганинск',
	'ст. Новопокровская',
	'г. Новороссийск',
	'г. Гулькевичи',
	'ст. Калининская',
	'г. Анапа',
	'ст. Староминская',
	'г. Новокубанск',
	'г. Геленджик',
	'г. Абинск'],
	'Красноярский край': ['г. Красноярск',
	'г. Назарово',
	'г. Канск',
	'с. Новоселово',
	'п. Балахта',
	'г. Уяр',
	'г. Ужур',
	'г. Минусинск',
	'с. Агинское',
	'р.п. Абан',
	'г. Лесосибирск',
	'г. Ачинск',
	'г. Шарыпово',
	'г. Боготол',
	'с. Дзержинское'],
	'Республика Хакасия': ['г. Абакан',
	'п. Копьево',
	'с. Таштып',
	'с. Бея',
	'с. БелыйЯр',
	'с. Шира',
	'г. Саяногорск',
	'с. Аскиз',
	'г. Черногорск'],
	'Курская область': ['г. Курск',
	'сл. Белая',
	'г. Фатеж',
	'пгт. Конышевка',
	'п. Глушково',
	'п. Солнцево',
	'г. Железногорск',
	'с. Мантурово',
	'г. Рыльск',
	'г. Суджа',
	'п. Медвенка',
	'г. Льгов',
	'г. Обоянь',
	'г. Щигры',
	'п. Золотухино',
	'п. Коренево',
	'г. Курчатов'],
	'Липецкая область': ['г. Липецк',
	'с. Тербуны',
	'г. Усмань',
	'г. Лебедянь',
	'с. Доброе',
	'г. Елец',
	'с. Хлевное',
	'г. Задонск',
	'г. Грязи'],
	'Республика Марий Эл': ['г. Йошкар-Ола',
	'г. Козьмодемьянск',
	'пгт. Сернур',
	'г. Звенигово',
	'пгт. Морки',
	'пгт. Советский',
	'пгт. Параньга',
	'пгт. Новый Торъял',
	'г. Волжск',
	'пгт. Мари-Турек',
	'пгт. Медведево'],
	'Республика Мордовия': ['г. Саранск',
	'с. Кемля',
	'г. Ковылкино',
	'р.п. Атяшево',
	'г. Краснослободск',
	'г. Ардатов',
	'п. Зубова Поляна',
	'п. Чамзинка',
	'г. Рузаевка',
	'п. Явас'],
	'Нижегородская область': ['г. НижнийНовгород',
	'г. Лысково',
	'р.п. Пильна',
	'р.п. Бутурлино',
	'г. Арзамас',
	'г. Сергачи',
	'р.п. Воротынец',
	'с. Починки',
	'г. Лукоянов',
	'р.п. Коверино',
	'г. Семенов',
	'г. Шахунья',
	'с. Гагино',
	'г. Урень',
	'г. Бор',
	'р.п. Тоншаево',
	'г. Кстово',
	'г. Городец',
	'г. Павлово',
	'г. Дзержинск'],
	'Новгородская область': ['г. ВеликийНовгород',
	'г. Боровичи',
	'г. Старая Русса',
	'с. Ямская Слобода',
	'г. Сольцы',
	'г. Пестово',
	'г. Малая Вишера',
	'п. Хвойная',
	'п. Демянск',
	'г. Окуловка',
	'г. Валдай'],
	'Новосибирская область': ['г. Новосибирск',
	'г. Карасук',
	'р.п. Сузун',
	'г. Барабинск',
	'р.п. Краснозерское',
	'г. Татарск',
	'р.п. Маслянино',
	'р.п. Коченево',
	'р.п. Чаны',
	'г. Искитим',
	'г. Черепаново',
	'г. Тогучин',
	'г. Купино',
	'г. Бердск'],
	'Омская область': ['г. Омск',
	'р.п. Любинский',
	'р.п. Нововаршавка',
	'р.п. Москаленки',
	'р.п. Полтавка',
	'р.п. Большеречье',
	'р.п. Муромцево',
	'с. Одесское',
	'р.п. Крутинка',
	'р.п. Шербакуль',
	'г. Калачинск',
	'р.п. Кормиловка',
	'г. Исилькуль',
	'р.п. Павлоградка',
	'р.п. Таврическое',
	'с. Солнечное',
	'р.п. Черлак',
	'г. Тара'],
	'Оренбургская область': ['г. Оренбург',
	'п.Переволоцкий',
	'с.Тоцкое',
	'с.Курманаевка',
	'г.Орск',
	'с.Ташла',
	'п.Новосергиевка',
	'п.Новоорск',
	'п.Адамовка',
	'г.Бугуруслан',
	'г.Бузулук',
	'с.Октябрьское',
	'п.Саракташ',
	'г.Сорочинск',
	'г.Кувандык',
	'п.Акбулак',
	'с.Пономаревка',
	'с.Плешаново',
	'с.Илек',
	'г.Соль-Илецк',
	'с.Александровка',
	'г.Ясный',
	'с.Грачевка',
	'с.Шарлык',
	'г.Абдулино',
	'с.Сакмара',
	'г.Гай'],
	'Орловская область': ['г.Орел',
	'г.Болхов',
	'г.Ливны',
	'пгт.Змиевка',
	'пгт.Кромы',
	'п.Глазуновка',
	'г.Дмитровск',
	'пгт.Колпна',
	'пгт.Покровское',
	'п.Нарышкино',
	'пгт.Верховье',
	'пгт.Залегощь',
	'п.Долгое',
	'г.Мценск'],
	'Пензенская область': ['г.Пенза',
	'пгт.Мокшан',
	'с.Бессоновка',
	'г.Кузнецк',
	'г.Каменка',
	'пгт.Колышлей',
	'г.НижнийЛомов',
	'г.Белинский',
	'р.п.Пачелма',
	'г.Никольск',
	'пгт.Шемышейка',
	'г.Сердобск',
	'пгт.Башмаково',
	'с.Неверкино',
	'г.Городище',
	'г.Спасск',
	'р.п.Земетчино'],
	'Пермский край': ['г.Пермь',
	'г.Кунгур',
	'г.Чайковский',
	'г.Добрянка',
	'г.Нытва',
	'г.Лысьва'],
	'Приморский край': ['г.Владивосток',
	'с.Камень-Рыболов',
	'г.Спасск-Дальний',
	'г.Арсеньев',
	'г.Уссурийск',
	'г.Дальнереченск',
	'г.Фокино',
	'с.Черниговка',
	'г.Находка',
	'г.Артем',
	'п.Кавалерово',
	'г.Лесозаводск'],
	'Псковская область': ['г.Псков',
	'г.Новосокольники',
	'пгт.Бежаницы',
	'г.ВеликиеЛуки',
	'г.Дно',
	'г.Невель',
	'г.Остров',
	'г.Печоры'],
	'Ростовская область': ['г.Ростов-на-Дону',
	'г.Семикаракорск',
	'ст.Тацинская',
	'с.Покровское',
	'с.Чалтырь',
	'сл.Кашары',
	'г.Константиновск',
	'п.Тарасовский',
	'п.Чертково',
	'р.п.Матвеев-Курган',
	'п.Орловский',
	'р.п.Усть-Донецкий',
	'п.Целина',
	'ст.Багаевская',
	'г.Азов',
	'г.БелаяКалитва',
	'с.Ремонтное',
	'ст.Вешенская',
	'г.Пролетарск',
	'п.Зимовники',
	'г.Сальск',
	'г.Аксай',
	'ст.Егорлыкская',
	'г.Зерноград',
	'г.Миллерово',
	'с.Песчанокопское',
	'г.КрасныйСулин',
	'г.Морозовск',
	'ст.Боковская',
	'г.Каменск-Шахтинский',
	'ст.Обливская',
	'г.Шахты',
	'г.Таганрог',
	'ст.Милютинская',
	'г.Волгодонск',
	'г.Батайск'],
	'Республика Калмыкия': ['г.Элиста',
	'г.Городовиковск',
	'п.Комсомольский'],
	'Рязанская область': ['г.Рязань',
	'р.п.Старожилово',
	'г.Михайлов',
	'г.Кораблино',
	'г.Касимов',
	'г.Ряжск',
	'г.Рыбное',
	'г.Скопин',
	'г.Новомичуринск',
	'г.Сасово',
	'р.п.Милославское',
	'г.Спас-Клепики',
	'п.Шилово'],
	'Самарская область': ['г.Самара',
	'г.Тольятти',
	'г.Кинель',
	'с.Пестравка',
	'с.Борское',
	'г.Похвистнево',
	'ст.Клявлино',
	'п.Безенчук',
	'с.Кинель-Черкассы',
	'г.Сызрань',
	'пгт.Суходол',
	'с.Исаклы',
	'с.Кошки',
	'с.Хворостянка',
	'с.БольшаяГлушица',
	'г.Нефтегорск',
	'с.БольшаяЧерниговка'],
	'Санкт-Петербург': ['г.Санкт-Петербург'],
	'Ленинградская область': ['г.Пикалево',
	'г.Приозерск',
	'г.Луга',
	'г.Лодейноеполе',
	'г.Волосово',
	'г.Тосно',
	'г.Гатчина',
	'г.Выборг',
	'г.Кингисепп',
	'г.СосновыйБор'],
	'Мурманская область': ['г.Мурманск',
	'с.Ловозеро',
	'г.Кола',
	'г.Полярный',
	'г.Кандалакша'],
	'Вологодская область': ['г.Вологда',
	'г.Тотьма',
	'пгт.Шексна',
	'г.Череповец',
	'г.Кириллов',
	'г.Грязовец',
	'г.ВеликийУстюг',
	'п.Чагода',
	'г.Устюжна',
	'г.Сокол',
	'г.Вытегра',
	'с.КичменгскийГородок',
	'с.ТарногскийГородок',
	'г.Бабаево'],
	'Республика Карелия': ['г.Петрозаводск',
	'г.Олонец',
	'г.Сортавала',
	'г.Медвежьегорск',
	'г.Кондопога',
	'г.Костомукша'],
	'Саратовская область': ['г.Саратов',
	'г.КрасныйКут',
	'г.Балашов',
	'р.п.Дергачи',
	'г.Маркс',
	'р.п.Степное',
	'г.Вольск',
	'г.Калининск',
	'г.Пугачев',
	'г.Новоузенск',
	'г.Ртищево',
	'г.Красноармейск',
	'г.Хвалынск',
	'г.Аркадак',
	'с.Перелюб',
	'г.Петровск',
	'р.п.БазарныйКарабулак',
	'г.Балаково',
	'г.Аткарск',
	'р.п.Ровное',
	'г.Энгельск',
	'р.п.Мокроус'],
	'Сахалинская область': ['г.Южно-Сахалинск',
	'г.Томари',
	'г.Холмск',
	'г.Анива',
	'г.Корсаков'],
	'Свердловская область': ['г.Екатеринбург',
	'г.Березовский',
	'г.Камышлов',
	'г.Алапаевск',
	'г.Ирбит',
	'г.Реж',
	'г.Красноуфимск',
	'г.Талица',
	'г.Каменск-Уральский',
	'г.НижнийТагил',
	'г.Серов',
	'г.Первоуральск',
	'г.Новоуральск'],
	'Смоленская область': ['г.Смоленск',
	'г.Вязьма',
	'г.Гагарин',
	'г.Демидов',
	'г.Рудня',
	'г.Рославль',
	'г.Сафоново'],
	'Ставропольский край': ['г.Ставрополь',
	'г.Кисловодск',
	'г.Ипатово',
	'г.Буденновск',
	'г.Георгиевск',
	'г.Светлоград',
	'с.Александровское',
	'г.Зеленокумск',
	'г.Новоалександровск',
	'г.Есентуки',
	'г.Благодарный',
	'г.Изобильный',
	'г.Пятигорск',
	'г.Невинномысск'],
	'Республика Северная Осетия-Алания': ['г.Владикавказ',
	'г.Алагир',
	'г.Беслан',
	'с.Эльхотово',
	'г.Моздок',
	'г.Ардон'],
	'Республика Карачаево-Черкессия': ['г.Черкесск',
	'г.Карачаевск',
	'п.Эркен-Шахар'],
	'Тамбовская область': ['г.Тамбов',
	'г.Жердевка',
	'п.Знаменка',
	'г.Мичуринск',
	'р.п.Сосновка',
	'р.п.Токаревка',
	'г.Рассказово',
	'р.п.Инжавино',
	'г.Кирсанов',
	'р.п.Мордово',
	'р.п.Мучкапский',
	'с.Петровское',
	'р.п.Ржакса',
	'п.Сатинка',
	'г.Уварово',
	'п.Строитель'],
	'Республика Татарстан': ['г.Казань',
	'г.Буинск',
	'г.Арск',
	'г.Чистополь',
	'с.Актаныш',
	'пгт.БогатыеСабы',
	'пгт.Балтаси',
	'г.НабережныеЧелны',
	'г.Бугульма',
	'р.п.Кукмор',
	'г.Лениногорск',
	'с.Тюлячи',
	'г.Нижнекамск',
	'г.Заинск',
	'г.Тетюши',
	'пгт.Алексеевское',
	'с.Муслюмово',
	'г.Альметьевск',
	'г.Нурлат',
	'г.Азнакаево',
	'пгт.РыбнаяСлобода',
	'г.Мамадыш',
	'г.Агрыз',
	'г.Елабуга',
	'г.Зеленодольск'],
	'Тверская область': ['г.Тверь',
	'г.Бежецк',
	'г.Кашин',
	'г.Зубцов',
	'г.Конаково',
	'г.Торжок',
	'г.КрасныйХолм',
	'г.ЗападнаяДвина',
	'п.КесоваГора',
	'п.Селижарово',
	'г.ВышнийВолочек',
	'г.Кимры',
	'г.Ржев',
	'г.Бологое',
	'г.Андреаполь',
	'г.Старица',
	'г.Осташков'],
	'Томская область': ['г.Томск',
	'с.Кожевниково',
	'г.Колпашево',
	'с.Молчаново',
	'г.Асино',
	'с.Зырянское',
	'с.Мельниково',
	'с.Бакчар',
	'с.Кривошеино',
	'с.Подгорное',
	'р.п.БелыйЯр',
	'с.Парабель'],
	'Республика Тыва': ['г.Кызыл',
	'пгт.Каа-Хем',
	'г.Чадан',
	'г.Шагонар',
	'г.Ак-Довурак'],
	'Тульская область': ['г.Тула',
	'п.Куркино',
	'г.Ефремов',
	'п.Ленинский',
	'г.Новомосковск',
	'г.Плавск',
	'г.Суворов',
	'г.Щекино',
	'г.Ясногорск',
	'г.Венев',
	'г.Богородицк',
	'г.Алексин',
	'п.Дубна',
	'г.Кимовск',
	'п.Одоев',
	'п.Чернь',
	'г.Белев'],
	'Тюменская область': ['г.Тюмень',
	'г.Ялуторовск',
	'г.Заводоуковск',
	'с.Исетское',
	'г.Ишим',
	'с.НижняяТавда',
	'с.Упорово',
	'г.Ханты-Мансийск',
	'г.Сургут'],
	'Республика Удмуртская': ['г.Ижевск',
	'г.Глазов',
	'п.Кез',
	'п.Ува',
	'г.Можга',
	'г.Воткинск',
	'с.Алнаши',
	'с.Завьялово',
	'г.Сарапул',
	'с.Вавож',
	'с.Якшур-Бодья',
	'с.МалаяПурга',
	'п.Балезино',
	'п.Игра',
	'п.Яр',
	'п.Кизнер',
	'с.Дебесы',
	'с.Красногорское',
	'г.Камбарка'],
	'Ульяновская область': ['г.Ульяновск',
	'р.п.Сурское',
	'с.Б.Нагаткино',
	'р.п.Кузоватово',
	'р.п.Майна',
	'р.п.Карсун',
	'р.п.Павловка',
	'р.п.Ст.Майна',
	'р.п.Вешкайма',
	'р.п.Радищево',
	'г.Барыш',
	'г.Инза',
	'р.п.Ишеевка',
	'р.п.Николаевка',
	'р.п.Чердаклы',
	'г.Димитровград',
	'р.п.Новоспасское',
	'г.Сенгилей'],
	'Хабаровский край': ['г.Хабаровск',
	'г.Вяземский',
	'г.Бикин',
	'п.Переяславка',
	'г.Комсомольск-на-Амуре',
	'г.СоветскаяГавань'],
	'Еврейская автономная область': ['г.Биробиджан'],
	'Чукотский автономный округ': ['г.Анадырь'],
	'Магаданска яобласть': ['г.Магадан',
	'п.Палатка'],
	'Москва': ['г.Москва'],
	'Московская область': ['г.Сергиев-Посад',
	'г.Клин',
	'г.Люберцы',
	'г.Ногинск',
	'г.Коломна',
	'г.Серпухов',
	'г.Дмитров',
	'г.Можайск',
	'г.Подольск',
	'г.Домодедово',
	'г.Балашиха',
	'г.Химки',
	'г.Солнечногорск',
	'г.Ступино',
	'г.Одинцово',
	'г.Воскресенск',
	'г.Долгопрудный',
	'г.Жуковский',
	'г.Орехово-Зуево',
	'г.Шатура',
	'г.Красногорск',
	'г.Егорьевск',
	'г.Мытищи',
	'г.Электросталь'],
	'Челябинская область': ['г.Челябинск',
	'с.Аргаяш',
	'п.Бреды',
	'с.Варна',
	'с.Еткуль',
	'с.Кизильское',
	'с.Миасское',
	'с.Кунашак',
	'с.Фершампенуаз',
	'г.Сатка',
	'г.Троицк',
	'с.Уйское',
	'г.Чебаркуль',
	'п.Увельский',
	'г.Магнитогорск',
	'г.Аша',
	'г.Миасс'],
	'Курганская область': ['г.Курган',
	'г.Шумиха',
	'г.Куртамыш',
	'г.Петухово',
	'г.Катайск',
	'г.Шадринск',
	'г.Далматово',
	'г.Щучье',
	'р.п.Каргаполье',
	'с.Шатрово',
	'с.Мокроусово',
	'г.Макушино'],
	'Республика Чеченская': ['г.Грозный',
	'с.Знаменское',
	'г.Гудермес',
	'ст.Шелковская',
	'с.Ачхой-Мартан',
	'г.Шали',
	'г.Урус-Мартан',
	'г.Аргун',
	'ст.Наурская',
	'п.Гикало',
	'с.Курчалой',
	'с.Серноводск',
	'с.Шатой',
	'с.НожайЮрт',
	'с.Ведено'],
	'Забайкальский край': ['г.Чита',
	'г.Шилка',
	'г.Борзя',
	'п.КрасныйЧикой',
	'п.Приаргунск',
	'г.Нерчинск',
	'п.Агинское',
	'п.Могойтуй',
	'г.Петровск-Забайкальский',
	'п.Чернышевск',
	'с.Улеты',
	'пгт.Оловянная',
	'с.Акша',
	'г.Сретенск',
	'с.Дульдурга',
	'г.Краснокаменск'],
	'Республика Чувашия': ['г.Чебоксары',
	'г.Новочебоксарск',
	'г.Канаш',
	'с.Батырево',
	'с.Комсомольское',
	'с.Красноармейское',
	'п.Кугеси',
	'п.Вурнары',
	'г.Ядрин',
	'г.Шумерля',
	'с.Моргауши',
	'с.Шемурша',
	'г.Цивильск',
	'с.Яльчики',
	'п.Урмары',
	'г.Алатырь',
	'г.Козловка'],
	'Республика Саха': ['г.Якутск',
	'г.Вилюйск',
	'с.Намцы',
	'с.Борогонцы',
	'г.Покровск',
	'с.Ытык-Кюель',
	'г.Нюрба',
	'п.НижнийБестях',
	'с.Чурапча',
	'г.Олекминск',
	'п.Хандыга',
	'с.Верхневилюйск',
	'с.Амга',
	'г.Ленск',
	'с.Бердигестях'],
	'Ярославская область': ['г.Ярославль',
	'г.Гаврилов-Ям',
	'г.Мышкин',
	'г.Ростов',
	'с.Чурьяково',
	'г.Тутаев',
	'г.Рыбинск',
	'г.Переславль-Залесский']
}

    def is_in_odp_full(self, inn):
        return self.is_in_odp(inn)

    def is_in_odp(self, inn):
        res = requests.post("https://www.rshb.ru/ajax/inncheck/inncheck.php", data="companyinn={}".format(inn))

        if res.text == '\n"wrong"':
            return True

        return False

    def get_work_region_list(self):

        res = []

        for region in self.rgs:
            res.append({'ID': region, 'name': region})

        return res

    def is_multithread_odp(self):
        return False

    def get_work_region_city_list(self, region):

        res = []

        for city in self.rgs[region]:
            res.append({'ID': city, 'name': city})

        return res

