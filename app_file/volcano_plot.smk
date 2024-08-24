include: "Deseq.smk"


rule volcanoplot:
    input:
        deseq_df = "reports/deseq_results.csv"
    output:
        plot = "reports/vol.png"
    conda:
        "envs/r_environment.yaml"
    script:
        "scripts/volcano.R"
