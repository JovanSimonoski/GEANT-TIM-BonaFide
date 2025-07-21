from arxiv import Result
from typing import List
from unidecode import unidecode

import arxiv

"""
      |   
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""


class ArxivClient:
    """
    A client for searching academic publications from the ArXiv repository using author-based queries.
    """

    def __init__(self):
        """
        Initialize the ArxivClient.

        Parameters:
            None

        Returns:
            None
        """
        pass

    @staticmethod
    def search_arxiv_publications(author_name: str, max_results: int = 50, transliterate_name: bool = True) -> List[
        Result]:
        """
        Search for publications on ArXiv by author name using the repository's search interface.

        Parameters:
            author_name (str): The full name of the author to search for.
                              Names with special characters will be transliterated if enabled.
            max_results (int): Maximum number of results to return (default: 50).
                              Limited by ArXiv API constraints.
            transliterate_name (bool): Whether to convert special characters to ASCII equivalents
                                     for improved search compatibility (default: True).

        Returns:
            List[Result]: List of arxiv.Result objects containing publication metadata such as:
                         - title: Publication title
                         - authors: List of all authors
                         - published: Publication date
                         - categories: ArXiv subject categories
                         - entry_id: Unique ArXiv identifier and URL
                         Returns empty list if no publications found or search fails.
        """
        if transliterate_name:
            author_name = unidecode(author_name)

        search_query = f"au:\"{author_name}\""

        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        client = arxiv.Client()
        results = list(client.results(search))
        return results

    @staticmethod
    def display_publication_info(results: List[Result]) -> None:
        """
        Display formatted publication information to console output.

        Parameters:
            results (List[Result]): List of arxiv.Result objects from search_arxiv_publications.
                                   Can be empty list for graceful handling.

        Returns:
            None: Prints formatted publication details including title, year,
                 field categories, authors, and ArXiv URL to standard output.
                 Displays "No publications found" message if results list is empty.
        """
        if not results:
            print("No publications found for this author.")
            return

        print(f"Found {len(results)} publications:")
        print("-" * 80)

        for i, result in enumerate(results, 1):
            pub_year = result.published.year
            categories = ", ".join(result.categories)
            authors = ", ".join(author.name for author in result.authors)

            print(f"Publication #{i}:")
            print(f"Title: {result.title}")
            print(f"Year: {pub_year}")
            print(f"Field: {categories}")
            print(f"Authors: {authors}")
            print(f"URL: {result.entry_id}")
            print("-" * 80)

    @staticmethod
    def get_coauthors(result):
        """
        Extract all author names from a publication result for collaboration network analysis.

        Parameters:
            result (arxiv.Result): A single publication result object from ArXiv search.
                                  Must contain valid authors list attribute.

        Returns:
            list: List of author name strings including the primary author and all collaborators.
                 Names are returned as provided in the ArXiv metadata without modification.
                 Returns empty list if no authors found in the result.
        """
        return [author.name for author in result.authors]
