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
    ##TM = Mittel der Temperatur in 2 m über dem Erdboden = column 5
    #TX = Maximum der Temperatur in 2 m über dem Erdboden = column 6

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
    if today == 6:
        tomorrow = days[today-6]
    else:
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

def plot_scraped_data(file):
    import matplotlib.pyplot as plt
    import h5py
    import numpy as np
    import datetime
    import pandas as pd
    from datetime import timedelta

    file = h5py.File(file,'r+')
    dframe_fl = pd.DataFrame(np.array(file['data_float']))
    dframe_fl.columns = ['date','location','t_min','t_max']

    list_fl = []
    #Only include dates for which  
    for x in range(int(file['data_float'][:,0].min())+2,int(file['data_float'][:,0].max())-1):
        list_fl.append([x,\
                        dframe_fl.loc[(dframe_fl['date']==x) & (dframe_fl['location']==0),['t_min']].values[0][0],\
                        dframe_fl.loc[(dframe_fl['date']==x) & (dframe_fl['location']==0),['t_max']].values[0][0],\
                        dframe_fl.loc[(dframe_fl['date']==x) & (dframe_fl['location']==1),['t_min']].values[0][0],\
                        dframe_fl.loc[(dframe_fl['date']==x) & (dframe_fl['location']==1),['t_max']].values[0][0],\
                        dframe_fl.loc[(dframe_fl['date']==x) & (dframe_fl['location']==2),['t_min']].values[0][0],\
                        dframe_fl.loc[(dframe_fl['date']==x) & (dframe_fl['location']==2),['t_max']].values[0][0],\
                       ]
                      )

    dframe_clean = pd.DataFrame(list_fl)

    columns = ['Date',\
               'Temp. Min. (DWD)',\
               'Temp. Max. (DWD)',\
               'Temp. Min. (wetter.com)',\
               'Temp. Max. (wetter.com)',\
               'Temp. Min. (wetter.de)',\
               'Temp. Max. (wetter.de)'
              ]

    dframe_clean.columns = columns      

    dframe_clean['Date'] = pd.to_datetime(dframe_clean['Date'], format='%Y%m%d')

    dframe_clean['Absolute Diff. wetter.com'] = (abs(dframe_clean['Temp. Max. (wetter.com)']\
                                                    - dframe_clean['Temp. Max. (DWD)']\
                                                   )\
                                                + abs(dframe_clean['Temp. Min. (wetter.com)']\
                                                    - dframe_clean['Temp. Min. (DWD)']\
                                                     )
                                                )

    dframe_clean['Absolute Diff. wetter.de'] = (abs(dframe_clean['Temp. Max. (wetter.de)']\
                                                    - dframe_clean['Temp. Max. (DWD)']\
                                                  )\
                                                + abs(dframe_clean['Temp. Min. (wetter.de)']\
                                                    - dframe_clean['Temp. Min. (DWD)']\
                                                     )       
                                               )

    # Create a figure and a set of subplots
    fig, ax = plt.subplots()

    # Plot a bar chart
    #ax.bar(x, y1, color='b', alpha=0.5, label='Bar')

    # Set width of the bars
    width = 0.3  

    ax.bar(dframe_clean['Date'],\
           dframe_clean['Absolute Diff. wetter.com'],\
           width,\
           label='Absolute Diff. wetter.com',\
           color=(1,0,0),\
          )

    ax.bar(dframe_clean['Date']+timedelta(hours=8),\
           dframe_clean['Absolute Diff. wetter.de'],\
           width,\
           label='Absolute Diff. wetter.de',\
           color=(0,0,1)
          )

    # Plot a line chart
    #ax.plot(x, y2, color='r', marker='o', label='Line')
    ax.plot(dframe_clean['Date'],\
             dframe_clean['Temp. Min. (DWD)'],\
             linestyle='dotted',\
             color=(0,1,0)
            )
    ax.plot(dframe_clean['Date'],\
             dframe_clean['Temp. Max. (DWD)'],\
             linestyle='dotted',\
             color=(0,1,0),\
             label='DWD (actual)',\
            )
    ax.plot(dframe_clean['Date'],\
             dframe_clean['Temp. Min. (wetter.com)'],\
             linestyle='dotted',\
             color=(1,0,0)
            )
    ax.plot(dframe_clean['Date'],\
             dframe_clean['Temp. Max. (wetter.com)'],\
             linestyle='dotted',\
             label='Wetter.com (forecast)',\
             color=(1,0,0)
            )
    plt.plot(dframe_clean['Date'],\
             dframe_clean['Temp. Min. (wetter.de)'],\
             linestyle='dotted',\
             color=(0,0,1)
            )
    plt.plot(dframe_clean['Date'],\
             dframe_clean['Temp. Max. (wetter.de)'],\
             linestyle='dotted',\
             label='Wetter.de (forecast)',\
             color=(0,0,1)
            )

    # Add a legend
    plt.legend(loc="upper center",\
               fontsize=7)
    ax.set(xlabel='Date',\
           ylabel='Temperature',\
           title='Min. and max. temperature forecasts and actuals',\
          )

    # Rotate the tick labels
    plt.setp(ax.get_xticklabels(),\
             rotation=45,\
             ha="right",rotation_mode="anchor"
            )

    # Show the plot
    plt.show()

    # Save the plot
    fig.savefig('IU_web_scrape_Linechart.png',bbox_inches='tight')


    #sum_row = dframe_clean['Absolute Diff. wetter.com'

    print(dframe_clean[['Date',\
                        'Absolute Diff. wetter.com',\
                        'Absolute Diff. wetter.de',\
                       ]
                      ]
         ,'\n'
         )

    print(f'Total difference for wetter.com: {round(dframe_clean["Absolute Diff. wetter.com"].sum(),2)} degrees')
    print(f'Total difference for wetter.de: {round(dframe_clean["Absolute Diff. wetter.de"].sum(),2)} degrees')

    file.close()


def execute_scrape(file_data_sources,file_data_storage):
    import h5py
    import numpy as np
    from IU_scrape_func import scrape_dwd
    from IU_scrape_func import scrape_wetter_com
    from IU_scrape_func import scrape_wetter_de
    from IU_scrape_func import scrape_sites_append
    from IU_scrape_func import scrape_sites_open
    import datetime

    file_name_sites = file_data_sources
    file_name_data = file_data_storage
    ds_name_fl = 'data_float'
    ds_name_st = 'data_string'

    #Create csv file with websites to scrape
    #websites = ['https://www.dwd.de/DE/leistungen/klimadatendeutschland/klimadatendeutschland.html',
    #            'https://www.wetter.com/wetter_aktuell/wettervorhersage/morgen/deutschland/berlin/berlin-tempelhof/DE2823538.html',
    #            'https://www.wetter.de/wetter/r/162894/diese-woche'
    #           ]
    #for x in websites:
    #    scrape_sites_append(file_name_sites, x)

    #Open csv file with websites to scrape
    sites = scrape_sites_open('IU_scrape_sites.csv')

    #Create & open file if it does not exist
    try:
        file = h5py.File(file_name_data,'r+')
    except FileNotFoundError:
        file = h5py.File(file_name_data,'w')    

    #Created datasets if they do not exist
    if not ds_name_fl in list(file.keys()):
        dset_fl = file.create_dataset(ds_name_fl, (0,4), maxshape=(None,4), dtype = 'float64') 
    else:
        dset_fl = file[f'/{ds_name_fl}']

    if not ds_name_st in list(file.keys()):
        dt = h5py.string_dtype(encoding='utf-8')
        dset_st = file.create_dataset(ds_name_st, (0,3), maxshape=(None,3), dtype = dt) 
    else:
        dset_st = file[f'/{ds_name_st}']

    if not dset_fl.shape[0] == dset_st.shape[0]:
        print('Dataset-lengths do not correspond!')

    data_fl = np.array([scrape_dwd(sites[0]),scrape_wetter_com(sites[1]),scrape_wetter_de(sites[2])])
    data_st = np.array([[datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"),'DWD','0'], \
                        [datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"),'Wetter.com','1'], \
                        [datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"),'Wetter.de','2']
                       ]
                      )

    dset_st.resize(dset_st.shape[0]+3, axis=0)
    dset_fl.resize(dset_fl.shape[0]+3, axis=0)
    dset_st[dset_st.shape[0]-3:dset_st.shape[0],:] = data_st
    dset_fl[dset_fl.shape[0]-3:dset_fl.shape[0],:] = data_fl

    #To get rid of b: .decode("utf-8")
    #for x in range(0,len(dset_st)):
    #    print(dset_st[x,:], dset_fl[x,:])

    print(dset_fl[...])
    print(dset_st[...])

    #Close file
    file.close()
