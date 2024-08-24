suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(stringr))
suppressPackageStartupMessages(library(survminer))
suppressPackageStartupMessages(library(survival))


survival_df <- read.csv(snakemake@input[[1]], row.names = 1,check.names = FALSE)
Threshold_value <-  snakemake@params$threshold
gene <- snakemake@params$gene

survival_df$group <- ifelse(survival_df[[gene]] >=Threshold_value,"High","low")
survival_df$deceased <- ifelse(survival_df$vital_status == "Alive", FALSE, TRUE)

survival_df$overall_survival <- ifelse(survival_df$vital_status == "Alive",
                                    survival_df$days_to_last_follow_up,
                                   survival_df$days_to_death)



fit <- survfit(Surv(overall_survival, deceased) ~ group, data = survival_df)

survival_plotA1 <- ggsurvplot(fit,
                              data = survival_df,
                              pval = TRUE,
                              risk.table = TRUE,
                              conf.int = FALSE,
                              tables.height = 0.2,
                              tables.theme = theme_cleantable(),
                              surv.median.line = "hv",
                              palette = c("#ff0000", "#2E9FDF"),
                              ggtheme = theme_classic(),
                              legend.title = gene)

# Center the title
survival_plotA1$plot <- survival_plotA1$plot +
  ggtitle(paste0("Survival Plot for ", gene, " Gene Expression")) +
  theme(plot.title = element_text(hjust = 0.5))

# Save the plot
ggsave(
  filename = snakemake@output[[1]],
  plot = survival_plotA1$plot, # Extract the plot from the list
  device = "png",
  height = 6,
  width = 10,
  units = "in",
  dpi = 300
)

write.csv(survival_df, file = snakemake@output[[2]], row.names = TRUE)