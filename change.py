import time
import hashlib
import re, yaml, os
import argparse
from urllib.request import urlopen, Request
from notifiers.notify import Notifier
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name")
parser.add_argument("-url", "--url", required=True)
args = parser.parse_args()

directory = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
config = yaml.load(open(os.path.join(directory, 'config.yml'), 'r').read(),Loader=yaml.Loader)
notifier = Notifier()
notifier.notifiers = config['notifiers']

name = args.name
url = Request(args.url, headers={'User-Agent': 'Mozilla/5.0'})
cresponse = urlopen(url).read()
cresponse=re.sub('''<a href="/cdn-cgi/l/email-protection#[0-9a-z]*">''', "<a>", str(cresponse))
currentHash = hashlib.sha224(cresponse.encode('utf-8')).hexdigest()
print("Started the process at: ",datetime.now())

# current_file = open("current.txt", "w")
# new_file = open("new.txt", "w")
c=0
while True:
    try:
        print("Check-", c, " triggered : ",datetime.now())
        nresponse = urlopen(url).read()
        nresponse=re.sub('''<a href="/cdn-cgi/l/email-protection#[0-9a-z]*">''', "<a>", str(nresponse))
        # newHash = hashlib.sha224(nresponse.encode('utf-8')).hexdigest()
        if nresponse == cresponse:
            print("No Change: ",datetime.now())
            continue
        else:
            # current_file.write(cresponse)
            # new_file.write(nresponse)
            print("Something Changed at: ",datetime.now())
            cresponse = urlopen(url).read()
            cresponse=re.sub('''<a href="/cdn-cgi/l/email-protection#[0-9a-z]*">''', "<a>", str(cresponse))
            # currentHash = hashlib.sha224(cresponse.encode('utf-8')).hexdigest()
            notifier.messages = [
            {
                "slack":{
                    "status": "#008000",
                    "long_message":"Change in wesbite: "+ name,
                    "short_message": "Site Change",
                    "domain": args.url
                }
            }]
            notifier.notify()
            print("Alert Sent at: ", datetime.now())
        c=c+1
        time.sleep(3600)

    except Exception as e:
        print("Error at ",datetime.now(), e)
        notifier.messages = [
        {
            "slack":{
                "status": "#D00000",
                "long_message":"ERROR in code for: "+ name,
                "short_message": "Exception",
                "domain": args.url
            }
        }]
        notifier.notify()
        time.sleep(300)
# current_file.close()
# new_file.close()
