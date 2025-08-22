import dns.resolver
import urllib.parse

"""
      |   
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""


class DNSAnalyzer:
    """
    Performs comprehensive DNS analysis to determine relationships between email domains and website domains.
    """

    def __init__(self):
        """
        Initialize the DNSAnalyzer.

        Parameters:
            None

        Returns:
            None
        """
        pass

    def get_domain_from_email(self, email):
        """
        Extract the domain portion from an email address.

        Parameters:
            email (str): The email address to parse (e.g., "user@example.com").

        Returns:
            str: The domain portion of the email (everything after '@').
        """
        return email.split('@')[-1]

    def get_domain_from_url(self, url):
        """
        Extract and normalize the domain from a URL.

        Handles URLs with or without protocol prefixes and removes 'www.' subdomain if present.

        Parameters:
            url (str): The URL to parse. Can include or omit http/https protocol.

        Returns:
            str: The normalized domain name.
        """
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc or parsed.path
        return domain.lstrip('www.') if domain.startswith('www.') else domain

    def get_ns_records(self, domain):
        """
        Retrieve the NS (Name Server) records for a domain.

        Parameters:
            domain (str): The domain to query.

        Returns:
            list[str]: List of name server hostnames with trailing dots removed.
                      Returns empty list if query fails.
        """
        try:
            answers = dns.resolver.resolve(domain, 'NS')
            return [str(r.target).rstrip('.') for r in answers]
        except Exception:
            return []

    def get_a_records(self, domain):
        """
        Retrieve the A records (IPv4 addresses) for a domain.

        Parameters:
            domain (str): The domain to query.

        Returns:
            list[str]: List of IPv4 addresses. Returns empty list if query fails.
        """
        try:
            answers = dns.resolver.resolve(domain, 'A')
            return [str(r.address) for r in answers]
        except Exception:
            return []

    def get_aaaa_records(self, domain):
        """
        Retrieve the AAAA records (IPv6 addresses) for a domain.

        Parameters:
            domain (str): The domain to query.

        Returns:
            list[str]: List of IPv6 addresses. Returns empty list if query fails.
        """
        try:
            answers = dns.resolver.resolve(domain, 'AAAA')
            return [str(r.address) for r in answers]
        except Exception:
            return []

    def get_cname_record(self, domain):
        """
        Retrieve the CNAME record for a domain.

        Parameters:
            domain (str): The domain to query.

        Returns:
            str or None: The canonical name with trailing dot removed,
                        or None if no CNAME record exists or query fails.
        """
        try:
            answers = dns.resolver.resolve(domain, 'CNAME')
            return str(answers[0].target).rstrip('.')
        except Exception:
            return None

    def get_mx_records(self, domain):
        """
        Retrieve the MX (Mail Exchange) records for a domain.

        Parameters:
            domain (str): The domain to query.

        Returns:
            list[str]: Sorted list of mail server hostnames with trailing dots removed.
                      Returns empty list if query fails.
        """
        try:
            answers = dns.resolver.resolve(domain, 'MX')
            return sorted([str(r.exchange).rstrip('.') for r in answers])
        except Exception:
            return []

    def get_soa_email(self, domain):
        """
        Retrieve the SOA (Start of Authority) responsible person email for a domain.

        Parameters:
            domain (str): The domain to query.

        Returns:
            str or None: The responsible person's email from SOA record with trailing dot removed,
                        or None if query fails.
        """
        try:
            answers = dns.resolver.resolve(domain, 'SOA')
            return str(answers[0].rname).rstrip('.')
        except Exception:
            return None

    def get_txt_records(self, domain):
        """
        Retrieve all TXT records for a domain.

        Parameters:
            domain (str): The domain to query.

        Returns:
            list[list[bytes]]: List of TXT record string lists. Each TXT record can contain
                              multiple strings. Returns empty list if query fails.
        """
        try:
            answers = dns.resolver.resolve(domain, 'TXT')
            return [r.strings for r in answers]
        except Exception:
            return []

    def find_spf(self, records):
        """
        Find and extract SPF (Sender Policy Framework) record from TXT records.

        Searches through TXT records to find the one containing SPF policy.

        Parameters:
            records (list[list[bytes]]): List of TXT record string lists from get_txt_records().

        Returns:
            str or None: The SPF record as a decoded string, or None if no SPF record found.
        """
        for record_set in records:
            for record in record_set:
                if b'v=spf1' in record:
                    return record.decode()
        return None

    def run_dns_analysis(self, email_domain, website_domain=None):
        """
        Perform comprehensive DNS analysis on email and optionally website domains.

        Gathers all DNS record types for the specified domains.

        Parameters:
            email_domain (str): The domain from the email address to analyze.
            website_domain (str, optional): The website domain to analyze. If None,
                                          only email_domain is analyzed.

        Returns:
            dict: DNS analysis results containing:
                 - email_domain: Dict with all DNS records for email domain
                 - website_domain: Dict with all DNS records for website domain (if different)
                 Both domains include: domain, mx_records, ns_records, a_records,
                 aaaa_records, cname_record, soa_email, txt_records, spf_record
        """
        results = {}

        if not website_domain:
            website_domain = email_domain

        results["email_domain"] = {
            "domain": email_domain,
            "mx_records": self.get_mx_records(email_domain),
            "ns_records": self.get_ns_records(email_domain),
            "a_records": self.get_a_records(email_domain),
            "aaaa_records": self.get_aaaa_records(email_domain),
            "cname_record": self.get_cname_record(email_domain),
            "soa_email": self.get_soa_email(email_domain),
            "txt_records": self.get_txt_records(email_domain)
        }
        results["email_domain"]["spf_record"] = self.find_spf(results["email_domain"]["txt_records"])

        if website_domain != email_domain:
            results["website_domain"] = {
                "domain": website_domain,
                "mx_records": self.get_mx_records(website_domain),
                "ns_records": self.get_ns_records(website_domain),
                "a_records": self.get_a_records(website_domain),
                "aaaa_records": self.get_aaaa_records(website_domain),
                "cname_record": self.get_cname_record(website_domain),
                "soa_email": self.get_soa_email(website_domain),
                "txt_records": self.get_txt_records(website_domain)
            }
            results["website_domain"]["spf_record"] = self.find_spf(results["website_domain"]["txt_records"])

        return results

    def compare_dns_results(self, results):
        """
        Compare DNS results between email and website domains to assess relationship.

        Analyzes similarities in DNS records to determine if domains belong to the same organization.
        Calculates a relationship score based on matching records and configurations.

        Parameters:
            results (dict): DNS analysis results from run_dns_analysis() containing both
                           email_domain and website_domain data.

        Returns:
            dict or None: Comparison results containing:
                         - matching_nameservers: List of common name servers
                         - matching_mx_records: List of common mail servers
                         - matching_a_records: List of common IPv4 addresses
                         - matching_aaaa_records: List of common IPv6 addresses
                         - soa_email_relation: Boolean indicating related SOA emails
                         - spf_similarity: Boolean indicating similar SPF configurations
                         - email_soa/website_soa: SOA email addresses
                         - email_spf/website_spf: SPF record strings
                         - relation_score: Numerical score (0-100) indicating relationship strength
                         Returns None if website_domain not in results.
        """
        if "website_domain" not in results:
            return None

        similarities = {
            "matching_nameservers": [],
            "matching_mx_records": [],
            "matching_a_records": [],
            "matching_aaaa_records": [],
            "soa_email_relation": False,
            "spf_similarity": False,
            "email_soa": [],
            "website_soa": [],
            "email_spf": [],
            "website_spf": [],
            "relation_score": 0
        }

        email_domain = results["email_domain"]
        website_domain = results["website_domain"]

        email_ns = set(email_domain["ns_records"])
        website_ns = set(website_domain["ns_records"])
        similarities["matching_nameservers"] = sorted(list(email_ns.intersection(website_ns)))

        email_mx = set(email_domain["mx_records"])
        website_mx = set(website_domain["mx_records"])
        similarities["matching_mx_records"] = sorted(list(email_mx.intersection(website_mx)))

        email_a = set(email_domain["a_records"])
        website_a = set(website_domain["a_records"])
        similarities["matching_a_records"] = sorted(list(email_a.intersection(website_a)))

        email_aaaa = set(email_domain["aaaa_records"])
        website_aaaa = set(website_domain["aaaa_records"])
        similarities["matching_aaaa_records"] = sorted(list(email_aaaa.intersection(website_aaaa)))

        email_soa = email_domain["soa_email"]
        website_soa = website_domain["soa_email"]

        similarities["email_soa"] = email_soa
        similarities["website_soa"] = website_soa

        if email_soa and website_soa:
            email_soa_domain = email_soa.replace('.', '@', 1).split('@')[-1]
            website_soa_domain = website_soa.replace('.', '@', 1).split('@')[-1]
            similarities["soa_email_relation"] = (
                    email_soa == website_soa or
                    email_soa_domain == website_soa_domain or
                    email_domain["domain"] in website_soa or
                    website_domain["domain"] in email_soa
            )

        email_spf = email_domain["spf_record"]
        website_spf = website_domain["spf_record"]

        similarities["email_spf"] = email_spf
        similarities["website_spf"] = website_spf

        if email_spf and website_spf:
            email_spf_elements = set(email_spf.split())
            website_spf_elements = set(website_spf.split())
            common_elements = email_spf_elements.intersection(website_spf_elements)

            includes_match = False
            ip_match = False

            for element in common_elements:
                if element.startswith('include:'):
                    includes_match = True
                if element.startswith('ip4:') or element.startswith('ip6:'):
                    ip_match = True

            similarities["spf_similarity"] = includes_match or ip_match

        relation_score = 0

        if similarities["matching_nameservers"]:
            relation_score += 25 * min(len(similarities["matching_nameservers"]), 2)

        if similarities["matching_a_records"]:
            relation_score += 30

        if similarities["matching_aaaa_records"]:
            relation_score += 15

        if similarities["matching_mx_records"]:
            relation_score += 20

        if similarities["soa_email_relation"]:
            relation_score += 10

        if similarities["spf_similarity"]:
            relation_score += 10

        similarities["relation_score"] = min(relation_score, 100)

        return similarities
