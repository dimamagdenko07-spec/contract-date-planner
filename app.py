import pandas as pd
import streamlit as st
import requests
from datetime import date

st.set_page_config(page_title='План закупки', page_icon='RU')

@st.cache_data
def get_ru_calendar(year):
    #Функция получения официального календаря РФ
    try:
        response = requests.get(f"https://isdayoff.ru/api/getdata?year={year}")
        if response.status_code == 200:
            days = response.text
            base_date = date(year, 1, 1)
        holidays = []
        extra_workdays = []

        for i, day_type in enumerate(days):
            current_day = pd.to_datetime(base_date) + pd.Timedelta(days=i)
            #Выходной
            if day_type == '1':
                holidays.append(current_day)

            if day_type == '0' and current_day.weekday() >= 5:
                extra_workdays.append(current_day)
        return holidays, extra_workdays
    except:
        print(1)
        return [], []

st.title('Планировщик дат')

#Ввод
target_date = st.date_input('Дата заключения договора:', value=date(2026, 11, 2))
if target_date:
    target_year = target_date.year
    #Получаем календарь
    h_2025, w_2025 = get_ru_calendar(target_year-1)
    h_2026, w_2026 = get_ru_calendar(target_year)
    all_holidays = h_2025 + h_2026
    all_workdays = w_2025 + w_2026
    #Создаём русский календарь
    russian_bussiness_days = pd.offsets.CustomBusinessDay(
        holidays=all_holidays,
        weekmask='Mon Tue Wed Thu Fri Sat Sun' 
    )
    #Начинаем вычисление
    step_4 = pd.to_datetime(target_date)
    planning_deadline = target_date - russian_bussiness_days * 49
    #Находим такой первый рабочий день месяца, чтобы до нашей даты дедлайна было хотя бы 5 рабочих дней
    first_day = (planning_deadline - russian_bussiness_days * 5).replace(day=1)
    step_3_start  = first_day if first_day not in all_holidays else first_day + (russian_bussiness_days * 0)
    step_2_start = step_3_start  - russian_bussiness_days * 5
    step_1_start = step_2_start - russian_bussiness_days * 10

    data = [
        {'Этап' : '1. Согласование проекта договора и ТЗ для закупки', 'Дата начала' : step_1_start.strftime('%d.%m.%Y')},
        {'Этап' : '2. Направление закупки в профильный департамент', 'Дата начала' : step_2_start.strftime('%d.%m.%Y')},
        {'Этап' : '3. Начало периода планирования', 'Дата начала' : step_3_start.strftime('%d.%m.%Y')},
        {'Этап' : '4. Начало заключения договора', 'Дата начала' : planning_deadline.strftime('%d.%m.%Y')},
        {'Этап' : '5. Дедлайн заключения договора', 'Дата начала' : step_4.strftime('%d.%m.%Y')}
    ]
    st.table(pd.DataFrame(data))