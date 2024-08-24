# AutoRNASeq
Simplified RNA-Seq Insights with automation

This is a application which that automates RNA-Seq data analysis. Users can upload raw counts and metadata files to generate useful plots and insights from the data. The backend leverages R scripts and Snakemake for processing.
Installation
Follow these steps to set up and run the application:
Installation
Follow these steps to set up and run the application:

### 1. Clone the Repository
```git clone https://github.com/Moha-cm/AutoRNASeq.git`

`cd AutoRNASeq\app_file`

3. Install Python Dependencies
Make sure you have Python installed (preferably in a virtual environment). Then, install the required Python packages using requirements.txt:
`pip install -r requirements.txt`

4. Set Up Mamba and Install Snakemake
To manage Snakemake and other bioinformatics tools efficiently, you'll need Mamba, a faster alternative to Conda. You can install Mamba using Miniforge:

Install Miniforge:
Visit the Miniforge GitHub page and download the appropriate installer for your operating system.

Set Up Mamba:

Once Miniforge is installed, you can set up Mamba by running:
`conda install mamba -n base -c conda-forge`
Install Snakemake:

Now, install Snakemake using Mamba:
`mamba install -c conda-forge snakemake`

4. Running the Application
After installing all dependencies, you can start the Flask application:

`python ./app.py`

5. Usage
Upload Data: Use the UI to upload your raw counts and metadata files.
Generate Plots: The application will trigger Snakemake workflows and R scripts to process the data and generate plots based on your input.
Explore Results: Visualize the generated plots and download files directly from the interface.
