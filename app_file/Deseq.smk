configfile: "config.yaml"
rule Deseq_analysis:
    input:
      raw_counts = config['raw_counts'],
      condition = config['meta_data'],
      reference_geneids = "data/ensembl_gene_ids.csv"
    output:
      deseq_result = "reports/deseq_results.csv",
      up_regulated = "reports/up_regulated_genes.csv",
      down_regulated = "reports/down_regulated_genes.csv"
      
    conda:
        "envs/r_environment.yaml"
    script:
        "scripts/Deseq.R"


    
    





