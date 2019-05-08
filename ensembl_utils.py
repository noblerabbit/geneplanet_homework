import sys
import json
import time
from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

class EnsemblRestClient(object):
    def __init__(self, server='http://rest.ensembl.org', reqs_per_sec=15):
        self.server = server
        self.reqs_per_sec = reqs_per_sec
        self.req_count = 0
        self.last_req = 0

    def perform_rest_action(self, endpoint, hdrs=None, params=None):
        if hdrs is None:
            hdrs = {}

        if 'Content-Type' not in hdrs:
            hdrs['Content-Type'] = 'application/json'

        if params:
            endpoint += '?' + urlencode(params)

        data = None

        # check if we need to rate limit ourselves
        if self.req_count >= self.reqs_per_sec:
            delta = time.time() - self.last_req
            if delta < 1:
                time.sleep(1 - delta)
            self.last_req = time.time()
            self.req_count = 0
        
        try:
            request = Request(self.server + endpoint, headers=hdrs)
            response = urlopen(request)
            content = response.read()
            if content:
                data = json.loads(content)
            self.req_count += 1

        except HTTPError as e:
            # check if we are being rate limited by the server
            if e.code == 429:
                if 'Retry-After' in e.headers:
                    retry = e.headers['Retry-After']
                    time.sleep(float(retry))
                    self.perform_rest_action(endpoint, hdrs, params)
            else:
                sys.stderr.write('Request failed for {0}: Status code: {1.code} Reason: {1.reason}\n'.format(endpoint, e))
           
        return data

    def get_snp(self, snp_name):
        snp = self.perform_rest_action(
            endpoint='/variation/human/{0}'.format(snp_name), 
            params={'genotypes': '1'}
        )
        return snp

# def run(snp_name):
#     client = EnsemblRestClient()
#     snp = client.get_snp(snp_name)
#     return snp

def get_snp_sample(snp_dict, individual_name):
    genotypes = snp_dict["genotypes"]
    
    # get reference allele pair
    ref = ""
    alt = ""
    if snp_dict['ancestral_allele'] != None  :ref = snp_dict['ancestral_allele'] + "|"
    if snp_dict['minor_allele'] != None  :alt = "|" + snp_dict['minor_allele']
    reference_genotype = ref + alt
    
    for g in genotypes:
        if individual_name == g["sample"].split(':')[-1]:
#             print("Found_Match")
            return g["genotype"]

    print("[INFO] No indivudal SNP. Getting reference allele pair.")
    return reference_genotype

def ensembl_snp_collector(snp_list, sample_name):
    """Returns dict of allele pair (ie C|T) values for specific Ensembl sample genotype 
    (genotype of an invididual from the Ensembl database). Samples have code names (ie "HG00099")."""
    
    start = time.time()
    
    info = {}
    info["sample_name"] = sample_name
    snp = {}
    
    print("[INFO] Collecting {} SNPs for sample {}".format(len(snp_list), sample_name))
    # establish connection to Ensembl database
    client = EnsemblRestClient()
    
    # iterate through list of snps and query the database for each snp and store snp to dict
    for i, snp_name in enumerate(snp_list):
        print("[INFO] Collecting ({}/{}): {}".format(i+1, len(snp_list), snp_name))
        snp_info = client.get_snp(snp_name)
        snp[snp_name] = get_snp_sample(snp_info, sample_name)
    
    # organize info_dict to return
    info["snps"] = snp
    
    print("[INFO] SNPs for the sample collected in {}".format(round(time.time()-start,0)))
    return info


global SNP_COLLECTOR
SNP_COLLECTOR = {}

def ensembl_snp_collector_api(snp_list, sample_name):
    """
    The API version of the above function suitable for Flask output. [INFO] statemens can be sent
    as HTTP stream.
    Returns dict of allele pair (ie C|T) values for specific Ensembl sample genotype 
    (genotype of an invididual from the Ensembl database). Samples have code names (ie "HG00099")."""
    
    start = time.time()
    
    info = {}
    SNP_COLLECTOR["sample_name"] = sample_name
    snp = {}
    
    yield "<h3>Collecting {} SNPs for sample {}</h3>".format(len(snp_list), sample_name)
    # establish connection to Ensembl database
    client = EnsemblRestClient()
    
    # iterate through list of snps and query the database for each snp and store snp to dict
    for i, snp_name in enumerate(snp_list):
        yield "[INFO] Collecting ({}/{}): {}<br>".format(i+1, len(snp_list), snp_name)
        snp_info = client.get_snp(snp_name)
        snp[snp_name] = get_snp_sample(snp_info, sample_name)
    
    # organize info_dict to return
    SNP_COLLECTOR["snps"] = snp
    
    yield "[INFO] SNPs for the sample collected in {}<br>".format(round(time.time()-start,0))   

if __name__ == '__main__':
    snp_list = ['rs78540526', 'rs75915166', 'rs554219', 'rs7726159', 'rs10069690']
    snips = ensembl_snp_collector(snp_list, "HG00158")
    print(snips)