#!/usr/bin/env python
# coding: utf-8
import geopandas as gp
import pandas as pd
import postcodes_io_api
import argparse
import adriangb_sjoin
import numpy as np


def spatialPointPuller(outerPC):
    PCapi = postcodes_io_api.Api(debug_http=False)
    desiredColumns = ['outcode', 'latitude', 'longitude']
    dataforOutput = []
    for i in range(len(outerPC.index)):
        df = outerPC.iloc[[i]]
        retrievedData = PCapi.get_outcode(df[args.outerPC][i])
        try:
            dataDict = retrievedData['result']
            dataList = [dataDict[x] for x in desiredColumns]
            dataList.insert(0, df[args.sampleID][i])
            dataforOutput.append(dataList)
        except:
            if df[args.outerPC].notnull()[i] is True:
                print("Check postcode for:\n" + str(df[[args.sampleID, args.outerPC]]))
            dataList = [df[args.sampleID][i], df[args.outerPC][i], np.nan, np.nan]
            dataforOutput.append(dataList)
    outFrame = pd.DataFrame(dataforOutput, columns=[args.sampleID, 'outcode', 'latitude', 'longitude'])
    return outFrame


def GADMtranslate(coordsFrame):
    ukADM2 = gp.read_file('./gadm36_GBR.gpkg', layer='gadm36_GBR_2')
    validPoints = coordsFrame[~coordsFrame['latitude'].isna()]
    invalidPoints = coordsFrame[~coordsFrame['latitude'].notna()]
    coordinateDF = gp.GeoDataFrame(validPoints, geometry=gp.points_from_xy(validPoints.longitude, validPoints.latitude))
    coordinateDF.crs = 'epsg:4326'
    pointsinPoly = adriangb_sjoin.sjoin_nearest(coordinateDF, ukADM2)
    pointsinPoly.rename(columns={'NAME_2': 'adm2', 'outcode': args.outerPC}, inplace=True)
    outDF = pd.DataFrame(pointsinPoly)
    outDF = pd.concat([outDF, invalidPoints], axis=0, ignore_index=True)
    return (outDF[[args.sampleID, args.outerPC, 'latitude', 'longitude', 'adm2']])


def adm2generation(metadata):
    locationFrame = spatialPointPuller(metadata)
    adm2 = GADMtranslate(locationFrame)
    metadata = pd.merge_ordered(metadata, adm2, how='left', on=args.sampleID)
    return metadata



parser = argparse.ArgumentParser(description='adm2 generation from outer-level postcodes')
parser.add_argument('metadata', metavar='metadata.csv', type=str,
                    help='CSV file containing the sample metadata for which adm2 information will be generated.')

parser.add_argument('--sampleID', default='central_sample_id', type=str, metavar='central_sample_id',
                    help='Column name for the unique sample IDs as defined in .csv file.')

parser.add_argument('--outerPC', default='adm2_private', type=str, metavar='adm2_private',
                    help='Column name for the outer-level postcodes as defined in .csv file.')

parser.add_argument('--output', type=str,
                    help='Filename for desired output file.')
args = parser.parse_args()


#print(args)

metaframe = pd.read_csv(args.metadata)
outFrame=adm2generation(metaframe)
outFrame.to_csv(args.output, index=False)
