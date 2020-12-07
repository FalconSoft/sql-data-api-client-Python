# sql-data-api-client-Python
SQL Data Api client for Python

### Usage

> pip install SqlDataApi

```py
import SqlDataApi as sql

"""Sql Data Api"""
sql.SqlDataApi.set_api_url("https://localhost:44302")
sql.SqlDataApi.set_authentication("12121212-token-21121212")

# query data
result = sql.SqlDataApi("SQL-Shared").run_query_to_array("test1.Sample100",
    filter="country = @country",
    filter_params={"country": "UK"}
)
print(result)

# save data
status = sql.SqlDataApi("SQL-Shared").save_array("test1.Sample100", result)
print(status)

# execute stored procedure
sp_res = sql.SqlDataApi("northwind-db-connection").execute_sp_to_array("northwind.NorthwindEmployeesSummary", {'startDate': "2019-01-01", 'endDate': "2020-05-14"})
print(sp_res)


"""
result = sql.SqlDataApi("SQL-Shared").run_query_to_array("test1.Sample100",
    filter="country = @country",
    filter_params={"country": "UK"}
)

# load to frame
dataFrame = pd.DataFrame.from_records(result)

# manipulate dataFrame here ...

listOfItems = json.loads(dataFrame.to_json(orient='records'))

# save data
status = sql.SqlDataApi("SQL-Shared").save_array("test1.Sample100", listOfItems)
print(status)
"""


```

### License

A permissive MIT License (c) FalconSoft Ltd.
