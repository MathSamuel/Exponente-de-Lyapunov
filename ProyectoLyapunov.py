#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress

# Función para cargar los datos de tipo XLSX
def load_exchange_data(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df

#Funcion para calcular los rendimientos logarítmicos.
def log_returns(prices):
    return np.log(prices / prices.shift(1)).dropna()

#Funcion para calcular el exponente de Lyapunov mediante la separación de trayectorias.
def lyapunov_exponent(series, delta=1e-5):
    
    perturbed_series = series.copy()
    perturbed_series.iloc[0] += delta * series.iloc[0]  # Perturbación proporcional al valor inicial
    separation = np.abs(perturbed_series - series)
    t = np.arange(len(separation))
    slope, _, _, _, _ = linregress(t, separation)
    return slope

# Cargar datos desde el archivo XLSX
file_path = "data_2000_2023.xlsx"
sheet_name = "datos"
df = load_exchange_data(file_path, sheet_name)

if df is not None:
    print("Datos cargados correctamente.")
    print("Países únicos en los datos:", df['País__ESTANDAR'].unique())

    # Calcular el promedio anual de las tasas de cambio para cada país
    annual_rates = df.groupby(['Años__ESTANDAR', 'País__ESTANDAR'])['value'].mean().unstack()

    # Seleccionar las tasas de cambio para los países
    countries = ['Chile', 'Colombia', 'Perú', 'México', 'Panamá']
    exchange_rates = {country: annual_rates[country].dropna() for country in countries if country in annual_rates.columns}

    # Mostrar resumen de los datos encontrados
    for country, rates in exchange_rates.items():
        print(f"Datos encontrados para {country}: {len(rates)} registros.")

    # Calcular exponentes de Lyapunov para cada país
    lyap_exponents = {}
    for country, rates in exchange_rates.items():
        returns = log_returns(rates)
        if not returns.empty and len(returns) > 1:  # Verificar que haya suficientes datos
            try:
                lyap_exponents[country] = lyapunov_exponent(returns)
            except ValueError as e:
                print(f"Error al calcular el exponente de Lyapunov para {country}: {e}")
        else:
            print(f"Advertencia: No hay suficientes datos para calcular el exponente de Lyapunov para {country}.")

    # Determinar el país con la mayor inestabilidad
    positive_lyap = {k: v for k, v in lyap_exponents.items() if v > 0}
    if positive_lyap:
        most_chaotic = max(positive_lyap, key=positive_lyap.get)
        print(f"La moneda más caótica frente al USD es: {most_chaotic}")
    else:
        print("No hay monedas con comportamiento caótico.")

    # Visualización de tasas de cambio anuales
    if exchange_rates:
        plt.figure(figsize=(12, 6))
        for country, rates in exchange_rates.items():
            plt.plot(rates.index, rates, label=country) 
        plt.title("Tasas de cambio anuales frente al USD")
        plt.xlabel("Año")
        plt.ylabel("Tasa de cambio promedio")
        plt.legend() 
        plt.grid()
        plt.show()

    # Visualización de exponentes de Lyapunov
    if lyap_exponents:
        plt.figure(figsize=(8, 5))
        plt.bar(lyap_exponents.keys(), lyap_exponents.values(), color='skyblue')
        plt.title("Exponentes de Lyapunov por país")
        plt.xlabel("País")
        plt.ylabel("Exponente de Lyapunov")
        plt.grid(axis='y')
        plt.show()

    # Resultados en tabla
    if lyap_exponents:
        results_df = pd.DataFrame.from_dict(lyap_exponents, orient='index', columns=['Exponente de Lyapunov'])
        print(results_df)

