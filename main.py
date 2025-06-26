import requests
import dns.resolver
import tldextract
import urllib.parse

tlds = {
    "ac", "ad", "ae", "af", "ag", "ai", "al", "am", "ao", "ar", "as", "at", "au", "aw", "ax", "az",
    "ba", "bb", "bd", "be", "bf", "bg", "bh", "bi", "bj", "bm", "bn", "bo", "br", "bs", "bt", "bv",
    "bw", "by", "bz", "ca", "cc", "cd", "cf", "cg", "ch", "ci", "ck", "cl", "cm", "cn", "co", "cr",
    "cu", "cv", "cw", "cx", "cy", "cz", "de", "dj", "dk", "dm", "do", "dz", "ec", "ee", "eg", "er",
    "es", "et", "eu", "fi", "fj", "fk", "fm", "fo", "fr", "ga", "gb", "gd", "ge", "gf", "gg", "gh",
    "gi", "gl", "gm", "gn", "gp", "gq", "gr", "gs", "gt", "gu", "gw", "gy", "hk", "hm", "hn", "hr",
    "ht", "hu", "id", "ie", "il", "im", "in", "io", "iq", "ir", "is", "it", "je", "jm", "jo", "jp",
    "ke", "kg", "kh", "ki", "km", "kn", "kp", "kr", "kw", "ky", "kz", "la", "lb", "lc", "li", "lk",
    "lr", "ls", "lt", "lu", "lv", "ly", "ma", "mc", "md", "me", "mg", "mh", "mk", "ml", "mm", "mn",
    "mo", "mp", "mq", "mr", "ms", "mt", "mu", "mv", "mw", "mx", "my", "mz", "na", "nc", "ne", "nf",
    "ng", "ni", "nl", "no", "np", "nr", "nu", "nz", "om", "pa", "pe", "pf", "pg", "ph", "pk", "pl",
    "pm", "pn", "pr", "ps", "pt", "pw", "py", "qa", "re", "ro", "rs", "ru", "rw", "sa", "sb", "sc",
    "sd", "se", "sg", "sh", "si", "sj", "sk", "sl", "sm", "sn", "so", "sr", "st", "su", "sv", "sx",
    "sy", "sz", "tc", "td", "tf", "tg", "th", "tj", "tk", "tl", "tm", "tn", "to", "tr", "tt", "tv",
    "tw", "tz", "ua", "ug", "uk", "us", "uy", "uz", "va", "vc", "ve", "vg", "vi", "vn", "vu", "wf",
    "ws", "ye", "yt", "za", "zm", "zw"
}


def get_domain_from_email(email):
    return email.split('@')[-1]


def get_domain_from_url(url):
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    parsed = urllib.parse.urlparse(url)
    domain = parsed.netloc or parsed.path
    return domain.lstrip('www.') if domain.startswith('www.') else domain


def get_ns_records(domain):
    try:
        answers = dns.resolver.resolve(domain, 'NS')
        return [str(r.target).rstrip('.') for r in answers]
    except Exception:
        return []


def get_a_records(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        return [str(r.address) for r in answers]
    except Exception:
        return []


def get_aaaa_records(domain):
    try:
        answers = dns.resolver.resolve(domain, 'AAAA')
        return [str(r.address) for r in answers]
    except Exception:
        return []


def get_cname_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'CNAME')
        return str(answers[0].target).rstrip('.')
    except Exception:
        return None


def get_mx_records(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return sorted([str(r.exchange).rstrip('.') for r in answers])
    except Exception:
        return []


def get_soa_email(domain):
    try:
        answers = dns.resolver.resolve(domain, 'SOA')
        return str(answers[0].rname).rstrip('.')
    except Exception:
        return None


def get_txt_records(domain):
    try:
        answers = dns.resolver.resolve(domain, 'TXT')
        return [r.strings for r in answers]
    except Exception:
        return []


def find_spf(records):
    for record_set in records:
        for record in record_set:
            if b'v=spf1' in record:
                return record.decode()
    return None


def run_dns_analysis(email_domain, website_domain=None):
    results = {}

    if not website_domain:
        website_domain = email_domain

    results["email_domain"] = {
        "domain": email_domain,
        "mx_records": get_mx_records(email_domain),
        "ns_records": get_ns_records(email_domain),
        "a_records": get_a_records(email_domain),
        "aaaa_records": get_aaaa_records(email_domain),
        "cname_record": get_cname_record(email_domain),
        "soa_email": get_soa_email(email_domain),
        "txt_records": get_txt_records(email_domain)
    }
    results["email_domain"]["spf_record"] = find_spf(results["email_domain"]["txt_records"])

    if website_domain != email_domain:
        results["website_domain"] = {
            "domain": website_domain,
            "mx_records": get_mx_records(website_domain),
            "ns_records": get_ns_records(website_domain),
            "a_records": get_a_records(website_domain),
            "aaaa_records": get_aaaa_records(website_domain),
            "cname_record": get_cname_record(website_domain),
            "soa_email": get_soa_email(website_domain),
            "txt_records": get_txt_records(website_domain)
        }
        results["website_domain"]["spf_record"] = find_spf(results["website_domain"]["txt_records"])

    return results


def compare_dns_results(results):
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


def print_dns_comparison(similarities, email_domain, website_domain):
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
        print(
            f"\n       Related SOA emails found")
        print(
            f"              Email SOA: {similarities["email_soa"]}")
        print(
            f"              Website SOA: {similarities["website_soa"]}")

    if similarities['spf_similarity']:
        print(
            f"\n       Related SPF configurations found")
        print(
            f"              Email SPF: {similarities["email_spf"]}")
        print(
            f"              Website SPF: {similarities["website_spf"]}")


def print_individual_dns_analysis(dns_results, email_domain):
    if "website_domain" in dns_results:
        website_domain = dns_results["website_domain"]["domain"]

        similarities = compare_dns_results(dns_results)
        print_dns_comparison(similarities, email_domain, website_domain)
    else:
        print_dns_comparison(None, email_domain, email_domain)


def print_dns_analysis(results):
    if "website_domain" in results:
        similarities = compare_dns_results(results)
        print_dns_comparison(similarities)


def calculate_match_score(email, result, dns_results=None):
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
        "total": 0
    }

    email_full_domain = email.split('@')[-1]
    email_parts = tldextract.extract(email_full_domain)

    # Add DNS verification bonus if applicable
    if dns_results:
        email_a_records = set(dns_results["email_domain"]["a_records"])

        for link in result.get('links', []):
            link_domain = get_domain_from_url(link)

            # Temporary DNS lookup for the website
            try:
                website_a_records = set(get_a_records(link_domain))

                # If there's any overlap in A records, it's a good sign they belong to the same organization
                if email_a_records.intersection(website_a_records) and email_a_records and website_a_records:
                    score_breakdown["dns_verification_bonus"] = 10
                    break
            except:
                pass

            # Check SOA email patterns
            soa_email = dns_results["email_domain"]["soa_email"]
            if soa_email:
                soa_domain = get_domain_from_email(soa_email.replace('.', '@', 1))
                if soa_domain and (soa_domain in link or link_domain in soa_domain):
                    score_breakdown["dns_verification_bonus"] = max(score_breakdown["dns_verification_bonus"], 5)

        # Add DNS similarity bonus if both domains were analyzed
        if "website_domain" in dns_results:
            similarities = compare_dns_results(dns_results)
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
            crossref_id = result.get('external_ids', {}).get('FundRef', {}).get('all', ['N/A'])[0]
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


def generate_ror_queries(email):
    extracted = tldextract.extract(email.split('@')[-1])

    parts = extracted.subdomain.split('.') + [extracted.domain] if extracted.subdomain else [extracted.domain]

    suffix = extracted.suffix

    queries = []
    if suffix.split('.')[-1] in tlds:
        base_query = f"https://api.ror.org/organizations?query.advanced=country.country_code:{suffix.upper()}%20AND%20links:"
    else:
        base_query = f"https://api.ror.org/organizations?query.advanced=links:"

    # Generate all possible domain variants, including intermediate subdomains
    domain_variants = set()
    for i in range(len(parts)):
        domain_variants.add(".".join(parts[i:]))
        if i < len(parts) - 1:
            domain_variants.add(".".join(parts[i:-1]))

    domain_variants.update(parts)

    for variant in sorted(domain_variants, key=lambda x: x.count('.')):
        queries.append(base_query + variant)

    return queries


def fetch_ror_data(queries):
    results = []
    for query in queries:
        try:
            response = requests.get(query)
            if response.status_code == 200:
                data = response.json()
                results.extend(data.get("items", []))
        except requests.RequestException as e:
            print(f"Error fetching data from {query}: {e}")
    return results


def fetch_crossref_data(crossref_id):
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

def find_org_associated_with_email(email: str) -> None:
    # Extract domain from email for DNS analysis
    email_domain = get_domain_from_email(email)

    # Get initial DNS results for email domain only
    initial_dns_results = run_dns_analysis(email_domain)

    # Generate ROR queries
    queries = generate_ror_queries(email)

    print("\nGenerated ROR Queries:")
    for query in queries:
        print(f"  {query}")

    results = fetch_ror_data(queries)

    if not results:
        print("\nNo ROR results found")
        print_dns_analysis(initial_dns_results)
        return

    print(f"\nFound {len(results)} potential organization matches")

    # Score and sort results
    scored_results = []
    for result in results:
        dns_results_for_result = initial_dns_results.copy()
        if result.get('links'):
            website_domain = get_domain_from_url(result['links'][0])
            if website_domain != email_domain:
                dns_results_for_result = run_dns_analysis(email_domain, website_domain)

        scored_results.append(
            (result, calculate_match_score(email, result, dns_results_for_result), dns_results_for_result))

    scored_results.sort(key=lambda x: x[1]["total"], reverse=True)

    print("\nOrganization Matches:")
    print("=" * 80)

    for i, (result, score_breakdown, dns_results_for_result) in enumerate(scored_results, start=1):
        crossref_id = result.get('external_ids', {}).get('FundRef', {}).get('all', ['N/A'])[0]
        crossref_data = fetch_crossref_data(crossref_id) if crossref_id != 'N/A' else None

        print(f"\n{i}. {result.get('name')}")
        print(f"   Match Score: {score_breakdown['total']}%")
        print(f"   Website(s): {', '.join(result.get('links', []))}")

        print("\n   Score Breakdown:")
        print(
            f"      Fully Qualified Domain Match        : {score_breakdown['fully_qualified_domain_name_match']:>3}/100 points")
        print(
            f"      Base Domain Match                   : {score_breakdown['domain_match']:>3}/80  points")

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
        print(
            f"      Crossref Bonus                      : {score_breakdown['crossref_bonus']:>3}/5   points")

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

        print_individual_dns_analysis(dns_results_for_result, email_domain)

        print("\n" + "-" * 80)

def main():
    email = input("Enter the email address: ")
    find_org_associated_with_email(email)

if __name__ == "__main__":
    main()
