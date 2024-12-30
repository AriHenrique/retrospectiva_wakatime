import pygal
import requests
from pygal.style import Style
import json
import os


def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['data']
    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer requisição para {url}: {e}")
        return None


def format_hours(minutes):
    whole_hours = int(minutes)
    minutes = (minutes - whole_hours) * 60
    return f'{whole_hours}hrs {int(minutes)}min'


waka_api_key = os.getenv('WAKA')
base = 'https://wakatime.com'

stats_url = f'{base}/api/v1/users/current/stats/last_year?api_key={waka_api_key}'
dados = fetch_data(stats_url)

if not dados:
    print("Falha ao obter dados.")
    exit(1)

total_horas = round(dados['total_seconds'] / 60 / 60, 2)
linguagens = dados['languages']
melhor_dia = dados['best_day']


def max_mes_horas():
    meses = dict()
    for i in range(1, 13):
        mes_url = f'{base}/api/v1/users/current/stats/2024-{i:02d}?api_key={waka_api_key}'
        mes = fetch_data(mes_url)
        if mes:
            meses[mes['human_readable_range']] = round(mes['total_seconds'] / 60 / 60, 2)
    if meses:
        max_month = max(meses, key=meses.get)
        max_value = meses[max_month]
        return {max_month: max_value}
    return {}


def filter_languages(dados: list):
    lang_hours = dict()
    for dado in dados:
        hours = dado['total_seconds'] / 60 / 60
        if hours > 1:
            lang_hours[dado['name']] = round(hours, 2)
    return lang_hours


languages = filter_languages(linguagens)

custom_style = Style(
    background='transparent',
    plot_background='transparent',
    foreground='black',
    foreground_strong='black',
    foreground_subtle='black',
    opacity='.9',
    opacity_hover='.2',
    transition='400ms ease-in-out'
)

format_langs = {language: format_hours(hours) for language, hours in languages.items()}

pie_chart = pygal.Pie(style=custom_style, inner_radius=0.6)
for language, hours in languages.items():
    pie_chart.add(f'{language} ({format_hours(hours)})', hours)

pie_chart.legend_at_bottom = True
pie_chart.legend_spacing = 50
pie_chart.legend_box_size = 15

pie_chart.render_to_file('static/programming_languages_time.svg')

total_hours = format_hours(total_horas)

max_mes = max_mes_horas()
max_mes_name = list(max_mes.keys())[0] if max_mes else "N/A"
max_mes_hours = format_hours(list(max_mes.values())[0]) if max_mes else "N/A"

data = {
    "total_hours": total_hours,
    "max_day": melhor_dia['date'],
    "max_day_hours": melhor_dia['text'],
    "max_month": max_mes_name,
    "max_month_hours": max_mes_hours,
    "languages": format_langs
}

with open('static/data.json', 'w') as f:
    json.dump(data, f, indent=4)

print("JSON e SVG gerados com sucesso!")
