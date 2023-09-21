import csv
import json
import sys

import pandas as pd
import requests

import os
from dotenv import load_dotenv

load_dotenv()

mainSearchApi = os.getenv('MAIN_SEARCH_API')
detailedSearchApi = os.getenv('DETAILED_SEARCH_API')
nameHistoryApi = os.getenv('NAME_HISTORY_API')
filingHistoryApi = os.getenv('FILING_HISTORY_API')
mergerHistoryApi = os.getenv('MERGER_HISTORY_API')
assumedNameApi = os.getenv('ASSUMED_NAME_API')

apiList = [mainSearchApi, detailedSearchApi, nameHistoryApi, filingHistoryApi, mergerHistoryApi, assumedNameApi]


main_df = pd.DataFrame()


def mainSearch(name):
    payload_data_main = {
        "searchValue": name,
        "searchByTypeIndicator": "EntityName",
        "searchExpressionIndicator": "Contains",
        "entityStatusIndicator": "AllStatuses",
        "entityTypeIndicator":
            ["Corporation",
             "LimitedLiabilityCompany",
             "LimitedPartnership",
             "LimitedLiabilityPartnership"],
        "listPaginationInfo":
            {"listStartRecord": 1,
             "listEndRecord": 50}}


    try:
        response = requests.post(apiList[0], json=payload_data_main)

        if response.status_code == 200:
            data = response.json()
            #print(data['entitySearchResultList'])

            df = pd.DataFrame(data['entitySearchResultList'])
            excel_file = "mainSearch.xlsx"
            df.to_excel(excel_file, index=False)
            print(f"JSON data saved as {excel_file}")

            # print(df['dosID'])
            '''len(df['dosID'])'''

            auxilarySearches(df['dosID'])

        else:
            print(f"Request failed with status code {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")


def auxilarySearches(companyID):

    detailed_df = pd.DataFrame()

    length = len(companyID)
    test = 5
    # length = test
    for j in range(1, len(apiList)):
        temp_df = pd.DataFrame()
        for i in range(length):
            payload_data_other = {
                "SearchID": companyID[i],
                "listPaginationInfo":
                    {"listStartRecord": 1,
                     "listEndRecord": 50}
            }

            try:
                resAux = requests.post(apiList[j], json=payload_data_other)

                if resAux.status_code == 200:
                    dataA = resAux.json()
                    # print(data['entitySearchResultList'])

                    x = pd.json_normalize(dataA)
                    temp_df = pd.concat([temp_df, x], ignore_index=True)
                    # print(temp_df)

                    if i == length - 1:
                        if j == 1:
                            detailed_df = pd.concat([detailed_df, temp_df])
                        elif j == 2:
                            temp_df.drop(temp_df.columns[[0, 1, 2, 3, -1]], axis=1, inplace=True)
                            detailed_df = pd.concat([detailed_df, temp_df], axis=1)
                        elif j == 3:
                            temp_df.drop(temp_df.columns[[0, 1, 2, 3, 4, -1]], axis=1, inplace=True)
                            detailed_df = pd.concat(
                                [detailed_df, temp_df], axis=1)
                        else:
                            temp_df.drop(temp_df.columns[[0, 1, 2, -1]], axis=1, inplace=True)
                            detailed_df = pd.concat(
                                [detailed_df, temp_df], axis=1)


            except requests.exceptions.RequestException as e:
                print(f"Request error: {e}")

        if j == len(apiList) - 1:

            excel_file = "detailedDF.xlsx"
            detailed_df.to_excel(excel_file, index=False)
            print(f"JSON data saved as {excel_file}")

        print(f'Succesfully downloaded data from {apiList[j]}')


if __name__ == "__main__":
    name = "Community Corporation of Buffalo"
    #
    # text = input("prompt")
    # print(sys.argv)

    mainSearch(name)

