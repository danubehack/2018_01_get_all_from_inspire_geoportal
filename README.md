# Get Geodata from INSPIRE Geoportal
authors: Boris Kruzliak, Tomas Kliment

## Summary
INSPIRE Geoportal application offers options to download spatial datasets provided by EU Member states. Data are organised by INSPIRE spatial data themes and by priority datasets domain, legislation anad country. Goal of the project was to check the actual availability of the downloadable datasets, provide an automatic procedure to download all INSPIRE priority datasets available for a country, dwnload all datasets available from INSPIRE Geoportal Catalogue service and support the visualisation of the data, including the possible combination with the Copernicus data resources.

## Motivation
- The current [INSPIRE Geoportal](http://inspire-geoportal.ec.europa.eu/) application offers options to download spatial datasets provided by EU member states within INSPIRE legislation framework. 
- The data are organized by INSPIRE Spatial Data Themes and INSPIRE Priority Datasets categories.

## Goal
- Goal of the project was to check the actual availability of the downloadable datasets, whether they can or cannot be downloaded by users
- Provide an automatic procedure to download all INSPIRE priority datasets available for a country
- Download all datasets available from INSPIRE Geoportal CSW
- Provide visialisation of the data

## Target user groups
- Public sector
- Research and academy

## Results
- Priority and INSPIRE Data Themes datasets portal scrapper offeing users to launch it with country code and application type arguments.
#### Download data from INSPIRE Geoportal Themes for Slovenia 
```bash
python inspire_download.py -country SI -app themes
```

#### Download data from INSPIRE Geoportal Priority datasets for Slovakia
```bash
python inspire_download.py -country SK -app priority

```
- Video: https://youtu.be/1-1589e1_xQ


