import requests,json,sys,xmltodict
from xml.etree import ElementTree

def find(key, dictionary):
    for k, v in dictionary.iteritems():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find(key, d):
                    yield result

country = 'SK'
endpoint = 'http://inspire-geoportal.ec.europa.eu/GeoportalProxyWebServices/resources/OGCCSW202/SK?'

serviceUp = requests.head(endpoint+'service=CSW&request=GetCapabilities')

if (serviceUp.status_code) != 200:
    print("Service is not available exiting the process.")
    sys.exit()

### GET HITS FOR SERVICES

def createPostData(start,max,serviceType):
    postData = '''<csw:GetRecords
     xmlns:csw="http://www.opengis.net/cat/csw/2.0.2"
     xmlns:ogc="http://www.opengis.net/ogc" service="CSW" version="2.0.2" resultType="hits" startPosition="{0}" maxRecords="{1}" 
     outputFormat="application/xml" 
     outputSchema="http://www.opengis.net/cat/csw/2.0.2" 
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
     xsi:schemaLocation="http://www.opengis.net/cat/csw/2.0.2 
     http://schemas.opengis.net/csw/2.0.2/CSW-discovery.xsd">
      <csw:Query typeNames="csw:Record">
        <csw:ElementSetName>brief</csw:ElementSetName>
        <csw:Constraint version="1.1.0">
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>ServiceType</ogc:PropertyName>
              <ogc:Literal>{2}</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
        </csw:Constraint>
      </csw:Query>
    </csw:GetRecords>'''.format(start,max,serviceType)
    return postData


serviceCount = requests.post(endpoint,data=createPostData(start=1,max=1,serviceType='download'))

tree = ElementTree.fromstring(serviceCount.content)

xmlToJson = xmltodict.parse(serviceCount.content)
total=list(find(dictionary=xmlToJson,key='@numberOfRecordsMatched'))
if total[0] > 0:
    print("Found {} download services.".format(total[0]))
else:
    print("No download services found")
    sys.exit()

startPosition = 1
while startPosition <= int(total[0]):
    getRecords = requests.post(endpoint,data=createPostData(startPosition,max=1,serviceType='download'))
    print startPosition
    startPosition = startPosition + 1
    continue



### GENERIC TOOLS

