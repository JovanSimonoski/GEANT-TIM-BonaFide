from clients.arxiv_client import ArxivClient

"""
      |
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""


def main():
    """
    ArXiv publications finder script.

    Prompts the user for an author name and uses the ArxivClient
    to search and display academic publications from the ArXiv repository
    with formatted output including titles, years, and co-authors.

    Parameters:
        None

    Returns:
        None
    """
    author_name = input("Enter the author name: ")

    max_results = 50

    try:
        print(f"Searching for publications by '{author_name}'...")
        results = ArxivClient.search_arxiv_publications(author_name, max_results)

        ArxivClient.display_publication_info(results)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
