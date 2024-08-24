suppressPackageStartupMessages(library(org.Hs.eg.db))
suppressPackageStartupMessages(library(ReactomePA))
suppressPackageStartupMessages(library(DOSE))
suppressPackageStartupMessages(library(enrichR))
suppressPackageStartupMessages(library(enrichplot))
suppressPackageStartupMessages(library(clusterProfiler))
suppressPackageStartupMessages(library(dplyr))

padj <- 0.05
log2FoldChange <- 1

data <-  read.csv(snakemake@input[[1]], row.names = 1,check.names = FALSE)

# GENE EXPRESSION STUDIES
c_up_ind <- (data$log2FoldChange > {log2FoldChange }) & (data$padj < padj)
c_up_ind[is.na(c_up_ind)] = FALSE
c_up_genes <- data$Gene_name[c_up_ind]
c_up_ensembl <- data$ensembl_gene_id[c_up_ind]

#  MOLECULAR FUNCTION

c_up_entrez <- bitr(c_up_ensembl, fromType = "ENSEMBL",
                         toType = c("ENTREZID"),
                         OrgDb = org.Hs.eg.db)

c_up_entrez <- c_up_entrez[!is.na(c_up_entrez)]



M_tab <- enrichGO(gene = c_up_ensembl,
                OrgDb = org.Hs.eg.db,
                keyType = 'ENSEMBL',
                ont = "MF",
                pAdjustMethod = "BH",
                pvalueCutoff = 0.05,
                qvalueCutoff = 0.05,
                readable = TRUE)
if(!is.null(M_tab)) {{
  M_tab_df <- data.frame(M_tab)
  M_tab_df[,c(5,6,7)] <- round(M_tab_df[,c(5,6,7)], digits=3)
  if (nrow(M_tab_df) > 0) {{
    M_tab_df$Gene_set_library <- 'Molecular Function'
    M_tab_df$Regulation <- 'Upregulated'

  }}
  write.csv(M_tab_df, file = snakemake@output[[1]], row.names = FALSE)
  }}



# cellular functions

C_tab <- enrichGO(gene = c_up_ensembl,
                 OrgDb = org.Hs.eg.db,
                 keyType = 'ENSEMBL',
                 ont = "CC",
                 pAdjustMethod = "BH",
                 pvalueCutoff = 0.05,
                 qvalueCutoff = 0.05,
                 readable = TRUE)
  if(!is.null(C_tab)) {{
    c_tab_df <- data.frame(C_tab)
    c_tab_df[,c(5,6,7)] <- round(c_tab_df[,c(5,6,7)], digits=3)
    if (nrow(c_tab_df) > 0) {{
      c_tab_df$Gene_set_library <- 'Cellular Component'
      c_tab_df$Regulation <- 'Upregulated'
    }}
    write.csv(c_tab_df, file = snakemake@output[[2]], row.names = FALSE)
  }}



# BIOLOGICAL PROCESS

b_tab <- enrichGO(gene = c_up_ensembl,
                  OrgDb = org.Hs.eg.db,
                  keyType = 'ENSEMBL',
                  ont = "BP",
                  pAdjustMethod = "BH",
                  pvalueCutoff = 0.05,
                  qvalueCutoff = 0.05,
                  readable = TRUE)
  if(!is.null(b_tab )) {{
    b_tab_df <- data.frame(b_tab)
    b_tab_df[,c(5,6,7)] <- round(b_tab_df[,c(5,6,7)], digits=3)
    if (nrow(b_tab_df) > 0) {{
      b_tab_df$Gene_set_library <- 'Biological Process'
      b_tab_df$Regulation <- 'Upregulated'
    }}
    write.csv(b_tab_df, file = snakemake@output[[3]], row.names = FALSE)
  }}


# PATHWAY ENRICHMENT

p_tab <- enrichKEGG(gene = c_up_entrez,
                   organism = 'hsa',
                   pvalueCutoff = 0.05)
  if(!is.null(p_tab)) {{
    p_tab_df <- data.frame(p_tab)
    p_tab_df[,c(5,6,7)] <- round(p_tab_df[,c(7,8,9)], digits=3)
    if (nrow(p_tab_df) > 0) {{
      p_tab_df$Gene_set_library <- 'KEGG Pathways'
      p_tab_df$Regulation <- 'Upregulated'
    }}
    write.csv(p_tab_df, file = snakemake@output[[4]], row.names = FALSE)

  }}
  

# reactome_pathway

r_tab <- enrichPathway(gene = c_up_entrez, 
                       pvalueCutoff = 0.05, 
                       readable = TRUE)
  if(!is.null(r_tab)) {{
    r_tab_df <- data.frame(r_tab)
    r_tab_df[,c(5,6,7)] <- round(r_tab_df[,c(5,6,7)], digits=3)
    if (nrow(r_tab_df) > 0) {{
      r_tab_df$Gene_set_library <- 'REACTOME Pathways'
      r_tab_df$Regulation <- 'Upregulated'
    }}
    
    write.csv(r_tab_df, file = snakemake@output[[5]], row.names = FALSE)

   
  }}


# wiki pathway

w_tab <- enrichWP(c_up_entrez, organism = "Homo sapiens")
  if(!is.null(w_tab)) {{
    w_tab_df <- data.frame(w_tab)
    w_tab_df[,c(5,6,7)] <- round(w_tab_df[,c(5,6,7)], digits=3)
    if (nrow(w_tab_df) > 0) {{
      w_tab_df$Gene_set_library <- 'WikiPathways'
      w_tab_df$Regulation <- 'Upregulated'
    }}
    write.csv(w_tab_df, file = snakemake@output[[6]], row.names = FALSE)
  }}
  

# DISEASE ENRICHMENT

d_tab <- enrichDO(gene = c_up_entrez,
                  ont = "DO",
                  pvalueCutoff = 0.05,
                  pAdjustMethod = "BH",
                  qvalueCutoff = 0.05,
                  readable = TRUE)
  if(!is.null(d_tab)) {{
    d_tab_df <- data.frame(d_tab)
    d_tab_df[,c(5,6,7)] <- round(d_tab_df[,c(5,6,7)], digits=3)
    if (nrow(d_tab_df) > 0) {{
      d_tab_df$Gene_set_library <- 'Disease Ontology'
      d_tab_df$Regulation <- 'Upregulated'
    }}
    write.csv(d_tab_df, file = snakemake@output[[7]], row.names = FALSE)
    
  }}


# # NETWORK OF CANCER GENES
# nc_tab <- enrichNCG(gene = c_up_entrez,
#                    pvalueCutoff = 0.05,
#                    pAdjustMethod = "BH",
#                    qvalueCutoff = 0.05,
#                    readable = TRUE)
#   if(!is.null(nc_tab)) {{
#     nc_tab_df <- data.frame(nc_tab)
#     nc_tab_df[,c(5,6,7)] <- round(nc_tab_df[,c(5,6,7)], digits=3)
#     if (nrow(nc_tab_df) > 0) {{
#       nc_tab_df$Gene_set_library <- 'Network of Cancer Genes'
#       nc_tab_df$Regulation <- 'Upregulated'
#     }}
#     write.csv(nc_tab_df, file = snakemake@output[[8]], row.names = FALSE)
    
#   }}


# # DISEASE GENE NETWORK

# GN_tab <- enrichDGN(gene = c_up_entrez,
#                    pvalueCutoff = 0.05,
#                    pAdjustMethod = "BH",
#                    qvalueCutoff = 0.05,
#                    readable = TRUE)
#   if(!is.null(GN_tab)) {{
#     GN_tab_df <- data.frame(GN_tab)
#     GN_tab_df[,c(5,6,7)] <- round(GN_tab_df[,c(5,6,7)], digits=3)
#     if (nrow(GN_tab_df) > 0) {{
#       GN_tab_df$Gene_set_library <- 'Disease Gene Network'
#       GN_tab_df$Regulation <- 'Upregulated'
#     }}
#     write.csv(GN_tab_df, file = snakemake@output[[9]], row.names = FALSE)
    
#   }}