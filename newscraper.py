from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd

# Enlace a NASA Exoplanet
START_URL = "https://exoplanets.nasa.gov/exoplanet-catalog/"

# Configuración del navegador
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ejecutar en modo headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
browser.get(START_URL)

time.sleep(10)

planets_data = []

# Definir el método de extracción de datos para Exoplanet
def scrape():
    for i in range(0, 10):
        print(f'Extrayendo página {i + 1} ...')

        # Objeto BeautifulSoup
        soup = BeautifulSoup(browser.page_source, "html.parser")

        # Bucle para encontrar los elementos usando el selector adecuado
        for div_tag in soup.find_all("div", class_="hds-content-item"):
            try:
                #Obtener el nombre del planeta
                name = div_tag.find("div", class_="hds-content-item-inner").find("a",class_="link-external-false hds-content-item-heading").find("h3",class_="heading-22 margin-0").text.strip()

                light_years_from_earth = ""
                planet_mass = ""
                stellar_magnitude = ""
                discovery_date = ""

                #Obtener los campos personalizados para iterar sobre ellos
                custom_fields = div_tag.find("div", class_="hds-content-item-inner").find_all("div", class_="CustomField")

                for index, div_tag_inner in enumerate(custom_fields):
                    try:
                        #Asume que los campos personalizados estan en el orden Años luz, Masa del Planeta, Magnitud Estelar y Fecha de Descubrimiento
                        if index == 0:
                            light_years_from_earth_tag = div_tag_inner.find("span", string="Light-Years From Earth: ")
                            light_years_from_earth = light_years_from_earth_tag.find_next_sibling().text.strip() if light_years_from_earth_tag else "N/A"
                        elif index == 1:
                            planet_mass_tag = div_tag_inner.find("span", string="Planet Mass: ")
                            planet_mass = planet_mass_tag.find_next_sibling().text.strip() if planet_mass_tag else "N/A"
                        elif index == 2:
                            stellar_magnitude_tag = div_tag_inner.find("span", string="Stellar Magnitude: ")
                            stellar_magnitude = stellar_magnitude_tag.find_next_sibling().text.strip() if stellar_magnitude_tag else "N/A"
                        elif index == 3:
                            discovery_date_tag = div_tag_inner.find("span", string="Discovery Date: ")
                            discovery_date = discovery_date_tag.find_next_sibling().text.strip() if discovery_date_tag else "N/A"

                    except Exception as e:
                        print(f"Error al extraer datos: {e}")

                #Adjunta los datos al arreglo de planetas
                planets_data.append([name,light_years_from_earth, planet_mass,stellar_magnitude,discovery_date])
            except Exception as e:
                print(f"Error al extraer datos: {e}")

        # Hacer clic para ir a la siguiente página
        try:
            next_button = browser.find_element(by=By.XPATH, value='//button[@class="next page-numbers"]')
            next_button.click()
            time.sleep(5)
        except Exception as e:
            print(f"No se pudo hacer clic en el botón de siguiente página: {e}")
            break

# Llamada del método
scrape()

# Definir los encabezados
#headers = ["name", "light_years_from_earth", "planet_mass", "stellar_magnitude", "discovery_date"]

headers = ["name","light_years_from_earth","planet_mass","stellar_magnitude","discovery_date"]

# Definir el dataframe de Pandas
planet_df_1 = pd.DataFrame(planets_data, columns=headers)

# Convertir a CSV
planet_df_1.to_csv('scraped_data.csv', index=True, index_label="id")

# Cerrar el navegador
browser.quit()
