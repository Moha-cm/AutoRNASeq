suppressPackageStartupMessages(library(DESeq2))
suppressPackageStartupMessages(library(dplyr))

# Define padj and log2FoldChange thresholds
padj <- 0.05
log2FoldChange <- 1

# Read input files
Expression_df <- read.csv(snakemake@input[[1]], row.names = 1,check.names = FALSE)
condition_df <- read.csv(snakemake@input[[2]])
reference_df <- read.csv(snakemake@input[[3]], row.names = 3)

# Create DESeq2 dataset
dds <- DESeqDataSetFromMatrix(countData = Expression_df, colData = condition_df, design = ~ Condition)

# Ensure the condition column is correctly factorized
dds$Condition <- factor(dds$Condition)

# Perform variance stabilizing transformation
vsd <- varianceStabilizingTransformation(dds, blind = FALSE)

# Estimate size factors and normalize counts
dds <- estimateSizeFactors(dds)
norm_counts <- counts(dds, normalized = TRUE)

# Perform DESeq analysis
dds <- DESeq(dds)
resc <- data.frame(results(dds))
resc <- round(resc, digits = 3)

# Assign significance groups
resc$group <- "insig"
resc$group[(resc$padj <= padj) & (resc$log2FoldChange >= log2FoldChange)] <- "up"
resc$group[(resc$padj <= padj) & (resc$log2FoldChange <= -log2FoldChange)] <- "down"
resc$group <- factor(resc$group, levels = c("insig", "up", "down"))

# Merge results with reference data
data <- merge(resc, reference_df, by = 0, how = "inner")
rownames(data) <- data$Row.names
data <- data[, -1]

# Filter up and down-regulated genes and merge with reference data
up_Regulated <- resc %>% filter(group == "up")
up_Regulated <- merge(up_Regulated, reference_df, by = 0, how = "inner")

down_Regulated <- resc %>% filter(group == "down")
down_Regulated <- merge(down_Regulated, reference_df, by = 0, how = "inner")

# Write outputs to CSV files
write.csv(data, file = snakemake@output[[1]], row.names = TRUE)
write.csv(up_Regulated, file = snakemake@output[[2]], row.names = FALSE)
write.csv(down_Regulated, file = snakemake@output[[3]], row.names = FALSE)
