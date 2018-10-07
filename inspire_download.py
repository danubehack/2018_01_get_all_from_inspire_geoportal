import sys
import json
import requests
import re
level2=[]
levels4=[]
file = open('pokus.txt','a') 
session = requests.session()
url = 'http://inspire-geoportal.ec.europa.eu/solr/select?wt=json&q=(*%3A*%5E1.0%20OR%20(interoperabilityAspect%3A(DOWNLOAD_MATCHING_DATA_IS_AVAILABLE%20AND%20DATA_DOWNLOAD_LINK_IS_AVAILABLE)%5E3.0%20OR%20interoperabilityAspect%3A(LAYER_MATCHING_DATA_IS_AVAILABLE)%5E2.0%20OR%20interoperabilityAspect%3A(*)%5E1.0))&fq=sourceMetadataResourceLocator%3A*&fq=resourceType%3A(dataset%20OR%20series)&fl=id%2CresourceTitle%2CmemberStateCountryCode%2CinspireTheme%2CisDw%3Aquery(%24isDwQ)%2CisVw%3Aquery(%24isVwQ)&isDwQ=interoperabilityAspect%3A(DOWNLOAD_MATCHING_DATA_IS_AVAILABLE%20AND%20DATA_DOWNLOAD_LINK_IS_AVAILABLE)&isVwQ=interoperabilityAspect%3A(LAYER_MATCHING_DATA_IS_AVAILABLE)&sort=score%20desc%2CresourceTitle%20asc&start=0&rows=100&callback=?&json.wrf=processData_dtResults&fq=memberStateCountryCode%3A%22'+sys.argv[1]+'%22&fq=priorityDataset%3A*&_=1538831009749'
ans = session.get(url)
#print(ans.text)
j = json.loads(ans.text.replace('processData_dtResults(','').replace(')',''))
i = json.loads(str(j['response']).replace('\'','\"'))
for doc in i['docs']:
    f = json.loads(str(doc).replace('\'','\"'))
    #print(f['id'])
    if str(f).find('isDw')>-1:
        level2.append('http://inspire-geoportal.ec.europa.eu/resources'+f['id']+'/?callback=parseResponse')
    else:
        pass
   
for level in level2:
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
   
        

    j = json.loads(ans2.text.replace('parseResponse(','').replace(');',''))

    if str(j['SpatialDataSetResource']['DownloadServiceDataSetMetadataLocator'])[0] !='[':
        level3=j['SpatialDataSetResource']['DownloadServiceDataSetMetadataLocator']['URL']

        if str(level3).find('../../../')>-1:
            levels4.append('http://inspire-geoportal.ec.europa.eu/resources'+link4+'/'+level3.replace('../../../','')+'/?callback=parseResponse')
        else:
            levels4.append('http://inspire-geoportal.ec.europa.eu/resources'+link3+'/'+level3.replace('../../','')+'/?callback=parseResponse')        
    else:
        pocet_soub=0

        for mess in j['SpatialDataSetResource']['DownloadServiceDataSetMetadataLocator']:
            level3=j['SpatialDataSetResource']['DownloadServiceDataSetMetadataLocator'][pocet_soub]['URL']
            pocet_soub=pocet_soub+1
            if str(level3).find('../../../')>-1:
                levels4.append('http://inspire-geoportal.ec.europa.eu/resources'+link4+'/'+level3.replace('../../../','')+'/?callback=parseResponse')
            else:
                levels4.append('http://inspire-geoportal.ec.europa.eu/resources'+link3+'/'+level3.replace('../../','')+'/?callback=parseResponse')

for level4 in levels4:
    ans4 = session.get(level4)
    if ans4.text.find('SpatialDataSetDownloadLink')>-1:
        j = json.loads(ans4.text.replace('parseResponse(','').replace(');',''))
        if str(j['DownloadServiceSpatialDataSetResource']['SpatialDataSetDownloadLink'])[0] !='[':
   
            url=j['DownloadServiceSpatialDataSetResource']['SpatialDataSetDownloadLink']['SpatialDataSetDownloadResourceLocator']['DownloadResourceLocator']['URL']
            
            ans5=session.get(url)
            fd = open('nl/'+url.rsplit('/', 1)[-1], 'wb')
            fd.write(ans5.content)
            fd.close()
        else:
            ii=0
            hh=[]
            for level5 in j['DownloadServiceSpatialDataSetResource']['SpatialDataSetDownloadLink']:
                hh.append(ii)            
                ii=ii+1
            
                       
            for i in hh:
                
                url=j['DownloadServiceSpatialDataSetResource']['SpatialDataSetDownloadLink'][i]['SpatialDataSetDownloadResourceLocator']['DownloadResourceLocator']['URL']
                
                ans5=session.get(url)
                fd = open('nl/'+url.rsplit('/', 1)[-1], 'wb')
                fd.write(ans5.content)
                fd.close()                    
    else:
        pass

