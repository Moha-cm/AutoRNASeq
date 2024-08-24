suppressPackageStartupMessages(library(ggplot2))
suppressPackageStartupMessages(library(plotly))
suppressPackageStartupMessages(library(dplyr))
suppressPackageStartupMessages(library(stringr))


deseq_df <- read.csv(snakemake@input[[1]], row.names = 1,check.names = FALSE)

padj <- 0.05
log2FoldChange <- 1

p <- ggplot(deseq_df, aes(x = log2FoldChange, y = -log10(padj), color = group, label = Gene_name)) +
  geom_point(size = 2) +
  xlab("log2FoldChange") +
  geom_hline(yintercept = -log10(0.05), size = 0.5, colour = 'red', linetype = "dotted") +
  geom_vline(xintercept = c(log2FoldChange, log2FoldChange), size = 0.5, colour = 'red', linetype = "dotted") +
  ylab("-log10(padj)") +
  ggtitle("Volcano Plot of DESeq2 Results") +
  theme_bw() +
  theme(plot.title = element_text(hjust = 0.5)) +
  scale_colour_manual(values = c("black", "blue", "green"))

# Save the ggplot as a PNG image
ggsave(
  filename = snakemake@output[[1]],
  plot = p,
  device = "png",
  height = 6,
  width = 6,
  units = "in",
  dpi = 300
)