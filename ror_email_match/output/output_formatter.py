"""
      |
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""


class OutputFormatter:
    """
    Handles formatting and display of organization finder results.

    This class provides methods to present DNS analysis comparisons, organization matches,
    and scoring breakdowns in a structured, readable format for console output.
    """

    def __init__(self):
        """
        Initialize the OutputFormatter.

        Parameters:
            None

        Returns:
            None
        """
        pass

    def print_dns_comparison(self, similarities, email_domain, website_domain):
        """Print DNS comparison results in a formatted way"""
        if not similarities:
            print(f"\n   DNS Comparison")
            print(f"   No comparison available (same domain: {email_domain})")
            return

        print(f"\n   DNS Comparison: {email_domain} and {website_domain}")
        print("   " + "-" * 60)

        score = similarities["relation_score"]
        print(f"\n       Domain Relationship Score: {score}/100")

        if similarities["matching_nameservers"]:
            print(f"\n       Matching Name Servers:")
            for ns in similarities["matching_nameservers"]:
                print(f"       - {ns}")

        if similarities["matching_a_records"]:
            print(f"\n       Matching A Records (IPs):")
            for ip in similarities["matching_a_records"]:
                print(f"       - {ip}")

        if similarities["matching_mx_records"]:
            print(f"\n       Matching MX Records:")
            for mx in similarities["matching_mx_records"]:
                print(f"       - {mx}")

        if similarities['soa_email_relation']:
            print(f"\n       Related SOA emails found")
            print(f"              Email SOA: {similarities["email_soa"]}")
            print(f"              Website SOA: {similarities["website_soa"]}")

        if similarities['spf_similarity']:
            print(f"\n       Related SPF configurations found")
            print(f"              Email SPF: {similarities["email_spf"]}")
            print(f"              Website SPF: {similarities["website_spf"]}")

    def print_individual_dns_analysis(self, dns_results, email_domain, dns_analyzer):
        """
        Print DNS analysis results for individual organization matches.

        Displays DNS comparison between email domain and organization website domain,
        or indicates when domains are identical.

        Parameters:
            dns_results (dict): DNS analysis results containing email_domain and
                               optionally website_domain data.
            email_domain (str): The email domain being analyzed.
            dns_analyzer (DNSAnalyzer): DNSAnalyzer instance for comparison operations.

        Returns:
            None
        """
        if "website_domain" in dns_results:
            website_domain = dns_results["website_domain"]["domain"]

            similarities = dns_analyzer.compare_dns_results(dns_results)
            self.print_dns_comparison(similarities, email_domain, website_domain)
        else:
            self.print_dns_comparison(None, email_domain, email_domain)

    def print_dns_analysis(self, results, dns_analyzer):
        """
        Print general DNS analysis results.

        Parameters:
            results (dict): DNS analysis results from DNSAnalyzer.
            dns_analyzer (DNSAnalyzer): DNSAnalyzer instance for comparison operations.

        Returns:
            None
        """
        if "website_domain" in results:
            similarities = dns_analyzer.compare_dns_results(results)
            self.print_dns_comparison(similarities)

    def print_organization_results(self, scored_results, result_display_limit, email_domain, dns_analyzer,
                                   crossref_client):
        """Print formatted organization results"""
        print("\nOrganization Matches:")
        print("=" * 80)

        for i, (result, score_breakdown, dns_results_for_result) in enumerate(scored_results, start=1):
            if i > result_display_limit:
                break

            crossref_id = result.get('external_ids', {}).get('FundRef', {}).get('all', ['N/A'])[0]
            crossref_data = crossref_client.fetch_crossref_data(crossref_id) if crossref_id != 'N/A' else None

            print(f"\n{i}. {result.get('name')}")
            print(f"   Match Score: {score_breakdown['total']}%")
            print(f"   Website(s): {', '.join(result.get('links', []))}")

            print("\n   Score Breakdown:")
            print(
                f"      Fully Qualified Domain Match        : {score_breakdown['fully_qualified_domain_name_match']:>3}/100 points")
            print(f"      Base Domain Match                   : {score_breakdown['domain_match']:>3}/80  points")

            if score_breakdown["domain_match"] > 0:
                print(
                    f"         Email is Subdomain of Website    : {score_breakdown['email_is_subdomain_of_website_domain']:>3}/10  points")
                print(
                    f"         Website is Subdomain of Email    : {score_breakdown['website_is_subdomain_of_email_domain']:>3}/-10 points")
                print(
                    f"         Subdomain Mismatch Penalty       : {score_breakdown['subdomain_mismatch']:>3}/-10 points")
            else:
                print(
                    f"      Email in Website Subdomain          : {score_breakdown['domain_of_email_in_website_subdomain']:>3}/20  points")
                print(
                    f"      Website in Email Subdomain          : {score_breakdown['domain_of_website_in_email_subdomain']:>3}/20  points")

            print(
                f"      DNS Similarity Bonus                : {score_breakdown['dns_similarity_bonus']:>3}/15  points")
            print(f"      Crossref Bonus                      : {score_breakdown['crossref_bonus']:>3}/5   points")

            print(f"\n   Crossref ID: {crossref_id}")

            if crossref_data:
                print("   Crossref Data:")
                print(f"      Name        : {crossref_data.get('name', 'N/A')}")
                print(f"      Location    : {crossref_data.get('location', 'N/A')}")
                print(f"      Works Count : {crossref_data.get('work-count', 'unknown')}")

                alt_names = crossref_data.get('alt-names', [])
                if alt_names:
                    preview = ', '.join(alt_names[:3])
                    suffix = ", ..." if len(alt_names) > 3 else ""
                    print(f"      Also known as: {preview}{suffix}")

            self.print_individual_dns_analysis(dns_results_for_result, email_domain, dns_analyzer)

            print("\n" + "-" * 80)
