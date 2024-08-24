

vsd_matrix <- as.data.frame(cbind(assay(vsd)[, colnames(upper_limit)],assay(vsd)[, colnames(lower_limit)]))
vsd_matrix <- merge(vsd_matrix,gene_name,by=0,all.x=TRUE)
vsd_matrix$Gene_name[is.na(vsd_matrix$Gene_name)] <- 'unknown'
row.names(vsd_matrix) <- make.unique(vsd_matrix$Gene_name)
vsd_matrix <- subset(vsd_matrix, select=-c(ensembl_gene_id, Gene_name,ensembl_gene_id_version))
vsd_matrix <- vsd_matrix[,-c(1)]
topVarGenes <- order(rowVars(as.matrix(vsd_matrix), na.rm = TRUE), decreasing = TRUE)[1:20]
