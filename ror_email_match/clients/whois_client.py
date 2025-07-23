import whois


class WHOISClient:
    def __init__(self):
        pass

    @staticmethod
    def query_domain(domain):
        if not domain:
            print("No domain provided.")
            return None

        result = whois.whois(domain)

        relevant_fields = {
            "domain_name": result.domain_name,
            "org": result.org,
            "name": result.name,
            "emails": result.emails,
            "address": result.address,
            "city": result.city,
            "state": result.state,
            "country": result.country,
        }

        return relevant_fields

    @staticmethod
    def compare_domains(domain1, domain2):
        if not domain1 or not domain2:
            print("No domain provided.")
            return None

        domain1_results = WHOISClient.query_domain(domain1)
        domain2_results = WHOISClient.query_domain(domain2)

        results = {}
        match_score = 0

        if ((domain1_results['domain_name'] == domain2_results['domain_name']) and
                domain1_results['domain_name'] is not None and domain2_results['domain_name'] is not None):
            results['domain_name'] = domain1_results['domain_name']
            match_score += 100

        if ((domain1_results['org'] == domain2_results['org']) and
                domain1_results['org'] is not None and domain2_results['org'] is not None):
            results['org'] = domain1_results['org']
            match_score += 100

        if ((domain1_results['name'] == domain2_results['name']) and
                domain1_results['name'] is not None and domain2_results['name'] is not None):
            results['name'] = domain1_results['name']
            match_score += 100

        if (((domain1_results['address'] == domain2_results['address']) and
             domain1_results['address'] is not None and domain2_results['address'] is not None) and

                ((domain1_results['city'] == domain2_results['city']) and
                 domain1_results['city'] is not None and domain2_results['city'] is not None) and

                ((domain1_results['state'] == domain2_results['state']) and
                 domain1_results['state'] is not None and domain2_results['state'] is not None) and

                ((domain1_results['country'] == domain2_results['country']) and
                 domain1_results['country'] is not None and domain2_results['country'] is not None)):
            results['address'] = domain1_results['address']
            match_score += 50

        if domain1_results['emails'] is not None and domain2_results['emails'] is not None:
            for email1 in domain1_results['emails']:
                for email2 in domain2_results['emails']:
                    if email1 == email2:
                        if 'emails' not in results:
                            results['emails'] = []
                        results['emails'].append(email1)
            match_score += 80

        return match_score % 100, results
