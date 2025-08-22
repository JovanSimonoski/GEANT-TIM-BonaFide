import tldextract
from ror_email_match.clients.dns_client import DNSAnalyzer

"""
      |   
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""


class MatchScorer:
    """
    Calculates match scores between email domains and organization results from ROR.

    This class evaluates how well an email domain matches with potential organization
    results by analyzing domain relationships, DNS records, WHOIS data, and external identifiers
    to produce a comprehensive scoring system.
    """

    def __init__(self):
        """
        Initialize the MatchScorer with a DNSAnalyzer instance.

        Parameters:
            None

        Returns:
            None
        """
        self.dns_analyzer = DNSAnalyzer()

    def calculate_match_score(self, email, result, dns_results=None, whois_results=None):
        """
        Calculate a comprehensive match score between an email and an organization result.

        Analyzes domain relationships, DNS similarities, WHOIS data, and external identifiers to
        determine how likely it is that the email belongs to the organization.

        Parameters:
            email (str): The email address to match against.
            result (dict): Organization result from ROR API containing name, links,
                          and external_ids.
            dns_results (dict, optional): DNS analysis results from DNSAnalyzer.run_dns_analysis().
                                        If provided, enables DNS verification bonuses.
            whois_results (dict, optional): WHOIS comparison results containing match_score and matches.
                                          If provided, enables WHOIS verification bonuses.

        Returns:
            dict: Score breakdown containing:
                 - fully_qualified_domain_name_match: 0-100 points for exact FQDN match
                 - domain_match: 0-80 points for base domain match
                 - website_is_subdomain_of_email_domain: 0 to -10 points
                 - email_is_subdomain_of_website_domain: 0-10 points
                 - subdomain_mismatch: 0 to -10 points for conflicting subdomains
                 - domain_of_email_in_website_subdomain: 0-20 points
                 - domain_of_website_in_email_subdomain: 0-20 points
                 - crossref_bonus: 0-5 points for having Crossref data
                 - dns_verification_bonus: 0-10 points for DNS record matches
                 - dns_similarity_bonus: 0-15 points based on overall DNS similarity
                 - whois_bonus: 0-20 points based on WHOIS data matches
                 - total: Sum of all score components
        """
        score_breakdown = {
            "fully_qualified_domain_name_match": 0,
            "domain_match": 0,
            "website_is_subdomain_of_email_domain": 0,
            "email_is_subdomain_of_website_domain": 0,
            "subdomain_mismatch": 0,
            "domain_of_email_in_website_subdomain": 0,
            "domain_of_website_in_email_subdomain": 0,
            "crossref_bonus": 0,
            "dns_verification_bonus": 0,
            "dns_similarity_bonus": 0,
            "whois_bonus": 0,
            "total": 0
        }

        email_full_domain = email.split('@')[-1]
        email_parts = tldextract.extract(email_full_domain)

        # Add WHOIS verification bonus if applicable
        if whois_results:
            whois_match_score = whois_results.get("match_score", 0)
            # Map WHOIS match score (0-100) to bonus points (0-20)
            score_breakdown["whois_bonus"] = min(20, whois_match_score // 5)

        # Add DNS verification bonus if applicable
        if dns_results:
            email_a_records = set(dns_results["email_domain"]["a_records"])

            for link in result.get('links', []):
                link_domain = self.dns_analyzer.get_domain_from_url(link)

                # Temporary DNS lookup for the website
                try:
                    website_a_records = set(self.dns_analyzer.get_a_records(link_domain))

                    # If there's any overlap in A records, it's a good sign they belong to the same organization
                    if email_a_records.intersection(website_a_records) and email_a_records and website_a_records:
                        score_breakdown["dns_verification_bonus"] = 10
                        break
                except:
                    pass

                # Check SOA email patterns
                soa_email = dns_results["email_domain"]["soa_email"]
                if soa_email:
                    soa_domain = self.dns_analyzer.get_domain_from_email(soa_email.replace('.', '@', 1))
                    if soa_domain and (soa_domain in link or link_domain in soa_domain):
                        score_breakdown["dns_verification_bonus"] = max(score_breakdown["dns_verification_bonus"], 5)

            # Add DNS similarity bonus if both domains were analyzed
            if "website_domain" in dns_results:
                similarities = self.dns_analyzer.compare_dns_results(dns_results)
                if similarities:
                    # Map the relation score from compare_dns_results (0-100) to a bonus (0-15)
                    relation_score = similarities["relation_score"]
                    score_breakdown["dns_similarity_bonus"] = min(15, relation_score // 7)  # Max bonus of 15 points

        for link in result.get('links', []):
            result_parts = tldextract.extract(link)
            result_fqdn = result_parts.fqdn

            if result_fqdn.split('.')[0] == "www":
                result_fqdn = result_fqdn[4:]

            # Fully Qualified Domain Name Match
            if email_parts.fqdn == result_fqdn:
                score_breakdown["fully_qualified_domain_name_match"] = max(
                    score_breakdown["fully_qualified_domain_name_match"], 100)
                return score_breakdown

            # Domain Match
            if email_parts.domain == result_parts.domain:
                score_breakdown["domain_match"] = max(score_breakdown["domain_match"], 80)

                # Crossref Data Bonus
                external_ids = result.get('external_ids', {})
                crossref_id = 'N/A'
                for external_id in external_ids:
                    if external_id["type"] == "fundref":
                        crossref_id = external_id["all"][0]

                if crossref_id != 'N/A':
                    score_breakdown["crossref_bonus"] = 5

                # Both Have Subdomains
                if email_parts.subdomain and (result_parts.subdomain and result_parts.subdomain != "www"):
                    score_breakdown["subdomain_mismatch"] = min(
                        score_breakdown["subdomain_mismatch"], -10)

                # Email Has Subdomain
                if email_parts.subdomain and (not result_parts.subdomain or result_parts.subdomain == "www"):
                    score_breakdown["email_is_subdomain_of_website_domain"] = max(
                        score_breakdown["email_is_subdomain_of_website_domain"], 10)

                # Website Has Subdomain
                if not email_parts.subdomain and (result_parts.subdomain and result_parts.subdomain != "www"):
                    score_breakdown["website_is_subdomain_of_email_domain"] = min(
                        score_breakdown["website_is_subdomain_of_email_domain"], -10)

            # Domain Mismatch
            else:
                if result_parts.subdomain and email_parts.subdomain:
                    result_subdomain_parts = result_parts.subdomain.split('.')
                    if result_fqdn.split('.')[0] == "www":
                        result_subdomain_parts = result_subdomain_parts[1:]

                    email_subdomain_parts = email_parts.subdomain.split('.')

                    # Domain of Website Matches Subdomain of Email
                    if result_parts.domain in email_subdomain_parts:
                        score_breakdown["domain_of_website_in_email_subdomain"] = max(
                            score_breakdown["domain_of_website_in_email_subdomain"], 20)

                    # Domain of Email Matches Subdomain of Website
                    if email_parts.domain in result_subdomain_parts:
                        score_breakdown["domain_of_email_in_website_subdomain"] = max(
                            score_breakdown["domain_of_email_in_website_subdomain"], 20)

        score_breakdown["total"] = sum(score_breakdown.values())

        return score_breakdown