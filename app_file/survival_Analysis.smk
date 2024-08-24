configfile: "config.yaml"

rule survival_analysis:
    input:
     survival_df = config['survival_df']
    
    output:
        plot = "reports/survival_plot.png",
        surv_df = "reports/survival_data.csv"

    params:
     threshold= config['thresh_hold'],
     gene=  config['Gene']

    conda:
        "envs/r_environment.yaml"
    script:
        "scripts/survival_plot.R"


    
    





