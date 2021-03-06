import requests
import sys
from imp import reload
reload(sys)

##if the version of your python is less than 3.0, please add this line of code:
##sys.setdefaultencoding('utf-8')

##get the path of the file
FileName = sys.argv[0].split('.')[0]
FullFileName = FileName + '.csv'

##load from JIRA
print('loading, please wait...')
url = "https://issues.apache.org/jira/sr/jira.issueviews:searchrequest-csv-all-fields/temp/SearchRequest.csv?jqlQuery=project+%3D+Camel+AND+resolution+%3D+Unresolved+ORDER+BY+priority+DESC%2C+updated+DESC"
r = requests.get(url)
with open(FullFileName, 'w', encoding='utf-8') as f:
    f.write(r.text)
