# Fallen

## Overview
Fallen Financial Tools es una recopilación de herramientas creadas mayormente por [St1tch](https://twitter.com/St1tch_BL), [Franco Lamas](https://www.linkedin.com/in/franco-lamas/) y Marcelo Colom.

## Fuentes

| Sitio | Datos|
| ------------ | :------------: |
|Cohen | Históricos|
|Yahoo Finance |Históricos|
|Rava Bursátil | Históricos|
|Ambito Financiero | Dolar Blue, Oficial y Solidario|
|Macrotrends |Históricos, Balances|

## Metodos
### Yahoo Finance
Ejemplo de data histórica:

    from Fallen import *
    
    #Fechas en formato Año-Mes-Día como string
    yahoo.get_history("GGAL.BA","2020-01-01","2021-12-01")
    
### Ambito Financiero
Ejemplo 

      from Fallen import *
      
      #Fechas en formato Año-Mes-Día como string
      ambito.dolar_blue("2016-10-01","2021-01-04")
El mismo metodo es valido tamto para dolar_oficial y dolar_solidario

### Rava Bursátil
Ejemplo 

    from Fallen import *
    
    #Fechas en formato Año-Mes-Día como string
    rava.get_history("GGAL","2020-01-01","2021-12-01")

### Macrotrends


### Cohen
Metodos disponibles:

- stocks(Acciones)
- fixed_income(Renta Fija)
- options(Opciones)
- cedears(CEDEARs)

Ejemplo

    from Fallen import *
    
    #Fechas en formato Año-Mes-Día como string
    cohen.stocks("GGAL","2023-09-01","2023-11-01")

### Macrotrends
Ejemplo de data histórica:

    from Fallen import *
    
    #Trae todo el histórico disponible, no se necesita especificar fecha.
    macrotrends.history("SPY")
    
Ejemplo de balances:

    from Fallen import *
    
    #freq es un parametro opcional, puede ser solo 'Q'(por defecto) o 'A'
    macrotrends.incomes("GGAL",freq='A')

## Colaboradores

[Paduel](https://github.com/paduel)

## Installation


    pip install Fallen==0.6.0

    pip install git+https://github.com/franco-lamas/Fallen --upgrade --no-cache-dir


## DISCLAIMER

La información es mostrada “tal cual es”, puede ser incorrecta o contener errores, eso es responsabilidad de cada sitio. No somos responsables por el uso indebido de los Scripts.
