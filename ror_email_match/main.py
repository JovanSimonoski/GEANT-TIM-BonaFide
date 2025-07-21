from core.organization_finder import OrganizationFinder

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
        Main entry point for the organization finder application.

        Prompts the user for an email address and uses the OrganizationFinder
        to identify and display potential organizational matches based on
        DNS analysis, ROR data, and Crossref metadata.

        Parameters:
            None

        Returns:
            None
    """
    finder = OrganizationFinder()
    email = input("Enter the email address: ")
    finder.find_org_associated_with_email(email)


if __name__ == "__main__":
    main()
