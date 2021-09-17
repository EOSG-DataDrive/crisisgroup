import datetime
import logging
import azure.functions as func
import sys
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import pandas as pd
import csv
import re

def main(mytimer: func.TimerRequest,crisisgroup:func.Out[func.InputStream]) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    df = pd.DataFrame(columns=['Country','Time','Description','Flag'])

    nextline = []
    temp =''
    for year in list(range(2003,2020)):
        for page in list(range(50)):
            page=str(page)
            link='https://www.crisisgroup.org/crisiswatch/database?page='+page+'&date_range=custom&from_month='+'01'+'&from_year='+str(year)+'&to_month='+'01'+'&to_year='+str(year+1)
            #link = 'https://www.crisisgroup.org/crisiswatch/database?date_range=custom&from_month=01&from_year=2004&to_month=01&to_year=2003'
            headers = {'User-Agent': 'Mozilla/5.0'}
            respo = requests.post(link,headers=headers)
            soup = BeautifulSoup(respo.text, 'html.parser')
            h3s = soup.find_all('h3',{"class": "[ u-df u-aic ]"})
            times = soup.find_all('time',{"class": "u-ttu u-fs13 u-fwn u-db u-gray--light u-mar-t10"})
            descriptions=soup.find_all('div',{'class':'o-crisis-states__detail [ u-ptserif u-fs18 ]'})
            #print(len(h3s),len(times),len(descriptions))

            if not h3s:
                break 

            if (len(h3s)==len(times)) and (len(times)==len(desscriptions)):
                pass
            else:
                print('length error!!!!!! redo this page')
                        
            emptyindex=-1
            for index,h3 in enumerate(h3s):
                if h3.text.strip()=='':
                    emptyindex=index
                    break
            if emptyindex!=-1:
                del h3s[emptyindex]
                del times[emptyindex]
                print('length error solved')

                
            for index,h3 in enumerate(h3s):
                flaglist = []
                h3txt = h3.text.strip()

                datetxt = times[index].text
                desctxt = descriptions[index].find('p')
                if desctxt == None:
                    desctxt ='No description'
                else:
                    desctxt = desctxt.text.strip()


                flags=h3.find_all('span',{"class": "o-icon [ u-mar-r5 ]"})
                for flag in flags:
                    index1=str(flag).find('#')
                    index2=str(flag).find('></use></svg></span>')
                    flaglist.append(str(flag)[index1+1:index2-1])

                nextline.append([h3txt,datetxt,desctxt,flaglist])

#for i in range(0,len(nextline)):
    #print(nextline[i])

    df = pd.DataFrame(nextline,columns=['Country','Date','Description','Status'])
    df['Status'] = [','.join(map(str, l)) for l in df['Status']]
    #df.to_csv("C:\\Users\\sanjana\\Desktop\\Crisis Group\\crisisgroupdata.csv",index=False,encoding='utf-8-sig')

                    
    dfcsv = df.to_csv(index=False)
    
    crisisgroup.set(dfcsv)
    logging.info("completed")
