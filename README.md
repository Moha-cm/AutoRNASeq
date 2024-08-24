# AutoRNASeq
## Simplified RNA-Seq Insights with Automation

AutoRNASeq is an application that automates RNA-Seq data analysis. Users can upload raw counts and metadata files to generate insightful plots and analyze their data. The backend leverages R scripts and Snakemake for processing.

Installation
Follow these steps to set up and run the application:

### 1. Clone the Repository
`git clone https://github.com/Moha-cm/AutoRNASeq.git`

`cd AutoRNASeq/app_file`

### 2. Install Python Dependencies
Ensure you have Python installed (preferably in a virtual environment). Then, install the required Python packages using the requirements.txt file:

`pip install -r requirements.txt`

### 3. Set Up Mamba and Install Snakemake
To efficiently manage Snakemake and other bioinformatics tools, you'll need Mamba, a faster alternative to Conda. You can install Mamba using Miniforge:

Install Miniforge:
Visit the Miniforge GitHub page and download the appropriate installer for your operating system.

Set Up Mamba:
Once Miniforge is installed, set up Mamba by running the following command:

`conda install mamba -n base -c conda-forge`

Install Snakemake:
Now, install Snakemake using Mamba:

`mamba install -c conda-forge snakemake`

### 4. Running the Application
After installing all dependencies, you can start the Flask application by running:

`python ./app.py`

### 5. Usage

Upload Data: Use the UI to upload your raw counts and metadata files with the samples columns like files in  the sample data folder.
Generate Plots: The application will trigger Snakemake workflows and R scripts to process the data and generate plots based on your input.
Explore Results: Visualize the generated plots and download files directly from the interface.
