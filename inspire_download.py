# -*- coding: utf-8 -*-
import os, sys, json, requests, re, zipfile,argparse
ap = argparse.ArgumentParser()
ap.add_argument("-country",required=False,dest="country",help="Define country code for which you wish download the data. Default SK")
ap.add_argument("-app",required=False,dest="app",help="Define INSPIRE Geoportal application profile, either priority or thematic, default is priority")
args = vars(ap.parse_args())
if args['country']:
    COUNTRY = args['country']
else:
    COUNTRY = 'sk'
if args['app']:
    APP = args['app']
else:
    APP = 'priority'
#bash = open(os.path.join(sys.argv[1],'ogr2ogr_bash.sh','a'))
bash = open(COUNTRY+'_ogr2ogr_bash.sh','a')
countryHomeDir = os.path.join(COUNTRY,APP)
if not os.path.exists(os.path.join(COUNTRY,APP)):
    os.makedirs(os.path.join(COUNTRY,APP))
level2=[]
levels4=[]
file = open('pokus.txt','a') 
session = requests.session()
baseUrl = 'http://inspire-geoportal.ec.europa.eu/solr/select?wt=json&' \
          'q=(*%3A*%5E1.0%20OR%20(interoperabilityAspect%3A(DOWNLOAD_MATCHING_DATA_IS_AVAILABLE%20AND%20DATA_DOWNLOAD_LINK_IS_AVAILABLE)%5E3.0%20OR%20interoperabilityAspect%3A(LAYER_MATCHING_DATA_IS_AVAILABLE)%5E2.0%20OR%20interoperabilityAspect%3A(*)%5E1.0))&' \
          'fq=sourceMetadataResourceLocator%3A*&' \
          'fq=resourceType%3A(dataset%20OR%20series)&' \
          'fl=id%2CresourceTitle%2CmemberStateCountryCode%2CinspireTheme%2CisDw%3Aquery(%24isDwQ)%2CisVw%3Aquery(%24isVwQ)&' \
          'isDwQ=interoperabilityAspect%3A(DOWNLOAD_MATCHING_DATA_IS_AVAILABLE%20AND%20DATA_DOWNLOAD_LINK_IS_AVAILABLE)&' \
          'isVwQ=interoperabilityAspect%3A(LAYER_MATCHING_DATA_IS_AVAILABLE)&' \
          'sort=score%20desc%2CresourceTitle%20asc&' \
          'start=0&' \
          'rows=1000&' \
          'callback=?&' \
          'json.wrf=processData_dtResults&' \
          'fq=memberStateCountryCode%3A%22'+COUNTRY+'%22&' \
          'fq=priorityDataset%3A*&' \
           '_=1539423924101'

if APP == 'priority':
    url = baseUrl
else:
    url = baseUrl.replace("fq=priorityDataset%3A*&","")
ans = session.get(url)
resultDict = json.loads(ans.text.replace('processData_dtResults(','').replace(')',''))
print("The number of results is: {}".format(resultDict['response']['numFound']))
if int(resultDict['response']['numFound']) == 0:
    print("No results found exiting the process.")
    sys.exit()
for doc in resultDict['response']['docs']:
    if 'isDw' in doc and 'id' in doc:
        print("Found downloadable source with id {}. Adding to further processing.".format(doc['id']))
        level2.append('http://inspire-geoportal.ec.europa.eu/resources' + doc['id'] + '/?callback=parseResponse')
    else:
        print("Resource with id {} has not link to download.".format(doc['id']))
        pass
if len(level2) == 0:
    print("No downloadable data found exiting the process.")
    sys.exit()

print("Found {} downloadable links. Starting downloads ... ".format(len(level2)))
for level in level2:
    print("Openning level2 session for {}".format(level))
    ans2 = session.get(level)
    params=re.split('/', level.replace('http://inspire-geoportal.ec.europa.eu/resources/','').replace('?callback=parseResponse',''))
    link4=''
    link3=''    
    params4=params[:-4]
    params3=params[:-3]
    for param4 in params4:
        link4=link4+'/'+param4
    for param3 in params3:
        link3=link3+'/'+param3
    resultDict = json.loads(ans2.text.replace('parseResponse(','').replace(');',''))
    if 'SpatialDataSetResource' in resultDict:
        if isinstance(resultDict['SpatialDataSetResource']['DownloadServiceDataSetMetadataLocator'],dict):
            level3=resultDict['SpatialDataSetResource']['DownloadServiceDataSetMetadataLocator']['URL']
            if str(level3).find('../../../')>-1:
                levels4.append('http://inspire-geoportal.ec.europa.eu/resources'+link4+'/'+level3.replace('../../../','')+'/?callback=parseResponse')
            else:
                levels4.append('http://inspire-geoportal.ec.europa.eu/resources'+link3+'/'+level3.replace('../../','')+'/?callback=parseResponse')
        elif isinstance(resultDict['SpatialDataSetResource']['DownloadServiceDataSetMetadataLocator'],list):
            for mdURL in resultDict['SpatialDataSetResource']['DownloadServiceDataSetMetadataLocator']:
                level3=mdURL['URL']
                if str(level3).find('../../../')>-1:
                    levels4.append('http://inspire-geoportal.ec.europa.eu/resources'+link4+'/'+level3.replace('../../../','')+'/?callback=parseResponse')
                else:
                    levels4.append('http://inspire-geoportal.ec.europa.eu/resources'+link3+'/'+level3.replace('../../','')+'/?callback=parseResponse')
zip_soubors=[]
for level4 in levels4:
    print("Openning level4 session for {}".format(level))
    try:
        ans4 = session.get(level4)
    except requests.exceptions.ConnectionError as e:
        print("Error: {}".format(e.message))
        continue
    resultDict = json.loads(ans4.text.replace('parseResponse(', '').replace(');', ''))
    if 'SpatialDataSetDownloadLink' in resultDict['DownloadServiceSpatialDataSetResource']:
        if isinstance(resultDict['DownloadServiceSpatialDataSetResource']['UniqueResourceIdentifier'],list):
            resourceId = resultDict['DownloadServiceSpatialDataSetResource']['UniqueResourceIdentifier'][0]
        elif isinstance(resultDict['DownloadServiceSpatialDataSetResource']['UniqueResourceIdentifier'],dict):
            resourceId = resultDict['DownloadServiceSpatialDataSetResource']['UniqueResourceIdentifier']
        filename = ''.join(e for e in resourceId['Namespace'] if e.isalnum()) + '_' + ''.join(e for e in resourceId['Code'] if e.isalnum())
        if isinstance(resultDict['DownloadServiceSpatialDataSetResource']['SpatialDataSetDownloadLink'],dict):
            try:
                url=resultDict['DownloadServiceSpatialDataSetResource']['SpatialDataSetDownloadLink']['SpatialDataSetDownloadResourceLocator']['DownloadResourceLocator']['URL']
                print("Download URL is: {}".format(url))
                #try:
                print("Downlaoding dataset from URL: {}".format(url))
                ans5 = session.get(url)
                print "RESPONSE HEADERS ARE: ", ans5.headers
                if 'zip' in ans5.headers['Content-Type']:
                    soubor = filename + '.zip'
                if 'xml' in ans5.headers['Content-Type']:
                    soubor = filename + '.xml'
                if 'gml' in ans5.headers['Content-Type']:
                    soubor = filename + '.gml'
                print("Ukladam do suboru: {}".format(soubor))
                dwPath = os.path.join(countryHomeDir, soubor)
                fd = open(dwPath, 'wb')
                fd.write(ans5.content)
                fd.close()
                if soubor.rsplit('.', 1)[-1] == 'zip':
                    try:
                        zip_ref = zipfile.ZipFile(dwPath, 'r')
                        zip_ref.extractall(os.path.splitext(dwPath)[0])
                        zip_ref.close()
                        zip_soubors.append(os.path.splitext(dwPath)[0])
                    except zipfile.BadZipFile:
                        print('ZIP nefunguje: {}'.format(dwPath))
                elif soubor.rsplit('.', 1)[-1] == 'gml':
                    bash.write(
                        'ogr2ogr -f "PostgreSQL" PG:"host=localhost port=5432 dbname=hackathon schemas=inspire user=postgres password=postgres" ' + os.path.join(countryHomeDir, soubor) + ' -progress -oo GML_ATTRIBUTES_TO_OGR_FIELDS=YES -nln ' + soubor.replace(
                            '.', '_').replace('-', '_') + ' \n')
                else:
                    pass

            except:
                print('URL nefunguje: '+url)
        elif isinstance(resultDict['DownloadServiceSpatialDataSetResource']['SpatialDataSetDownloadLink'],list):
            for item in resultDict['DownloadServiceSpatialDataSetResource']['SpatialDataSetDownloadLink']:
                url = item['SpatialDataSetDownloadResourceLocator']['DownloadResourceLocator']['URL']
                print("Download URL is: {}".format(url))
                try:
                    ans5=session.get(url)
                    print "RESPONSE HEADERS ARE: ", ans5.headers
                    if 'zip' in ans5.headers['Content-Type']:
                        soubor = filename + '.zip'
                    if 'xml' in ans5.headers['Content-Type']:
                        soubor = filename + '.xml'
                    if 'gml' in ans5.headers['Content-Type']:
                        soubor = filename + '.gml'
                    #fd = open(slozka+'/'+soubor, 'wb')
                    print("Ukladam do suboru: {}".format(soubor))
                    dwPath = os.path.join(countryHomeDir, soubor)
                    fd = open(dwPath, 'wb')
                    fd.write(ans5.content)
                    fd.close()
                    if soubor.rsplit('.', 1)[-1]=='zip':
                        try:
                            zip_ref = zipfile.ZipFile(dwPath, 'r')
                            zip_ref.extractall(os.path.splitext(dwPath)[0])
                            zip_ref.close()
                            zip_soubors.append(os.path.splitext(dwPath)[0])
                        except zipfile.BadZipFile:
                            print('ZIP nefunguje: {}'.format(dwPath))
                    elif soubor.rsplit('.', 1)[-1]=='gml':
                        bash.write('ogr2ogr -f "PostgreSQL" PG:"host=localhost port=5432 dbname=hackathon schemas=inspire user=postgres password=postgres" '+ os.path.join(countryHomeDir, soubor)+' -progress -oo GML_ATTRIBUTES_TO_OGR_FIELDS=YES -nln '+soubor.replace('.','_').replace('-','_')+' \n')
                    else:    
                        pass
                except:
                    print('URL nefunguje: '+url)
    else:
        pass
for zip_soubor in zip_soubors :
    for root, dirs, files in os.walk(zip_soubor):
        for file in files:
            if file.endswith(".shp"):
                print(os.path.join(root, file))
                bash.write('ogr2ogr -f "PostgreSQL" PG:"host=localhost port=5432 dbname=hackathon schemas=inspire user=postgres password=postgres" -nlt PROMOTE_TO_MULTI -unsetFieldWidth '+os.path.join(root, file)+'\n')