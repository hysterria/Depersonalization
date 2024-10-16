import csv
import io
import pandas as pd
from pandas.io.formats.printing import PrettyDict


def de_name(dict):
    if dict['ФИО'][-1] =='а':
        dict['ФИО'] = 'Ж'
    else:
        dict['ФИО'] = 'М'

def de_passport(dict):
    s=dict['Паспортные данные']
    dict['Паспортные данные']='**** ******'

def de_marsh(dict):
    if dict['Откуда'] in ['Москва', 'Санкт-Петербург', 'Казань', 'Нижний Новгород', 'Самара', 'Ростов-на-Дону','Ижевск','Сарапул','Пермь','Нефтекамск','Анапа','Орёл']:
        dict['Откуда']='Европа'
    else:
        dict['Откуда']='Азия'
    if dict['Куда'] in ['Москва', 'Санкт-Петербург', 'Казань', 'Нижний Новгород', 'Самара', 'Ростов-на-Дону','Ижевск','Сарапул','Пермь','Нефтекамск','Анапа','Орёл']:
        dict['Куда']='Европа'
    else:
        dict['Куда']='Азия'

def de_train_type(dict):
    train_types = {
        'скорые поезда': range(1, 150),
        'сезонные поезда': range(151, 298),
        'пассажирские': range(301, 450),
        'сезонные пассажирские': range(451, 598),
        'скоростные': range(701, 750),
        'высокоскоростные': range(751, 788),
    }
    type=int(dict['Рейс'][:-1])
    for i in train_types.keys():
        if type in train_types[i]:
            dict['Рейс']=i

def de_wagon(dict):
    wagons_and_seats = {
        'Сапсан': ['1Р', '1В', '1С', '2С', '2В', '2E'],
        'Стриж': ['1Е', '1Р', '2С'],
        'Сидячий': ['1С', '1Р', '1В', '2Р', '2Е'],
        'Плацкарт': ['3Э'],
        'Купе': ['2Э'],
        'Люкс': ['1Б', '1Л'],
        'Мягкий': ['1А', '1И']
    }
    type=dict['Вагон и место'][:2]
    for i in wagons_and_seats.keys():
        if type in wagons_and_seats[i]:
            dict['Вагон и место']=i

def de_price(dict):
    price =int(dict['Стоимость'][:-2])
    if price < 1000:
        dict['Стоимость']='< 1000'
    elif 1000 <= price < 2000:
        dict['Стоимость']='1000 - 2000'
    elif 2000 <= price < 4000:
        dict['Стоимость']='2000 - 4000'
    elif 4000 <= price < 5000:
        dict['Стоимость']='4000 - 5000'
    else:
        dict['Стоимость']= '>=5000'

def de_card(dict):
    dict['Карта оплаты'] =dict['Карта оплаты'][:4]+ ' **** **** ****'

def de_date(dict):
    for i in ('Дата отъезда','Дата приезда'):
        if dict[i][5:7] in ('01','02','12'):
            dict[i]='Зима'

        elif dict[i][5:7] in ('03','04','05'):
            dict[i]='Весна'

        elif dict[i][5:7] in ('06','07','08'):
            dict[i]='Лето'

        else:
            dict[i]='Осень'



with io.open('train_tickets_dataset.csv', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)

    with io.open('new_train_tickets_dataset.csv', mode='w', encoding='utf-8', newline='') as newfile:
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(newfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            de_name(row)
            de_passport(row)
            de_train_type(row)
            de_wagon(row)
            de_price(row)
            de_card(row)
            de_date(row)
            de_marsh(row)
            writer.writerow(row)



def evaluate_data_utility(original_df: pd.DataFrame, anonymized_df: pd.DataFrame, quasi_identifiers: list):
    results = []

    for col in quasi_identifiers:
        original_unique = original_df[col].nunique()
        anonymized_unique = anonymized_df[col].nunique()
        utility_loss = (original_unique - anonymized_unique) / original_unique * 100
        results.append({
            'Квази-идентификатор': col,
            'Уникальные значения (исходные данные)': original_unique,                'Уникальные значения (обезличенные данные)': anonymized_unique,
            'Потеря полезности (%)': round(utility_loss, 2)
        })

    return pd.DataFrame(results)


def calculate_k_anonymity_from_dict(data_list, quasi_identifiers):
    # Преобразовать список словарей в DataFrame
    data = pd.DataFrame(data_list)

    # Сгруппировать данные по квазиидентификаторам
    grouped = data.groupby(quasi_identifiers).size().reset_index(name='count')

    # Вычислить k-анонимность (минимальный размер группы)
    k_anonymity = grouped['count'].min()

    # Отсортировать по возрастанию количества записей в группах
    worst_groups = grouped.sort_values(by='count', ascending=True).head(5)

    # Рассчитать процентное соотношение для топ-5 наименее анонимных групп
    total_records = len(data)
    worst_groups['percentage'] = (worst_groups['count'] / total_records) * 100

    return k_anonymity, worst_groups



with io.open('new_train_tickets_dataset.csv', encoding='utf-8') as csvfile:
    new_reader = list(csv.DictReader(csvfile))

    name = input('Имя(Y/n): ')
    from_to = input('Маршрут(Y/n): ')
    dates = input('Даты(Y/n): ')
    rout = input('Рейс(Y/n): ')
    wagon = input('Вагон(Y/n): ')
    price = input('Стоимость(Y/n): ')
    card = input('Карта(Y/n): ')

    k_identiti=[]
    if name == 'Y':
        k_identiti.append('ФИО')
    if from_to == 'Y':
        k_identiti.append('Откуда')
        k_identiti.append('Куда')
    if dates == 'Y':
        k_identiti.append('Дата отъезда')
        k_identiti.append('Дата приезда')
    if rout == 'Y':
        k_identiti.append('Рейс')
    if wagon == 'Y':
        k_identiti.append('Вагон и место')
    if price == 'Y':
        k_identiti.append('Стоимость')
    if card == 'Y':
        k_identiti.append('Карта оплаты')

    k_anonymity, worst_groups = calculate_k_anonymity_from_dict(new_reader, k_identiti)
    original_data = pd.read_csv("train_tickets_dataset.csv")
    anonymized_data = pd.read_csv("new_train_tickets_dataset.csv")
    utility_report = evaluate_data_utility(original_data, anonymized_data, k_identiti)

    print("k-анонимность:", k_anonymity)
    print("Топ 5:\n", worst_groups)

    print(utility_report)
    print(type(evaluate_data_utility(original_data, anonymized_data, k_identiti)))
    print(type(calculate_k_anonymity_from_dict(new_reader, k_identiti)))






