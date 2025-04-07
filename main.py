import tldextract
import requests
import json

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


import tldextract


def calculate_match_score(email, result):
    score_breakdown = {
        "fully_qualified_domain_name_match": 0,
        "domain_match": 0,
        "website_is_subdomain_of_email_domain": 0,
        "email_is_subdomain_of_website_domain": 0,
        "subdomain_mismatch": 0,
        "domain_of_email_in_website_subdomain": 0,
        "domain_of_website_in_email_subdomain": 0,
        "crossref_bonus": 0,
        "total": 0
    }

    email_full_domain = email.split('@')[-1]
    email_parts = tldextract.extract(email_full_domain)

    for link in result.get('links', []):
        result_parts = tldextract.extract(link)
        result_fqdn = result_parts.fqdn

        if result_fqdn.split('.')[0] == "www":
            result_fqdn = result_fqdn[4:]

        # Fully Qualified Domain Name Match
        if email_parts.fqdn == result_fqdn:
            score_breakdown["fully_qualified_domain_name_match"] = max(score_breakdown["fully_qualified_domain_name_match"], 100)
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


def main():
    # email = "name.surname@sztaki.mta.hu"
    email = input("Enter the email address: ")

    queries = generate_ror_queries(email)

    print("\nGenerated Queries:")
    for query in queries:
        print(query)

    results = fetch_ror_data(queries)

    if not results:
        print("\nNo results")
        return

    scored_results = []
    for result in results:
        scored_results.append((result, calculate_match_score(email, result)))

    scored_results.sort(key=lambda x: x[1]["total"], reverse=True)

    print("\nFetched Results:\n" + "=" * 80)

    for i, (result, score_breakdown) in enumerate(scored_results, start=1):
        crossref_id = result.get('external_ids', {}).get('FundRef', {}).get('all', ['N/A'])[0]
        crossref_data = fetch_crossref_data(crossref_id) if crossref_id != 'N/A' else None

        print(f"\n{i}. \033[1m{result.get('name')}\033[0m")
        print(f"   \033[96mMatch Score: {score_breakdown['total']}%\033[0m")
        print(f"   Website(s): {', '.join(result.get('links', []))}")

        print("\n   \033[95mScore Breakdown:\033[0m")
        print(
            f"   ├─ Fully Qualified Domain Match        : \033[93m{score_breakdown['fully_qualified_domain_name_match']:>3}\033[0m/100 points")
        print(
            f"   ├─ Base Domain Match                   : \033[93m{score_breakdown['domain_match']:>3}\033[0m/80  points")

        if score_breakdown["domain_match"] > 0:
            print(
                f"   │  └─ Email is Subdomain of Website    : \033[93m{score_breakdown['email_is_subdomain_of_website_domain']:>3}\033[0m/10  points")
            print(
                f"   │  └─ Website is Subdomain of Email    : \033[93m{score_breakdown['website_is_subdomain_of_email_domain']:>3}\033[0m/-10 points")
            print(
                f"   │  └─ Subdomain Mismatch Penalty       : \033[93m{score_breakdown['subdomain_mismatch']:>3}\033[0m/-10 points")
        else:
            print(
                f"   ├─ Email in Website Subdomain          : \033[93m{score_breakdown['domain_of_email_in_website_subdomain']:>3}\033[0m/20  points")
            print(
                f"   ├─ Website in Email Subdomain          : \033[93m{score_breakdown['domain_of_website_in_email_subdomain']:>3}\033[0m/20  points")
        print(
            f"   └─ Crossref Bonus                      : \033[93m{score_breakdown['crossref_bonus']:>3}\033[0m/5   points")

        print(f"\n   \033[95mCrossref ID:\033[0m {crossref_id}")

        if crossref_data:
            print("   \033[95mCrossref Data:\033[0m")
            print(f"   ├─ Name        : {crossref_data.get('name', 'N/A')}")
            print(f"   ├─ Location    : {crossref_data.get('location', 'N/A')}")
            print(f"   └─ Works Count : {crossref_data.get('work-count', 'unknown')}")

            alt_names = crossref_data.get('alt-names', [])
            if alt_names:
                preview = ', '.join(alt_names[:3])
                suffix = ", ..." if len(alt_names) > 3 else ""
                print(f"      Also known as: {preview}{suffix}")

        print("\n" + "-" * 80)

    # print("\nFetched Results:")
    # print(json.dumps(results, indent=4))
    #
    # print("-" * 30)
    #
    # print(json.dumps(crossref_data, indent=4))


if __name__ == "__main__":
    main()
