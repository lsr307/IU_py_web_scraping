def scrape_dwd(site):
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import TimeoutException
    import time 

    driver = webdriver.Chrome()
    driver.get(site)

    # Make dropdown for weather stations visible and select Berlin Tempelhof 
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID,'343278_select_cl2Categories_Station')))
    driver.execute_script("document.getElementById('343278_select_cl2Categories_Station').style.display='inline-block';")
    element = driver.find_element('id','343278_select_cl2Categories_Station')
    station = Select(element)
    station.select_by_value('klimadatendeutschland_berlintempelhof')

    # Wait for refresh of site
    time.sleep(3)

    # Make dropdown for periodicity visible and select Daily
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID,'343278_select_cl2Categories_ZeitlicheAufloesung')))
    driver.execute_script("document.getElementById('343278_select_cl2Categories_ZeitlicheAufloesung').style.display='inline-block';")
    element = driver.find_element('id','343278_select_cl2Categories_ZeitlicheAufloesung')
    periodicity = Select(element)
    periodicity.select_by_value('klimadatendeutschland_tageswerte')

    # Wait for refresh of site
    time.sleep(3)

    data = driver.find_element(By.XPATH,"//div[@class='content-container']") \
            .find_element(By.XPATH,"//div[@class='content data']")
    #Split data into rows
    data = data.text.split('\n')
    #Drop header rows
    del data[0:2]

    column_width = [5,8,2,6,6,6,6,6,6,6,6,6,6,6]
    data_list = []
    for j in range (0,len(data)):
        data_temp = []
        column_start = 0
        for i in range(0,len(column_width)):
            data_temp.append(data[j][column_start : column_start + column_width[i]])
            column_start += column_width[i] + 1
        data_list.append(data_temp)

    #TN = Minimum der Temperatur in 2 m über dem Erdboden = column 4
    #TM = Mittel der Temperatur in 2 m über dem Erdboden = column 5
    #TX = Maximum der Temperatur in 2 m über dem Erdboden = column 6
    #for i in data_list[0:10][:]:
    #    print(i[1], i[4], i[5], i[6])
    t_min = data_list[2][4]
    t_max = data_list[2][6]
    t_date = data_list[2][1]
    t_source = 0
    
    return [round(float(t_date),0), round(float(t_source),0), round(float(t_min),2), round(float(t_max),2)] 


def scrape_wetter_com(site):
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import TimeoutException
    import datetime
    import time 

    driver = webdriver.Chrome()
    driver.get(site)

    element = driver.find_element(By.XPATH,"//a[@data-label='VHSTabTag_2']") \
                    .find_element(By.CSS_SELECTOR,'span.forecast-navigation-temperature-max') 
    t_max = float(element.text.replace('°',''))

    element = driver.find_element(By.XPATH,"//a[@data-label='VHSTabTag_2']") \
                    .find_element(By.CSS_SELECTOR,'span.forecast-navigation-temperature-min') 
    t_min = float(element.text.replace('°',''))

    td = datetime.date.today()
    t_date = td.year*10000+td.month*100+td.day+1
    t_source = 1
    
    return [round(float(t_date),0), round(float(t_source),0), round(float(t_min),2), round(float(t_max),2)]  



def scrape_wetter_de(site):
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import TimeoutException
    import time 
    import datetime
    today = datetime.date.today().weekday()
    days = ['Mo','Di','Mi','Do','Fr','Sa','So']
    tomorrow = days[today+1]

    driver = webdriver.Chrome()
    driver.get(site)

    time.sleep(3)
    iframe = driver.find_element(By.XPATH,"//iframe[@id='sp_message_iframe_764638']")
    driver.switch_to.frame(iframe)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@title='Alle akzeptieren']"))).click()
    driver.switch_to.default_content()

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"//div[@data-day=\'{tomorrow}\']"))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, f"//div[@data-day=\'{tomorrow}\']"))).click()

    element = driver.find_element(By.CSS_SELECTOR,'div.weather-daybox-base__minMax__max')
    t_max = float(element.text)

    element = driver.find_element(By.CSS_SELECTOR,'div.weather-daybox-base__minMax__min')
    t_min = float(element.text)
    
    td = datetime.date.today()
    t_date = td.year*10000+td.month*100+td.day+1
    t_source = 2
    
    return [round(float(t_date),0), round(float(t_source),0), round(float(t_min),2), round(float(t_max),2)]  

def scrape_sites_append(file, website):
    import csv
    with open(file, 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows([[website]])
        csv_file.close()

def scrape_sites_open(file):
    import csv
    with open(file, 'r', newline='') as csv_file:
        reader = csv.reader(csv_file)
        data = []
        for x in reader:
            data.append(x[0])
        csv_file.close()
        return data
