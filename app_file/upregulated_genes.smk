configfile: "config.yaml"
include: "Deseq.smk"

rule upregulated_gene_Analysis:
    input:
        deseq_df =  "reports/deseq_results.csv"
    output:
        molecular_df = "reports/upregulated_genes_Molecular_function.csv",
        cellular_df = "reports/upregulated_genes_cellular_function.csv",
        biological_df = "reports/upregulated_genes_biological_function.csv",
        pathway_df = "reports/upregulated_genes_pathway_enrichment.csv",
        reactome_df = "reports/upregulated_genes_reactome_pathway.csv",
        wikipathway_df = "reports/upregulated_genes_wiki_pathway.csv",
        disease_df = "reports/upregulated_genes_disease_pathway.csv"
        # cancer_genes_df =  "reports/upregulated_cancer_genes.csv",
        # gene_network_df =  "reports/upregulated_gene_network.csv"


    conda:
        "envs/r_environment.yaml"
    script:
        "scripts/upregulated_genes_pathway.R"

