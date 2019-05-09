# GenePlanet Homework - Task 2

#### Calculate the individual’s Polygenic Risk Score (PRS) for Breast Cancer based on the 77 SNPs as explained in the article*.</h3>
**Prediction of Breast Cancer Risk Based on Profiling With Common Genetic Variants
(J Natl Cancer Inst. 2015 Apr 8;107(5). pii: djv036. doi: 10.1093/jnci/djv036. Print 2015 May.)*


## File descriptions

* **GenePlanet_Homework_Task_2.ipnyb - Homework written in Jupyter Notebook**
* ensembl_utils.py - script to communicate with Ensembl database
* ./data/77SNP_Breast_Cancer_Table4.csv - Copy of Table 4 from the article
* prs_calculator.py - script to calculare PRS (similar to what is in notebook) that can be used by API
* /api/app.py - Flask server API implementation. Demo how we can deploy PRS caluclator as WWW service.

