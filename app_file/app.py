import os
import subprocess
from flask import Flask, request, render_template, redirect, url_for,send_file,send_from_directory
import pandas as pd
from PIL import Image
import plotly
import json
import plotly.express as px
import plotly.utils
import io


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store file information
uploaded_files = []

# Index page
@app.route('/')
def upload_form():
    return render_template('index.html', files_uploaded=len(uploaded_files) > 0)

# Upload endpoint
@app.route('/upload', methods=['POST'])
def upload_files():
    rawcounts_file = request.files['rawcounts']
    metafile = request.files['metafile']

    # Save uploaded files if needed
    # Example: save to 'uploads/' folder
    rawcounts_file.save(os.path.join(app.config['UPLOAD_FOLDER'], rawcounts_file.filename))
    metafile.save(os.path.join(app.config['UPLOAD_FOLDER'], metafile.filename))

    # Update uploaded_files list (can store filenames, etc.)
    uploaded_files.append((rawcounts_file.filename, metafile.filename))

    # Redirect to a new route where upload box is hidden
    return redirect(url_for('input_response'))


# Route to input_response after upload
@app.route('/input_response')
def input_response():
    global uploaded_files
    if not uploaded_files:
        return redirect(url_for('/upload_form'))
    else:
        
        def get_recent_files():
            if not uploaded_files:
                return None, None
            file_info = uploaded_files[-1]
            raw_counts_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[0])
            meta_data_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[1])
            return raw_counts_path, meta_data_path

        def read_data_files(raw_counts_path, meta_data_path):
            raw_counts_df = pd.read_csv(raw_counts_path)
            meta_data_df = pd.read_csv(meta_data_path)
            raw_counts_df.rename(columns={raw_counts_df.columns[0]: "barcodes"}, inplace=True)
            raw_counts_df = raw_counts_df.transpose()
            raw_counts_df = raw_counts_df.reset_index()
            raw_counts_df.columns = raw_counts_df.iloc[0]
            raw_counts_df = raw_counts_df.iloc[1:]
            common_columns = [col for col in meta_data_df.columns if col in raw_counts_df.columns]
            return raw_counts_df, meta_data_df, common_columns

        raw_counts_path, meta_data_path = get_recent_files()
        if not raw_counts_path or not meta_data_path:
            return redirect(url_for('/upload'))
        
        raw_counts_df, meta_data_df, common_columns = read_data_files(raw_counts_path, meta_data_path)

        raw_counts_data = raw_counts_df.to_dict(orient='records')
        meta_data_data = meta_data_df.to_dict(orient='records')
        colnames_meta = list(meta_data_df.select_dtypes(exclude='number').columns)
        raw_counts_column = list(raw_counts_df.select_dtypes(exclude='number').columns)

        return render_template('input_response.html', raw_counts=raw_counts_data, meta_data=meta_data_data)



@app.route('/scatter_plot', methods=["GET", "POST"])
def scatter_plot():
    global uploaded_files

    def get_recent_files():
        if not uploaded_files:
            return None, None
        file_info = uploaded_files[-1]
        raw_counts_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[0])
        meta_data_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[1])
        return raw_counts_path, meta_data_path

    def read_data_files(raw_counts_path, meta_data_path):
        raw_counts_df = pd.read_csv(raw_counts_path)
        meta_data_df = pd.read_csv(meta_data_path)
        raw_counts_df.rename(columns={raw_counts_df.columns[0]: "barcodes"}, inplace=True)
        raw_counts_df = raw_counts_df.transpose()
        raw_counts_df = raw_counts_df.reset_index()
        raw_counts_df.columns = raw_counts_df.iloc[0]
        raw_counts_df = raw_counts_df.iloc[1:]
        common_columns = [col for col in meta_data_df.columns if col in raw_counts_df.columns]
        return raw_counts_df, meta_data_df, common_columns

    raw_counts_path, meta_data_path = get_recent_files()
    if not raw_counts_path or not meta_data_path:
        return redirect(url_for('upload_form'))

    raw_counts_df, meta_data_df, common_columns = read_data_files(raw_counts_path, meta_data_path)
    colnames_meta = list(meta_data_df.select_dtypes(exclude='number').columns)
    raw_counts_column = list(raw_counts_df.select_dtypes(exclude='number').columns)
    
    
    if request.method == "POST":
        plot_x_axis = request.form.get('plot_x_axis')
        color_options = request.form.get('color_options')
        gene_name = request.form.get('gene')

        if not plot_x_axis or not color_options or not gene_name:
            return "All form fields are required.", 400

        gene_ids = pd.read_csv("ensembl_gene_ids.csv")
        filter_gene = gene_ids[gene_ids["Gene_name"] == gene_name]

        if filter_gene.empty:
            return "Gene not found.", 400
        
        filter_ensemble_version_id = filter_gene["ensembl_gene_id_version"].iloc[0]
        
        subset_columns = [plot_x_axis,filter_ensemble_version_id, color_options]

        dataset = pd.merge(meta_data_df, raw_counts_df, left_on=common_columns, right_on=common_columns)
        filter_dataset = dataset[subset_columns]
        filter_dataset.rename(columns={filter_ensemble_version_id: filter_gene["Gene_name"].iloc[0]}, inplace=True)
        filter_dataset[filter_gene["Gene_name"].iloc[0]] = filter_dataset[filter_gene["Gene_name"].iloc[0]].astype(str).astype(int) 
        filtered_gene = filter_gene["Gene_name"].iloc[0]
        
        fig = px.scatter(
            filter_dataset, 
            x=plot_x_axis, 
            y=filter_gene["Gene_name"].iloc[0],
            color=color_options,
            size=filter_gene["Gene_name"].iloc[0]
        )
        fig.update_layout(
            plot_bgcolor='white',
            title={
                'text': f"<b>{filtered_gene} Expression by {color_options.replace("_"," ").capitalize()}</b>",
                'x': 0.5,  # Center the title
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    'color': 'black'  # Change the font color to black
                }
            },
            xaxis={
                'showticklabels': False,  # Hide x-axis labels
                'showline': True,  # Show x-axis line
                'linecolor': 'black'  # Set x-axis border color to black
            },
            yaxis={
                'showticklabels': True,  # Show y-axis labels
                'showline': True,  # Show y-axis line
                'linecolor': 'black'  # Set y-axis border color to black
            })
        

       
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('scatter_plot.html', raw_counts=filter_dataset.to_dict(orient='records'), col_option=colnames_meta, exp_option= common_columns, files_uploaded=True, graphJSON=graphJSON)

    return render_template('scatter_plot.html', col_option=colnames_meta, exp_option= common_columns, files_uploaded=False)





@app.route('/box_plot', methods=["GET", "POST"])
def box_plot():
    global uploaded_files

    def get_recent_files():
        if not uploaded_files:
            return None, None
        file_info = uploaded_files[-1]
        raw_counts_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[0])
        meta_data_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[1])
        return raw_counts_path, meta_data_path

    def read_data_files(raw_counts_path, meta_data_path):
        raw_counts_df = pd.read_csv(raw_counts_path)
        meta_data_df = pd.read_csv(meta_data_path)
        raw_counts_df.rename(columns={raw_counts_df.columns[0]: "barcodes"}, inplace=True)
        raw_counts_df = raw_counts_df.transpose()
        raw_counts_df = raw_counts_df.reset_index()
        raw_counts_df.columns = raw_counts_df.iloc[0]
        raw_counts_df = raw_counts_df.iloc[1:]
        common_columns = [col for col in meta_data_df.columns if col in raw_counts_df.columns]
        return raw_counts_df, meta_data_df, common_columns

    raw_counts_path, meta_data_path = get_recent_files()
    if not raw_counts_path or not meta_data_path:
        return redirect(url_for('upload_form'))

    raw_counts_df, meta_data_df, common_columns = read_data_files(raw_counts_path, meta_data_path)
    colnames_meta = list(meta_data_df.select_dtypes(exclude='number').columns)
    raw_counts_column = list(raw_counts_df.select_dtypes(exclude='number').columns)

    if request.method == "POST":
        plot_x_axis = request.form.get('plot_x_axis')
        color_options = request.form.get('color_options')
        gene_name = request.form.get('gene')

        if not plot_x_axis or not color_options or not gene_name:
            return "All form fields are required.", 400

        gene_ids = pd.read_csv("ensembl_gene_ids.csv")
        filter_gene = gene_ids[gene_ids["Gene_name"] == gene_name]

        if filter_gene.empty:
            return "Gene not found.", 400
        
        filter_ensemble_version_id = filter_gene["ensembl_gene_id_version"].iloc[0]
        
        subset_columns = [plot_x_axis,filter_ensemble_version_id, color_options]

        dataset = pd.merge(meta_data_df, raw_counts_df, left_on=common_columns, right_on=common_columns)
        filter_dataset = dataset[subset_columns]
        filter_dataset.rename(columns={filter_ensemble_version_id: filter_gene["Gene_name"].iloc[0]}, inplace=True)
        filtered_gene = filter_gene["Gene_name"].iloc[0]
        fig = px.box(
            filter_dataset, 
            x=plot_x_axis, 
            y=filter_gene["Gene_name"].iloc[0],
            color=color_options )
        
        fig.update_layout(
            plot_bgcolor='white',
            title={
                'text': f"<b>{filtered_gene} Expression by {color_options.replace("_"," ").capitalize()}</b>",  # Make title bold
                'x': 0.5,  # Center the title
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {
                    'color': 'black'  # Change the font color to black
                }
            },
            xaxis={
                'showticklabels': False,  # Hide x-axis labels
                'showline': True,  # Show x-axis line
                'linecolor': 'black'  # Set x-axis border color to black
            },
            yaxis={
                'showticklabels': True,  # Show y-axis labels
                'showline': True,  # Show y-axis line
                'linecolor': 'black'  # Set y-axis border color to black
            })
       
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        return render_template('box_plot.html', raw_counts=filter_dataset.to_dict(orient='records'), col_option=colnames_meta, exp_option=raw_counts_column, files_uploaded=True, graphJSON=graphJSON)

    return render_template('box_plot.html', col_option=colnames_meta, files_uploaded=False)



@app.route('/volcano_plot', methods=["GET", "POST"])
def volcano_plot():
    global uploaded_files

    def get_recent_files():
        if not uploaded_files:
            return None, None
        file_info = uploaded_files[-1]
        raw_counts_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[0])
        meta_data_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[1])
        return raw_counts_path, meta_data_path

    def read_data_files(raw_counts_path, meta_data_path):
        raw_counts_df = pd.read_csv(raw_counts_path)
        meta_data_df = pd.read_csv(meta_data_path)
        raw_counts_df.rename(columns={raw_counts_df.columns[0]: "barcodes"}, inplace=True)
        raw_counts_df = raw_counts_df.transpose().reset_index()
        raw_counts_df.columns = raw_counts_df.iloc[0]
        raw_counts_df = raw_counts_df.iloc[1:]
        common_columns = [col for col in meta_data_df.columns if col in raw_counts_df.columns]
        return raw_counts_df, meta_data_df, common_columns

    raw_counts_path, meta_data_path = get_recent_files()
    if not raw_counts_path or not meta_data_path:
        return redirect(url_for('upload_form'))

    raw_counts_df, meta_data_df, common_columns = read_data_files(raw_counts_path, meta_data_path)
    colnames_meta = list(meta_data_df.select_dtypes(exclude='number').columns)
    
    if request.method == "POST":
        color_options = request.form.get('color_options')
        if not color_options:
            return "All form fields are required.", 400
        
        subset_columns = ["barcodes", color_options]
        condition_df = meta_data_df[subset_columns]
        condition_df.rename(columns={condition_df.columns[1]: "Condition"}, inplace=True)
        condition_df_path = os.path.join(app.config['UPLOAD_FOLDER'], 'condition_df.csv')
        condition_df.to_csv(condition_df_path, index=False)
        
         
        with open('config.yaml', 'w') as config_file:
            config_file.write(f"raw_counts: '{raw_counts_path}'\n")
            config_file.write(f"meta_data: '{condition_df_path}'\n")
            
        try:
            subprocess.run(['snakemake', '-s', 'volcano_plot.smk', '--cores', '1', '--use-conda'], check=True)
        except subprocess.CalledProcessError as e:
            return f"Error running Snakemake: {e}", 500
            
        app.config['STATIC_FOLDER'] = 'static/images'
        app.config['SNAKEMAKE_OUTPUTS']='snake_make_reports/'
        vol_image_path = os.path.join(app.config['STATIC_FOLDER'], 'vol.png')
        deseq_result_file =  os.path.join(app.config['SNAKEMAKE_OUTPUTS'], 'deseq_results.csv')
        if os.path.exists(vol_image_path):
            os.remove(vol_image_path)
        
        if os.path.exists(deseq_result_file):
            os.remove(deseq_result_file)
        os.rename('reports/vol.png', vol_image_path)
        os.rename('reports/deseq_results.csv', deseq_result_file)
        
        
        deseq_df = pd.read_csv("snake_make_reports/deseq_results.csv")
        deseq_df.rename(columns={deseq_df.columns[0]: "Ensemble_version_id"}, inplace=True)
        
        return render_template('volcano_plot.html', col_option=colnames_meta, files_uploaded=True, condition_data=condition_df.to_dict(orient='records'), Deseq_df=deseq_df.to_dict(orient='records'))
        
    return render_template('volcano_plot.html', col_option=colnames_meta, files_uploaded=False)






@app.route('/upregulaetd_genes', methods=["GET", "POST"])
def upregulaetd_genes():
    global uploaded_files

    def get_recent_files():
        if not uploaded_files:
            return None, None
        file_info = uploaded_files[-1]
        raw_counts_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[0])
        meta_data_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[1])
        return raw_counts_path, meta_data_path

    def read_data_files(raw_counts_path, meta_data_path):
        raw_counts_df = pd.read_csv(raw_counts_path)
        meta_data_df = pd.read_csv(meta_data_path)
        raw_counts_df.rename(columns={raw_counts_df.columns[0]: "barcodes"}, inplace=True)
        raw_counts_df = raw_counts_df.transpose().reset_index()
        raw_counts_df.columns = raw_counts_df.iloc[0]
        raw_counts_df = raw_counts_df.iloc[1:]
        common_columns = [col for col in meta_data_df.columns if col in raw_counts_df.columns]
        return raw_counts_df, meta_data_df, common_columns

    raw_counts_path, meta_data_path = get_recent_files()
    if not raw_counts_path or not meta_data_path:
        return redirect(url_for('upload_form'))

    raw_counts_df, meta_data_df, common_columns = read_data_files(raw_counts_path, meta_data_path)
    colnames_meta = list(meta_data_df.select_dtypes(exclude='number').columns)
    
    if request.method == "POST":
        color_options = request.form.get('color_options')
        if not color_options:
            return "All form fields are required.", 400
        
        subset_columns = ["barcodes", color_options]
        condition_df = meta_data_df[subset_columns]
        condition_df.rename(columns={condition_df.columns[1]: "Condition"}, inplace=True)
        condition_df_path = os.path.join(app.config['UPLOAD_FOLDER'], 'condition_df.csv')
        condition_df.to_csv(condition_df_path, index=False)
        
        with open('config.yaml', 'w') as config_file:
            config_file.write(f"raw_counts: '{raw_counts_path}'\n")
            config_file.write(f"meta_data: '{condition_df_path}'\n")
            
        try:
            subprocess.run(['snakemake', '-s', 'upregulated_genes.smk', '--cores', '1', '--use-conda'], check=True)
        except subprocess.CalledProcessError as e:
            return f"Error running Snakemake: {e}", 500
            
        app.config['SNAKEMAKE_OUTPUTS'] = 'snake_make_reports/'
        output_files = {
            'deseq_result_file': 'deseq_results.csv',
            'upregulated_genes':'up_regulated_genes.csv',
            'molecular_file': 'upregulated_genes_Molecular_function.csv',
            'cellular_file': 'upregulated_genes_cellular_function.csv',
            'biological_file': 'upregulated_genes_biological_function.csv',
            'pathway_file': 'upregulated_genes_pathway_enrichment.csv',
            'reactome_file': 'upregulated_genes_reactome_pathway.csv',
            'wikipathway_file': 'upregulated_genes_wiki_pathway.csv',
            'disease_file': 'upregulated_genes_disease_pathway.csv'
            # 'cancer_genes_file': 'upregulated_cancer_genes.csv',
            # 'gene_network_file': 'upregulated_gene_network.csv'
        }

        for key, filename in output_files.items():
            output_path = os.path.join(app.config['SNAKEMAKE_OUTPUTS'], filename)
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(f'reports/{filename}', output_path)
        
        deseq_df = pd.read_csv('snake_make_reports/deseq_results.csv')
        up_regulated_genes = pd.read_csv('snake_make_reports/up_regulated_genes.csv')
        molecular_df = pd.read_csv('snake_make_reports/upregulated_genes_Molecular_function.csv')
        cellular_df = pd.read_csv('snake_make_reports/upregulated_genes_cellular_function.csv')
        biological_df = pd.read_csv("snake_make_reports/upregulated_genes_biological_function.csv")
        pathway_df = pd.read_csv('snake_make_reports/upregulated_genes_pathway_enrichment.csv')
        reactome_df = pd.read_csv('snake_make_reports/upregulated_genes_reactome_pathway.csv')
        wikipathway_df = pd.read_csv('snake_make_reports/upregulated_genes_wiki_pathway.csv')
        disease_df = pd.read_csv('snake_make_reports/upregulated_genes_disease_pathway.csv')
        # cancer_genes_df = pd.read_csv('snake_make_reports/upregulated_cancer_genes.csv')
        # gene_network_df = pd.read_csv('snake_make_reports/upregulated_gene_network.csv')
        deseq_df.rename(columns={deseq_df.columns[0]: "Ensemble_version_id"}, inplace=True)
        up_regulated_genes.rename(columns={ up_regulated_genes.columns[0]: "Ensemble_version_id"}, inplace=True)
        
        return render_template('upregulated_genes.html', col_option=colnames_meta, files_uploaded=True, condition_data=condition_df.to_dict(orient='records'), 
                                Deseq_df=deseq_df.to_dict(orient='records'),
                                up_genes_df =  up_regulated_genes.to_dict(orient='records'),
                                molecular_df=molecular_df.to_dict(orient='records'),
                                cellular_df=cellular_df.to_dict(orient='records'),
                                biological_df=biological_df.to_dict(orient='records'),
                                pathway_df=pathway_df.to_dict(orient='records'),
                                reactome_df=reactome_df.to_dict(orient='records'),
                                wikipathway_df=wikipathway_df.to_dict(orient='records'),
                                disease_df=disease_df.to_dict(orient='records')
                                # cancer_genes_df=cancer_genes_df.to_dict(orient='records'),
                                # gene_network_df=gene_network_df.to_dict(orient='records')
                               )
        
    return render_template('upregulated_genes.html', col_option=colnames_meta, files_uploaded=True)


    


@app.route('/downregulaetd_genes', methods=["GET", "POST"])
def downregulaetd_genes():
    global uploaded_files

    def get_recent_files():
        if not uploaded_files:
            return None, None
        file_info = uploaded_files[-1]
        raw_counts_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[0])
        meta_data_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[1])
        return raw_counts_path, meta_data_path

    def read_data_files(raw_counts_path, meta_data_path):
        raw_counts_df = pd.read_csv(raw_counts_path)
        meta_data_df = pd.read_csv(meta_data_path)
        raw_counts_df.rename(columns={raw_counts_df.columns[0]: "barcodes"}, inplace=True)
        raw_counts_df = raw_counts_df.transpose().reset_index()
        raw_counts_df.columns = raw_counts_df.iloc[0]
        raw_counts_df = raw_counts_df.iloc[1:]
        common_columns = [col for col in meta_data_df.columns if col in raw_counts_df.columns]
        return raw_counts_df, meta_data_df, common_columns

    raw_counts_path, meta_data_path = get_recent_files()
    if not raw_counts_path or not meta_data_path:
        return redirect(url_for('upload_form'))

    raw_counts_df, meta_data_df, common_columns = read_data_files(raw_counts_path, meta_data_path)
    colnames_meta = list(meta_data_df.select_dtypes(exclude='number').columns)
    
    if request.method == "POST":
        color_options = request.form.get('color_options')
        if not color_options:
            return "All form fields are required.", 400
        
        subset_columns = ["barcodes", color_options]
        condition_df = meta_data_df[subset_columns]
        condition_df.rename(columns={condition_df.columns[1]: "Condition"}, inplace=True)
        condition_df_path = os.path.join(app.config['UPLOAD_FOLDER'], 'condition_df.csv')
        condition_df.to_csv(condition_df_path, index=False)
        
        with open('config.yaml', 'w') as config_file:
            config_file.write(f"raw_counts: '{raw_counts_path}'\n")
            config_file.write(f"meta_data: '{condition_df_path}'\n")
            
        try:
            subprocess.run(['snakemake', '-s', 'downregulated_genes.smk', '--cores', '1', '--use-conda'], check=True)
        except subprocess.CalledProcessError as e:
            return f"Error running Snakemake: {e}", 500
            
        app.config['SNAKEMAKE_OUTPUTS'] = 'snake_make_reports/'
        output_files = {
            'deseq_result_file': 'deseq_results.csv',
            'downregulated_genes':'down_regulated_genes.csv',
            'molecular_file': 'downregulated_genes_Molecular_function.csv',
            'cellular_file': 'downregulated_genes_cellular_function.csv',
            'biological_file': 'downregulated_genes_biological_function.csv',
            'pathway_file': 'downregulated_genes_pathway_enrichment.csv',
            'reactome_file': 'downregulated_genes_reactome_pathway.csv',
            'wikipathway_file': 'downregulated_genes_wiki_pathway.csv',
            'disease_file': 'downregulated_genes_disease_pathway.csv'
            # 'cancer_genes_file': 'downregulated_cancer_genes.csv',
            # 'gene_network_file': 'downregulated_gene_network.csv'
        }

        for key, filename in output_files.items():
            output_path = os.path.join(app.config['SNAKEMAKE_OUTPUTS'], filename)
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(f'reports/{filename}', output_path)
        
        deseq_df = pd.read_csv('snake_make_reports/deseq_results.csv')
        down_regulated_genes = pd.read_csv('snake_make_reports/down_regulated_genes.csv')
        molecular_df = pd.read_csv('snake_make_reports/downregulated_genes_Molecular_function.csv')
        cellular_df = pd.read_csv('snake_make_reports/downregulated_genes_cellular_function.csv')
        biological_df = pd.read_csv("snake_make_reports/downregulated_genes_biological_function.csv")
        pathway_df = pd.read_csv('snake_make_reports/downregulated_genes_pathway_enrichment.csv')
        reactome_df = pd.read_csv('snake_make_reports/downregulated_genes_reactome_pathway.csv')
        wikipathway_df = pd.read_csv('snake_make_reports/downregulated_genes_wiki_pathway.csv')
        disease_df = pd.read_csv('snake_make_reports/downregulated_genes_disease_pathway.csv')
        # cancer_genes_df = pd.read_csv('snake_make_reports/downregulated_cancer_genes.csv')
        # gene_network_df = pd.read_csv('snake_make_reports/downregulated_gene_network.csv')
        deseq_df.rename(columns={deseq_df.columns[0]: "Ensemble_version_id"}, inplace=True)
        down_regulated_genes.rename(columns={down_regulated_genes.columns[0]: "Ensemble_version_id"}, inplace=True)
        
        return render_template('downregulaetd_genes.html', col_option=colnames_meta, files_uploaded=True, condition_data=condition_df.to_dict(orient='records'), 
                                Deseq_df=deseq_df.to_dict(orient='records'),
                                down_genes_df =  down_regulated_genes.to_dict(orient='records'),
                                molecular_df=molecular_df.to_dict(orient='records'),
                                cellular_df=cellular_df.to_dict(orient='records'),
                                biological_df=biological_df.to_dict(orient='records'),
                                pathway_df=pathway_df.to_dict(orient='records'),
                                reactome_df=reactome_df.to_dict(orient='records'),
                                wikipathway_df=wikipathway_df.to_dict(orient='records'),
                                disease_df=disease_df.to_dict(orient='records')
                                # cancer_genes_df=cancer_genes_df.to_dict(orient='records'),
                                # gene_network_df=gene_network_df.to_dict(orient='records')
                               )

    return render_template('downregulaetd_genes.html', col_option=colnames_meta, files_uploaded=True)



@app.route('/survival_plot', methods=["GET", "POST"])
def survival_plot():
    global uploaded_files

    def get_recent_files():
        if not uploaded_files:
            return None, None
        file_info = uploaded_files[-1]
        raw_counts_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[0])
        meta_data_path = os.path.join(app.config['UPLOAD_FOLDER'], file_info[1])
        return raw_counts_path, meta_data_path

    def read_data_files(raw_counts_path, meta_data_path):
        raw_counts_df = pd.read_csv(raw_counts_path)
        meta_data_df = pd.read_csv(meta_data_path)
        raw_counts_df.rename(columns={raw_counts_df.columns[0]: "barcodes"}, inplace=True)
        raw_counts_df = raw_counts_df.transpose().reset_index()
        raw_counts_df.columns = raw_counts_df.iloc[0]
        raw_counts_df = raw_counts_df.iloc[1:]
        common_columns = [col for col in meta_data_df.columns if col in raw_counts_df.columns]
        return raw_counts_df, meta_data_df, common_columns

    raw_counts_path, meta_data_path = get_recent_files()
    if not raw_counts_path or not meta_data_path:
        return redirect(url_for('upload_form'))

    raw_counts_df, meta_data_df, common_columns = read_data_files(raw_counts_path, meta_data_path)

    if request.method == "POST":
        gene_name = request.form.get('gene')
        threshold_value = request.form.get('Threshold-Value')

        if not threshold_value or not gene_name:
            return "All form fields are required.", 400

        gene_ids = pd.read_csv("ensembl_gene_ids.csv")
        filter_gene = gene_ids[gene_ids["Gene_name"] == gene_name]

        if filter_gene.empty:
            return "Gene not found.", 400

        filter_ensemble_version_id = filter_gene["ensembl_gene_id_version"].iloc[0]

        required_columns = ["barcodes", "vital_status", "days_to_last_follow_up", "days_to_death"]

        def normalize_column_name(col):
            return col.replace("_", "").replace(" ", "").lower()

        normalized_required_columns = [normalize_column_name(col) for col in required_columns]
        present_columns = [col for col in meta_data_df.columns if normalize_column_name(col) in normalized_required_columns]

        if not present_columns:
            return "Insufficient meta data for survival analysis", 402

        dataset = pd.merge(meta_data_df, raw_counts_df, left_on=common_columns, right_on=common_columns)
        # print(filter_dataset)
        filter_dataset = dataset[[*present_columns , filter_ensemble_version_id]]
        filter_dataset.rename(columns={filter_ensemble_version_id: gene_name}, inplace=True)
        filter_dataset[gene_name] = filter_dataset[gene_name].astype(float)
        
        survival_df_path = os.path.join(app.config['UPLOAD_FOLDER'], 'survival_df.csv')
        filter_dataset.to_csv(survival_df_path, index=False)
        
        with open('config.yaml', 'w') as config_file:
            config_file.write(f"survival_df: '{survival_df_path}'\n")
            config_file.write(f"thresh_hold: '{threshold_value}'\n")
            config_file.write(f"Gene: '{gene_name}'\n")
            
        
            
        try:
            subprocess.run(['snakemake', '-s', 'survival_Analysis.smk', '--cores', '1', '--use-conda'], check=True)
        except subprocess.CalledProcessError as e:
            return f"Error running Snakemake: {e}", 500
        
        
        app.config['STATIC_FOLDER'] = 'static/images'
        app.config['SNAKEMAKE_OUTPUTS']='snake_make_reports/'
        survival_image_path = os.path.join(app.config['STATIC_FOLDER'], 'survival_plot.png')
        survival_result_file =  os.path.join(app.config['SNAKEMAKE_OUTPUTS'], 'survival_data.csv')
        if os.path.exists(survival_image_path):
            os.remove(survival_image_path)
        
        if os.path.exists(survival_result_file):
            os.remove(survival_result_file)
        os.rename('reports/survival_plot.png', survival_image_path)
        os.rename('reports/survival_data.csv', survival_result_file)
        
        
        survival_df = pd.read_csv("snake_make_reports/survival_data.csv")
        

        

        return render_template('survival_plot.html', survival_df=survival_df.to_dict(orient='records'), files_uploaded=True)

    return render_template('survival_plot.html', files_uploaded=False)

    

        

if __name__ == '__main__':
    app.run(debug=True)
