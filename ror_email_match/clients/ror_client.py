import requests
import tldextract

"""
      |   
  \  ___  /                           _________
 _  /   \  _    GÉANT                 |  * *  | Co-Funded by
    | ~ |       Trust & Identity      | *   * | the European
     \_/        Incubator             |__*_*__| Union
      =
"""


class RORClient:
    """
    A client for interacting with the Research Organization Registry (ROR) API.
    """

    def __init__(self):
        """
        Initialize the RORClient with a comprehensive list of top-level domains.

        Creates a set of valid TLDs for country-specific query generation.

        Parameters:
            None

        Returns:
            None
        """
        self.tlds = {
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

    def generate_ror_queries(self, email):
        """
        Generate ROR API query URLs based on email domain.

        Extracts domain components from email address and creates multiple query variants
        to maximize chances of finding matching organizations in ROR database.

        Parameters:
            email (str): The email address to analyze for generating queries.

        Returns:
            list[str]: List of ROR API query URLs targeting different domain variants.
                      Includes country-specific queries when applicable TLD is detected.
        """
        extracted = tldextract.extract(email.split('@')[-1])

        parts = extracted.subdomain.split('.') + [extracted.domain] if extracted.subdomain else [extracted.domain]

        suffix = extracted.suffix

        queries = []
        if suffix.split('.')[-1] in self.tlds:
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

    def fetch_ror_data(self, queries):
        """
        Execute multiple ROR API queries and aggregate results.

        Makes HTTP requests to each provided query URL and combines all organization
        results into a single list.

        Parameters:
            queries (list[str]): List of ROR API query URLs to execute.

        Returns:
            list[dict]: Aggregated list of organization data dictionaries from ROR API.
                       Each dictionary contains organization metadata like name, links,
                       and external identifiers.
        """
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
