import os
from google.cloud import bigquery

# Define credentials 
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'bigquery-credentials.json'
client = bigquery.Client()

def _fetch_data_bigquery(query):
    """
      Take SQL query in Standard SQL and returns a Pandas DataFrame of results
      ref: https://cloud.google.com/bigquery/docs/reference/standard-sql/enabling-standard-sql
    """
    return client.query(query, location="US").to_dataframe()


class DataQuery:
    """
    Data fetcher
    """
    def __init__(self, name, query, state, year):
        """
        name: a given name for the query
        query: string standard SQL query
        state: name of the US state
        year: year
        """
        self.name = name
        self.state = state
        self.year = year
        self.query = query % {'state': self.state, 'year': self.year} 


    def get_data(self):
        # Repalce state and year in the query
        print('running', self.state, self.year)
        # Get data from BigQuery
        return _fetch_data_bigquery(self.query)