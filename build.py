import json
import urllib.request
from datetime import datetime

# GeoName ID per Milano (Garantisce coordinate esatte e fuso orario IT)
GEONAMEID = '3173435'

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'KindleZmanimBot/1.0'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode('utf-8'))

def extract_time(iso_string):
    """Estrae solo HH:MM da una stringa ISO 8601 (es. 2026-05-15T20:25:00+02:00)"""
    if not iso_string: return "N/D"
    return iso_string[11:16]

def format_date(iso_date):
    """Formatta la data da YYYY-MM-DD a DD/MM/YYYY"""
    try:
        d = datetime.strptime(iso_date, '%Y-%m-%d')
        return d.strftime('%d/%m/%Y')
    except:
        return iso_date

def main():
    # 1. Recupera gli Zmanim del giorno per Milano
    url_zmanim = f"https://www.hebcal.com/zmanim?cfg=json&geonameid={GEONAMEID}"
    zmanim_data = fetch_json(url_zmanim)
    times = zmanim_data['times']
    oggi = format_date(zmanim_data['date'])

    # 2. Recupera Parashah e orari di Shabbat (m=50 minuti per Havdallah)
    url_shabbat = f"https://www.hebcal.com/shabbat?cfg=json&geonameid={GEONAMEID}&m=50"
    shabbat_data = fetch_json(url_shabbat)

    parashah = "Nessuna Parashah"
    candles = "N/D"
    havdalah = "N/D"

    for item in shabbat_data.get('items', []):
        if item.get('category') == 'parashat':
            # Rimuove la scritta "Parashat" se presente per evitare ripetizioni
            parashah = item.get('title', 'N/D')
        elif item.get('category') == 'candles':
            candles = extract_time(item.get('date'))
        elif item.get('category') == 'havdalah':
            havdalah = extract_time(item.get('date'))

    # 3. Leggi il template
    with open('template.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 4. Sostituisci i placeholder con i dati reali
    html = html.replace('{{PARASHAH}}', parashah)
    html = html.replace('{{DATE}}', oggi)
    html = html.replace('{{CANDLES}}', candles)
    html = html.replace('{{HAVDALAH}}', havdalah)
    
    # Zmanim
    html = html.replace('{{ALOT}}', extract_time(times.get('alotHaShachar', '')))
    html = html.replace('{{NETZ}}', extract_time(times.get('sunrise', '')))
    html = html.replace('{{SHEMA_MA}}', extract_time(times.get('sofZmanShmaMGA', '')))
    html = html.replace('{{SHEMA_GRA}}', extract_time(times.get('sofZmanShma', '')))
    html = html.replace('{{CHATZOT}}', extract_time(times.get('chatzot', '')))
    html = html.replace('{{MINCHA}}', extract_time(times.get('minchaGedola', '')))
    html = html.replace('{{SHKIAH}}', extract_time(times.get('sunset', '')))
    # Per Tzait usiamo i 3 piccoli astri (circa 8.5 gradi o 50 min)
    html = html.replace('{{TZAIT}}', extract_time(times.get('tzeit853deg', ''))) 

    # 5. Salva il file finale
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == '__main__':
    main()
