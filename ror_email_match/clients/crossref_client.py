import requests

"""
      |   
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""


class CrossrefClient:
    """
    A client for fetching organization metadata from the Crossref API using FundRef identifiers.
    """

    def __init__(self):
        """
        Initialize the CrossrefClient.

        Parameters:
            None

        Returns:
            None
        """
        pass

    def fetch_crossref_data(self, crossref_id):
        """
        Fetch organization data from the Crossref API using a Crossref ID.

        Parameters:
            crossref_id (str): The Crossref identifier for the organization.
                              Use 'N/A' if no ID is available.

        Returns:
            dict or None: Organization metadata dictionary containing fields like:
                         - name: Organization's primary name
                         - location: Geographic location
                         - work-count: Number of associated works
                         - alt-names: List of alternative names
                         Returns None if crossref_id is 'N/A', request fails,
                         or network error occurs.
        """
        if crossref_id == 'N/A':
            return None

        try:
            crossref_url = f"https://api.crossref.org/funders/{crossref_id}"
            response = requests.get(crossref_url)

            if response.status_code == 200:
                return response.json().get('message', {})
            else:
                print(f"Error fetching Crossref data: Status code {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"Error connecting to Crossref API: {e}")
            return None
