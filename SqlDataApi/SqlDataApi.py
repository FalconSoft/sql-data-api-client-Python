import json
import requests
import math
import datetime as datetime
import pandas as pd
from dateutil import parser

class SqlDataApi:

    _api_url = ""
    _auth_token = ""

    def __init__(self, connection_name):
        self._connection_name = connection_name

    @staticmethod
    def set_api_url(url):
        SqlDataApi._api_url = url

    @staticmethod
    def set_authentication(auth_token):
        SqlDataApi._auth_token = auth_token

    def save_array(self, table_name, items, batchsize=15000):
        url = "{}/sql-data-api/{}/save/{}?$accessToken={}".format(
            SqlDataApi._api_url, 
            self._connection_name,
            table_name,
            SqlDataApi._auth_token
        )

        if type(items) is str:
            items = json.loads(items)

        data_tables = self._array_to_tables(items, batchsize)

        commit_status = {
            "inserted" : 0,
            "updated": 0,
            "deleted": 0
        }
        
        for data_table in data_tables:
            payload = json.dumps({
                "tableData": data_table,
                "itemsToDelete": None
            })

            response = requests.request("POST", url,
                data=payload,
                headers={'content-type': "application/json"},
                verify=False
            )
            if response.status_code == 200:
                res = response.json()
                commit_status["inserted"] += res["inserted"]
                commit_status["updated"] += res["updated"]
                commit_status["deleted"] += res["deleted"]
            else:
                err_msg = "Unknown response. StatusCode:{0}, content: {1}".format(response.status_code, response.content) or response.json().get('Message')
                print("Server error status_code: %s, message : %s, ", str(response.status_code), err_msg)
                if response.status_code == 401:
                    raise NameError('Authorization has been denied for this request. Please provide valid token')

                raise NameError(err_msg)

        return commit_status

    def run_query_to_array(self, table_name, **kwargs):
        table = self._run_query(table_name, 
            select = kwargs.get('select', None),
            filter = kwargs.get('filter', None),
            filter_params = kwargs.get('filter_params', None),
            skip = kwargs.get('skip', None),
            order_by = kwargs.get('order_by', None),
            top = kwargs.get('top', None),
        )['table']

        return self._table_to_array(table)

    def execute_sp_to_array(self, stored_proc_name, params):
        url = "{}/sql-data-api/{}/execute?$accessToken={}".format(
            SqlDataApi._api_url, 
            self._connection_name,
            SqlDataApi._auth_token
        )

        payload = json.dumps({
            "commandType": "StoredProcedure",
            "params": params,
            "sql": stored_proc_name
        })

        response = requests.request("POST", url,
            data=payload,
            headers={'content-type': "application/json"},
            verify=False
        )

        if response.status_code == 200:
            return  self._table_to_array(response.json()['table'])

        err_msg = "Unknown response. StatusCode:{0}, content: {1}".format(response.status_code, response.content) or response.json().get('Message')
        print("Server error status_code: %s, message : %s, ", str(response.status_code), err_msg)

        raise NameError(err_msg)

    def _run_query(self, table_name, **kwargs):
        url = "{}/sql-data-api/{}/query/{}?$accessToken={}".format(
            SqlDataApi._api_url, 
            self._connection_name,
            table_name,
            SqlDataApi._auth_token
        )

        payload = json.dumps({
            "Select": kwargs.get('select', None),
            "FilterString": kwargs.get('filter', None),
            "FilterParameters": kwargs.get('filter_params', None),
            "Skip": kwargs.get('skip', None),
            "Top": kwargs.get('top', None),
            "OrderBy": kwargs.get('order_by', None),
            "MainTableAlias": None,
            "TablesJoin": None
        })

        response = requests.request("POST", url,
            data=payload,
            headers={'content-type': "application/json"},
            verify=False
        )

        if response.status_code == 200:
            return response.json()
        
        err_msg = "Unknown response. StatusCode:{0}, content: {1}".format(response.status_code, response.content) or response.json().get('Message')
        print("Server error status_code: %s, message : %s, ", str(response.status_code), err_msg)

        raise NameError(err_msg)
    
    def _table_to_array(self, table):
        result = []

        for row in table['rows']:
            item = {}

            for column_index in range(len(table['fieldNames'])):
                column_name = table['fieldNames'][column_index]
                column_type = table['fieldDataTypes'][column_index]

                if column_type != 'DateTime' or row[column_index] == None:
                    item[column_name] = row[column_index]
                else:
                    item[column_name] =  parser.parse(row[column_index])

            result.append(item)

        return result

    def _array_to_tables(self, array, max_batchsize = 15000):
        column_names = []
        content_size, header_size = [0, 0]
        result_tables = []

        if len(array) == 0:
            return result_tables

        for column_name in array[0].keys():
            column_names.append(column_name)
            header_size += len(column_name)

        content_size = header_size
        table = {
            'fieldNames': column_names,
            'rows': []
        }

        for item in array:
            row = []
            for column_name in column_names:
                value = item.get(column_name, "###NOT#FOUND#")

                if value == "###NOT#FOUND#":
                    print("Can't find column '{0}' in a row. It means first items keys are different than others.\n\r - header  - {1} \n\r - current - {2} \n\r item - {3}"
                    .format(column_name, column_names, item.keys(), item))
                    raise NameError("Can't find column '{0}' in a row".format(column_name))

                if type(value) is pd.pandas.Timestamp:
                    row.append(value.strftime("%Y-%m-%d %H:%M:%S"))
                elif type(value) is datetime.datetime:
                    row.append(value.strftime("%Y-%m-%d %H:%M:%S"))
                elif type(value) is datetime.date:
                    row.append(value.strftime("%Y-%m-%d"))
                elif  str(value) == 'null' or str(value) == 'nan' or str(value) == 'NaT' or pd.isnull(value):
                    row.append(None)
                else:
                    row.append(value)

            table["rows"].append(row)
            # add up content size
            content_size += len(''.join(str(x) for x in row))

            # if content is more than ~2m then we would create another table
            if content_size >= 1750000 or len(table["rows"]) > max_batchsize:
                result_tables.append(table)
                content_size = header_size
                table = {
                    'fieldNames': column_names,
                    'rows': []
                }

        # add last table per 
        result_tables.append(table)

        return result_tables

def main():    
    """test"""
    SqlDataApi.set_api_url("https://localhost:44302")
    SqlDataApi.set_authentication("12121212-token-21121212")

    result = SqlDataApi("SQL-Shared").run_query_to_array("test1.Sample100",
        filter="country = @country",
        filter_params={"country": "UK"}
    )
    print(result)
    status = SqlDataApi("SQL-Shared").save_array("test1.Sample100", result)
    print(status)

    sp_res = SqlDataApi("northwind-db-connection").execute_sp_to_array("northwind.NorthwindEmployeesSummary", {'startDate': "2019-01-01", 'endDate': "2020-05-14"})
    print(sp_res)

if __name__ == "__main__":
    main()