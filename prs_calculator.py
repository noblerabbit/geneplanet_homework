import ensembl_utils
import numpy as np
import pandas as pd

# loading the Table 4 information to memory

def get_prs(sample_number):
    df = pd.read_csv("../data/77SNP_Breast_Cancer_Table4.csv")
    df.set_index("SNP", inplace=True)
    # print(df.head())

    yield from ensembl_utils.ensembl_snp_collector_api(df.index, sample_number) 
    
    ind_snps = ensembl_utils.SNP_COLLECTOR
    
    # Append Individual Allelles column to the Table
    df['SAMPLE'] = pd.DataFrame([ind_snps["snps"]]).T
    
    X_k = {}
    for row in df.index:
        #get minor allele
        ref = df.loc[row].Alleles.split("/")[-1]
        sample = df.loc[row].SAMPLE.split("|")
        X_k[row] = sample.count(ref)
    
    # Append X_k to the Table 4
    df["X_k"] = pd.DataFrame([X_k]).T
    
    # yield df
    # Caluclate PRS for each type of Breast cancer
    
    # Initiating the values
    PRS_all = 0
    PRS_ER_neg = 0
    PRS_ER_pos = 0
    
    # iterating over each row in the column and summing the contribution of each SNP
    # to obtain the final PRS score (based on the PRS equation)
    
    for row in df.index:
        PRS_all += np.log(df.loc[row]["All breast cancers"])*df.loc[row]["X_k"]
        PRS_ER_pos += np.log(df.loc[row]["ER-positive disease"])*df.loc[row]["X_k"]
        PRS_ER_neg += np.log(df.loc[row]["ER-negative disease"])*df.loc[row]["X_k"]
    
    yield "<h3>All breast cancers PRS value: <b>{}</h3>".format(round(PRS_all, 3))
    yield "<h3>ER-positive disease PRS value: <b>{}</h3>".format(round(PRS_ER_pos,3))
    yield "<h3>ER-negative disease PRS value: <b>{}</h3>".format(round(PRS_ER_neg, 3))
    
    PRS = {"All breast cancers": PRS_all,
           "ER-positive disease": PRS_ER_pos,
           "ER-negative disease": PRS_ER_neg}
           
    # return PRS
    
if __name__ == "__main__":
  print(get_prs("HG00099"))
  