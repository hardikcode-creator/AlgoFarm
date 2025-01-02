import numpy as np
# from nsepythonserver import *

import smtplib
import ssl
import warnings
from datetime import date,datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from holiday import check_holiday
import pandas as pd
import os

warnings.filterwarnings("ignore")

path = os.path.dirname(os.path.realpath(__file__))
# print("bulkdeal",path)
sender = "algofarm014@gmail.com"
receiver = "surbhialgo2212@gmail.com"
receiver2="hardikagrawal0045@gmail.com"
context = ssl.create_default_context()
email_password = "cead vlgq vxce xobs"
listFO = pd.read_csv(path+"/FO_list.csv")
listFO.dropna(inplace=True)
curl_headers = ''' -H "authority: beta.nseindia.com" -H "cache-control: max-age=0" -H "dnt: 1" -H "upgrade-insecure-requests: 1" -H "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36" -H "sec-fetch-user: ?1" -H "accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9" -H "sec-fetch-site: none" -H "sec-fetch-mode: navigate" -H "accept-encoding: gzip, deflate, br" -H "accept-language: en-US,en;q=0.9,hi;q=0.8" --compressed'''
def nsefetch(payload):
        if (("%26" in payload) or ("%20" in payload)):
            encoded_url = payload
        else:
            encoded_url = urllib.parse.quote(payload, safe=':/?&=')
        payload_var = 'curl -b cookies.txt "' + encoded_url + '"' + curl_headers + ''
        try:
            output = os.popen(payload_var).read()
            output=json.loads(output)
        except ValueError:  # includes simplejson.decoder.JSONDecodeError:
            payload2 = "https://www.nseindia.com"
            output2 = os.popen('curl -c cookies.txt "'+payload2+'"'+curl_headers+'').read()
    
            output = os.popen(payload_var).read()
            output=json.loads(output)
        return output
def email_strat(data):
    if(len(data)>0):
        html = """
        <html><body><p>Bulk analysis for today</p>
        <p>Here is your data:</p>
        {0}
        <p>Regards,</p>
        <p>Puneet</p>
        </body></html>
        """.format(data.to_html())
    else:
        html = """
            <html><body><p>No data downloaded for today</p>
            <p>Regards,</p>
            <p>Puneet</p>
            </body></html>
            """
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            message = MIMEMultipart()
            smtp.login(sender, email_password)
            part1 = MIMEText(html, 'html')
            message.attach(part1)
            message['From'] = sender
            message["To"] = sender
            message["Subject"] = "Bulk analysis for {}".format(date.today().strftime("%Y-%m-%d"))
            smtp.sendmail(sender, receiver, message.as_string())
            smtp.sendmail(sender, receiver2, message.as_string())
    except Exception as e:
        print(e)
def nse_largedeals(mode="bulk_deals"):
    payload = nsefetch('https://www.nseindia.com/api/snapshot-capital-market-largedeal')
    if(mode=="bulk_deals"):
        return pd.DataFrame(payload["BULK_DEALS_DATA"])
    if(mode=="short_deals"):
        return pd.DataFrame(payload["SHORT_DEALS_DATA"])
    if(mode=="block_deals"):
        return pd.DataFrame(payload["BLOCK_DEALS_DATA"])

def analysis_filter():
    #### Find out all the company for which on that day there is only P and not S
    df = nse_largedeals("bulk_deals")
    df.drop_duplicates(inplace=True)
    df['Date'] = [datetime.strptime(x, "%m/%d/%Y").strftime('%Y-%m-%d') if ('/' in x) else x for x in df['date']]
    # print(date.today().strftime("%Y-%m-%d"))
    if(len(df)>0):
        df['Quantity_Traded'] = df['qty'].astype('float')
        countdeals = pd.pivot_table(df, values='Quantity_Traded', index=['symbol'], columns=['buySell'],
                                    aggfunc=np.sum).fillna(0).reset_index()
        countdeals['ratio'] = (countdeals['BUY'] - countdeals['SELL']) / (countdeals['BUY'] + countdeals['SELL'])
        temp = countdeals[countdeals['ratio'].abs() > 0.9]
        temp = pd.merge(temp, df[['symbol', 'clientName', 'watp']], on='symbol')
        temp['Date'] = df.Date.drop_duplicates().iloc[0]
        temp = temp[['Date','symbol', 'BUY', 'SELL', 'ratio', 'clientName', 'watp']]
        temp['Traded_Price'] = df['watp'].astype('float')
        temp['FO'] = temp.apply(lambda x: 1 if x['symbol'] in (listFO['Symbol'].to_list()) else 0, axis =1  )
        email_strat(temp)
    else:
        email_strat(pd.DataFrame(columns = ['Date', 'symbol', 'BUY', 'SELL', 'ratio', 'clientName', 'watp']))
        return False

if not check_holiday(date.today()):
    analysis_filter()
