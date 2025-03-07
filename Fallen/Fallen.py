# -*- coding: utf-8 -*-
#Fallen Financial Tools es una recopilacion de distintas herramientas para el analisis de activos, enfocadas en el mercado Argentino.

import pandas as pd
from datetime import datetime
import datetime
from pytz import timezone
import requests
import re
import json
import numpy as np 
import io
import urllib3

urllib3.disable_warnings()


class yahoo:
  def get_history(ticker,date_start,date_end):
    newyork_tz = timezone('America/New_York')
    var = date_start.split("-")
    var = list(map(int, var))
    p1 = str(int(newyork_tz.localize(datetime.datetime(var[0],var[1],var[2], 8, 0, 0)).timestamp()))

    var = date_end.split("-")
    var = list(map(int, var))
    p2 = str(int(newyork_tz.localize(datetime.datetime(var[0],var[1],var[2], 8, 0, 0)).timestamp()))

    url = f"https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={p1}&period2={p2}&interval=1d&events=history&includeAdjustedClose=true"
    df = pd.read_csv(url)
    return df



class ambito:
    BASE_URL = "https://mercados.ambito.com/"
    HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    @staticmethod
    def format_date(date_str):
        day, month, year = date_str.split("-")
        return f"{year}-{month}-{day}"
    
    @classmethod
    def fetch_data(cls, endpoint, start_date, end_date):
        
        url = f"{cls.BASE_URL}{endpoint}/historico-general/{cls.format_date(start_date)}/{cls.format_date(end_date)}"
        response = requests.get(url,headers=cls.HEADERS)
        data = response.json()
        
        df = pd.DataFrame(data)
        df.columns = df.loc[0]
        df = df.drop(labels=0, axis=0)
        
        if 'Compra' in df.columns:
            df['Compra'] = df['Compra'].str.replace(",", ".").astype(float)
        
        if 'Venta' in df.columns:
            df['Venta'] = df['Venta'].str.replace(",", ".").astype(float)
        
        df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')
        df.sort_values(by=['Fecha'], inplace=True)
        df = df.drop_duplicates(subset=['Fecha']).reset_index(drop=True)
        
        return df
    
    @classmethod
    def dolar_blue(cls, start_date, end_date):
        return cls.fetch_data("dolar/informal", start_date, end_date)
    
    @classmethod
    def dolar_oficial(cls, start_date, end_date):
        return cls.fetch_data("dolar/oficial", start_date, end_date)
    
    @classmethod
    def dolar_solidario(cls, start_date, end_date):
        return cls.fetch_data("dolarturista", start_date, end_date)


class rava:
  def get_history(ticker,start_date,end_date):
    s = requests.Session()

    def strbetw(text, left, right):
      match = re.search( left + '(.*?)' + right, text)
      if match:  
        return match.group(1)
      return ''

    url = "https://www.rava.com"
    headers = {
        "Host" : "www.rava.com",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language" : "en-US,en;q=0.5",
        "Accept-Encoding" : "gzip, deflate, br",    
        "DNT" : "1",
        "Connection" : "keep-alive",      
        "Upgrade-Insecure-Requests" : "1",
        "Sec-Fetch-Dest" : "document",
        "Sec-Fetch-Mode" : "navigate",
        "Sec-Fetch-Site" : "none",
        "Sec-Fetch-User" : "?1"
        }

    response = s.get(url = url, headers = headers)
    status = response.status_code
    if status != 200:
      print("login status", status)  
      exit()

    access_token = strbetw(response.text, ":access_token=\"\'", "\'\"")

    url = "https://clasico.rava.com/lib/restapi/v3/publico/cotizaciones/historicos"

    data = {
      "access_token": access_token, # - Parece que dura 30 minutos 
      "especie": ticker, #Ticker
      "fecha_inicio": start_date, #Para que traiga todo
      "fecha_fin": end_date#Para que traiga todo
    }
    headers = {
        "Host" : "clasico.rava.com",
        "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Accept" : "*/*",
        "Accept-Language" : "en-US,en;q=0.5",
        "Accept-Encoding" : "gzip, deflate",
        "Content-Type" : "application/x-www-form-urlencoded",
        "Origin" : "https://datos.rava.com",
        "DNT" : "1",
        "Connection" : "keep-alive",
        "Referer" : "https://datos.rava.com/",    
        "Sec-Fetch-Dest" : "empty",
        "Sec-Fetch-Mode" : "cors",
        "Sec-Fetch-Site" : "same-site"    
    }
    response = s.post(url = url, headers = headers, data = data)
    status = response.status_code
    if status != 200:
      print("form status", status)
      exit()
    quots=(pd.DataFrame(json.loads(response.text)['body']))
    quots.rename({'cierre': 'close','fecha':'date','apertura':'open','maximo':'high','minimo':'low','volumen':'volume'}, axis=1, inplace=True)

    quots=quots[['date',	'open',	'high',	'low',	'close',	'volume',	'timestamp']].copy()
    return quots

class macrotrends:
  def get_symbols():
      url = 'https://www.macrotrends.net/assets/php/ticker_search_list.php'
      response = requests.get(url)

      symbols = pd.DataFrame(response.json())
      symbols.index = symbols['s'].str.split('/').str[0]
      symbols['name'] = symbols['s'].str.split('/').str[1]
      return symbols

  def incomes(symbol, freq='Q'):
      symbols = macrotrends.get_symbols()

      url = f'https://www.macrotrends.net/stocks/charts/{symbol}/{symbols["name"]}/income-statement?freq={freq}'
      response = requests.get(url)
      content = response.content.decode('utf8','ignore')
      info = content.split('var originalData = ')[1].split(';\r\n\r\n\r\n')[0]
      if not info == 'null':
        data = pd.DataFrame(json.loads(info))
        data['field_name'] = data['field_name'].str.split('>').str[1].str.split('<').str[0]
        data = data.set_index('field_name').iloc[:,1:]
        data = data.replace('', 0).astype(float).replace(0, pd.NA).dropna(how='all', axis=0).T
        data.index = pd.to_datetime(data.index, format='%Y-%m-%d')
        data.columns.name = None
      else:
        print('Símbolo sin información disponible')
        data= None
      return data

  def history(symbol):
    url = f'https://www.macrotrends.net/assets/php/stock_data_download.php?s=61b72cbe23226&t={symbol}'
    response = requests.get(url)
    content = response.content.decode('ascii')
    csv_string = content.split('displayed on a web page."\n\n\n')[1]
    data = pd.read_csv(io.StringIO(csv_string), index_col=0)
    data.index = pd.to_datetime(data.index, format='%Y-%m-%d')
    return data

class cohen:
    session = requests.Session()  # Sesión compartida entre todos los métodos
    headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
    
    @staticmethod
    def _format_date(date_str):
        """Convierte la fecha de formato YYYY-MM-DD a DD/MM/YYYY"""
        return pd.to_datetime(date_str).strftime('%d/%m/%Y')

    @staticmethod
    def _get_data(grupo):
        """Obtiene los datos base de cotización para un grupo dado"""
        url = 'https://www.cohen.com.ar/Financial//ListCotizacion'
        data = {"grupo": grupo, "especieTipo": "", "campoOrden": "SIMBOLO", "sentidoOrden": "ASC"}
        
        # Realizar la solicitud y verificar respuesta
        response = cohen.session.post(url=url, headers=cohen.headers, data=data, verify=False)
        if response.status_code != 200:
            raise ValueError(f"Error en la solicitud, código de estado: {response.status_code}")
        
        return pd.DataFrame(response.json()["CotizacionList"])

    @staticmethod
    def _get_historical_data(idEspecie, start_date, end_date):
        """Solicita los datos históricos de cotizaciones para un idEspecie específico"""
        url = "https://www.cohen.com.ar/Financial/GetTablaCotizacionesHistoricas"
        data = {
            "idEspecie": idEspecie, 
            "fechaDesde": cohen._format_date(start_date), 
            'fechaHasta': cohen._format_date(end_date)
        }
        
        response = cohen.session.post(url=url, headers=cohen.headers, data=data, verify=False)
        if response.status_code != 200:
            raise ValueError(f"Error en la solicitud de datos históricos, código de estado: {response.status_code}")
        
        df = pd.DataFrame(response.json())
        df = df[["FechaString", "PrecioUltimo", "PrecioApertura", "PrecioMaximo", "PrecioMinimo", "VolumenNominal"]]
        df.columns = ["date", "close", "open", "high", "low", "volume"]
        df.date = pd.to_datetime(df.date.astype(str), format='%d/%m/%Y')
        return df

    @staticmethod
    def stocks(ticker, start_date, end_date):
        """Obtiene los datos de acciones"""
        df = cohen._get_data(grupo="ACCIONES")
        df["Simbolo"] = df["Simbolo"].apply(lambda x: x.split("-")[0])
        idEspecie = df.set_index("Simbolo").at[ticker+" ", "IdEspecie"]
        return cohen._get_historical_data(idEspecie, start_date, end_date)

    @staticmethod
    def cedears(ticker, start_date, end_date):
        """Obtiene los datos de CEDEARs"""
        df = cohen._get_data(grupo="CEDEARS")
        df["Simbolo"] = df["Simbolo"].apply(lambda x: x.split("-")[0])
        idEspecie = df.set_index("Simbolo").at[ticker+" ", "IdEspecie"]
        return cohen._get_historical_data(idEspecie, start_date, end_date)

    @staticmethod
    def fixed_income(ticker, start_date, end_date):
        """Obtiene los datos de renta fija"""
        df = cohen._get_data(grupo="RENTAFIJA")
        df["Simbolo"] = df["Simbolo"].apply(lambda x: x.split("-")[0])
        idEspecie = df.set_index("Simbolo").at[ticker+" ", "IdEspecie"]
        return cohen._get_historical_data(idEspecie, start_date, end_date)

    @staticmethod
    def options(ticker, start_date, end_date):
        """Obtiene los datos de opciones"""
        df = cohen._get_data(grupo="OPCIONES")
        df["Simbolo"] = df["Simbolo"].apply(lambda x: x.split("-")[0])
        idEspecie = df.set_index("Simbolo").at[ticker+" ", "IdEspecie"]
        return cohen._get_historical_data(idEspecie, start_date, end_date)
