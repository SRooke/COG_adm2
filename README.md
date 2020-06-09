# COG_adm2

Generation of adm2 from [GADM](https://gadm.org/) for COG-UK samples. 

## Dependencies

Create a conda environment from environment.yml file. 

```bash
conda env create -f environment.yml
```
Additionally a [forked version of sjoin.py](https://github.com/adriangb/geopandas/tree/sjoin-nearest) is used for spatial point 'rounding' to avoid potential edge-cases with coastal postcodes.

## Usage

The script can be run on an existing .csv file containing sample metadata. This file can be formatted in the standard COG-UK metadata format - in which case default headings for --sampleID and --outerPC can be used (central_sample_id and adm2_private, respectively). 


```bash
COG_adm2.py metadataInput.csv --output output.csv
```


Alternatively the column headings used in a non-standardised .csv containing sample metadata can be specified as below.

```bash
COG_adm2.py metadataInput.csv\
--sampleID 'sampleID' --outerPC 'outerPostcode' --output ./output.csv 
```

