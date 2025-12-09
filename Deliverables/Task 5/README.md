# MLOps Kubeflow Assignment

## Project Overview

This project implements a complete Machine Learning Operations (MLOps) pipeline for **Iris species classification**. The pipeline demonstrates industry-standard MLOps practices including data versioning with DVC, pipeline orchestration with Kubeflow, and continuous integration with Jenkins.

### ML Problem
The project addresses a multi-class classification problem using the classic Iris dataset. The goal is to classify iris flowers into three species (setosa, versicolor, virginica) based on four features: sepal length, sepal width, petal length, and petal width.

### Key Features
- Data versioning and tracking with DVC
- Modular pipeline components using Kubeflow Pipelines
- Random Forest classifier with configurable hyperparameters
- Comprehensive model evaluation metrics
- CI/CD automation with Jenkins
- Kubernetes-based deployment using Minikube

### Technologies Used
- **Version Control**: Git, GitHub, DVC
- **ML Framework**: Scikit-learn, Pandas, NumPy
- **Orchestration**: Kubeflow Pipelines (KFP)
- **Containerization**: Docker, Kubernetes (Minikube)
- **CI/CD**: Jenkins
- **Python Version**: 3.9+

---

## Project Structure

```
mlops-kubeflow-assignment/
│
├── data/                          # Dataset directory
│   ├── iris.csv                   # Raw Iris dataset
│   └── iris.csv.dvc               # DVC tracking file
│
├── src/                           # Source code
│   ├── pipeline_components.py     # Kubeflow component definitions
│   └── __pycache__/               # Python cache files
│
├── components/                    # Compiled pipeline artifacts
│   └── pipeline.yaml              # Compiled Kubeflow pipeline
│
├── Deliverables/                  # Assignment deliverables
│   ├── Task 1/                    # Data versioning screenshots
│   ├── Task 2/                    # Component screenshots
│   ├── Task 3/                    # Kubeflow execution screenshots
│   └── Task 4/                    # Jenkins CI/CD screenshots
│
├── pipeline.py                    # Main pipeline definition
├── requirements.txt               # Python dependencies
├── Jenkinsfile                    # Jenkins CI/CD configuration
└── README.md                      # This file
```

---

## Setup Instructions

### Prerequisites
- Ubuntu/Linux environment (recommended)
- Python 3.9 or higher
- Docker installed and running
- Git installed
- Minimum 4GB RAM and 20GB disk space

### 1. Clone the Repository

```bash
git clone https://github.com/D3aThNdDeMiSe/mlops-kubeflow-assignment.git
cd mlops-kubeflow-assignment
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv kubeflowenv

# Activate virtual environment
source kubeflowenv/bin/activate  # On Linux/Mac
# kubeflowenv\Scripts\activate   # On Windows

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. DVC Remote Storage Setup

#### Option A: Local Remote Storage (Simplest for testing)
```bash
# Initialize DVC
dvc init

# Create a local remote storage directory
mkdir -p /tmp/dvc-storage

# Configure DVC remote
dvc remote add -d myremote /tmp/dvc-storage

# Pull the data from remote
dvc pull
```

#### Option B: Google Drive Remote Storage
```bash
# Initialize DVC
dvc init

# Add Google Drive remote (replace FOLDER_ID with your Google Drive folder ID)
dvc remote add -d myremote gdrive://FOLDER_ID

# Authenticate with Google Drive
dvc remote modify myremote gdrive_acknowledge_abuse true

# Pull the data
dvc pull
```

#### Option C: AWS S3 Remote Storage
```bash
# Configure AWS credentials first
aws configure

# Add S3 remote
dvc remote add -d myremote s3://your-bucket-name/dvc-storage

# Pull data
dvc pull
```

### 4. Minikube Setup

```bash
# Install Minikube (if not already installed)
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=40g

# Verify Minikube is running
minikube status

# Enable necessary addons
minikube addons enable metrics-server
minikube addons enable storage-provisioner
```

### 5. Kubeflow Pipelines Installation

```bash
# Set Kubeflow Pipelines version
export PIPELINE_VERSION=2.0.5

# Install Kubeflow Pipelines
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/cluster-scoped-resources?ref=$PIPELINE_VERSION"
kubectl wait --for condition=established --timeout=60s crd/applications.app.k8s.io
kubectl apply -k "github.com/kubeflow/pipelines/manifests/kustomize/env/platform-agnostic?ref=$PIPELINE_VERSION"

# Wait for all pods to be ready (this may take 5-10 minutes)
kubectl wait --for=condition=ready --timeout=300s pod --all -n kubeflow

# Verify installation
kubectl get pods -n kubeflow

# Port forward to access the UI
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
```

Access the Kubeflow Pipelines UI at: `http://localhost:8080`

### 6. Jenkins Setup (Optional for CI/CD)

```bash
# Install Jenkins (if not already installed)
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
sudo apt-get update
sudo apt-get install jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Get initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Access Jenkins at: `http://localhost:8080`

**Configure Jenkins:**
1. Install suggested plugins
2. Create admin user
3. Install additional plugins: Git, Pipeline, Python
4. Create a new Pipeline job
5. Point it to your GitHub repository
6. Set the script path to `Jenkinsfile`

---

## Pipeline Walkthrough

### Pipeline Components

The ML pipeline consists of four main components:

#### 1. **Data Extraction** (`data_extraction`)
- Fetches the versioned dataset from DVC remote storage
- Falls back to local Iris dataset if DVC fetch fails
- **Inputs**: `repo_url`, `data_path`
- **Outputs**: `dataset_path` (Dataset artifact)

#### 2. **Data Preprocessing** (`data_preprocessing`)
- Handles missing values
- Splits data into training and test sets (80/20 split)
- Applies StandardScaler for feature normalization
- **Inputs**: `input_data`, `test_size`, `random_state`
- **Outputs**: `train_data`, `test_data` (Dataset artifacts)

#### 3. **Model Training** (`model_training`)
- Trains a Random Forest Classifier
- Configurable hyperparameters (n_estimators, max_depth)
- Saves trained model using joblib
- **Inputs**: `train_data`, `n_estimators`, `max_depth`, `random_state`
- **Outputs**: `model_output` (Model artifact)

#### 4. **Model Evaluation** (`model_evaluation`)
- Evaluates model on test data
- Computes accuracy, precision, recall, and F1-score
- Generates detailed classification report
- **Inputs**: `model_input`, `test_data`
- **Outputs**: `metrics_output` (Metrics artifact)

### Compiling the Pipeline

```bash
# Activate virtual environment
source kubeflowenv/bin/activate

# Compile the pipeline
python pipeline.py
```

This generates `components/pipeline.yaml` which can be uploaded to Kubeflow.

### Running the Pipeline

#### Method 1: Through Kubeflow UI (Recommended)

1. Access Kubeflow Pipelines UI at `http://localhost:8080`
2. Click on **"Pipelines"** in the left sidebar
3. Click **"Upload pipeline"**
4. Upload `components/pipeline.yaml`
5. Click **"Create run"**
6. Configure parameters (optional):
   - `repo_url`: Your GitHub repository URL
   - `data_path`: Path to dataset in repository
   - `test_size`: Train/test split ratio (default: 0.2)
   - `n_estimators`: Number of trees in Random Forest (default: 100)
   - `max_depth`: Maximum tree depth (default: 10)
   - `random_state`: Random seed (default: 42)
7. Click **"Start"** to execute the pipeline

#### Method 2: Using Python SDK

```python
import kfp

# Connect to Kubeflow Pipelines
client = kfp.Client(host='http://localhost:8080')

# Upload and run pipeline
client.create_run_from_pipeline_package(
    pipeline_file='components/pipeline.yaml',
    arguments={
        'repo_url': 'https://github.com/D3aThNdDeMiSe/mlops-kubeflow-assignment.git',
        'data_path': 'data/iris.csv',
        'test_size': 0.2,
        'n_estimators': 100,
        'max_depth': 10,
        'random_state': 42
    }
)
```

### Monitoring Pipeline Execution

1. In the Kubeflow UI, click on **"Runs"** to see all pipeline executions
2. Click on a specific run to view:
   - **Graph**: Visual representation of pipeline components
   - **Run output**: Logs and outputs from each component
   - **Config**: Input parameters used
   - **Metrics**: Model performance metrics

### Expected Results

A successful pipeline run should produce:
- **Accuracy**: ~0.95-0.98 (95-98%)
- **Precision**: ~0.95-0.98
- **Recall**: ~0.95-0.98
- **F1-Score**: ~0.95-0.98

---

## CI/CD with Jenkins

The Jenkins pipeline automates three key stages:

### Stage 1: Environment Setup
- Checks out code from GitHub
- Creates Python virtual environment
- Installs dependencies from `requirements.txt`
- Verifies Python and package versions

### Stage 2: Pipeline Compilation
- Compiles the Kubeflow pipeline using `pipeline.py`
- Generates `components/pipeline.yaml`
- Verifies the output file exists and is valid

### Stage 3: Pipeline Validation
- Validates YAML structure
- Checks for required fields (pipelineInfo, components, deploymentSpec)
- Counts components and tasks
- Checks for common issues (placeholders, missing fields)

### Triggering Jenkins Build

```bash
# Manual trigger through Jenkins UI
# Or configure webhook in GitHub repository settings

# Jenkins will automatically:
# 1. Pull latest code from GitHub
# 2. Set up environment
# 3. Compile pipeline
# 4. Validate structure
# 5. Archive artifacts
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Minikube Won't Start
```bash
# Stop and delete existing cluster
minikube stop
minikube delete

# Start fresh with more resources
minikube start --cpus=4 --memory=8192 --disk-size=40g --driver=docker
```

#### 2. Kubeflow Pods Not Running
```bash
# Check pod status
kubectl get pods -n kubeflow

# Check pod logs
kubectl logs -n kubeflow <pod-name>

# Restart deployment
kubectl rollout restart deployment/ml-pipeline-ui -n kubeflow
```

#### 3. DVC Pull Fails
```bash
# Check remote configuration
dvc remote list

# Re-authenticate (for cloud storage)
dvc remote modify myremote --local auth basic
dvc remote modify myremote --local user <username>
dvc remote modify myremote --local password <password>

# Force pull
dvc pull -f
```

#### 4. Pipeline Compilation Errors
```bash
# Ensure all dependencies are installed
pip install --upgrade kfp pandas scikit-learn

# Check Python version (should be 3.9+)
python --version

# Verify component imports
python -c "from src.pipeline_components import *"
```

#### 5. Jenkins Build Fails
```bash
# Check Jenkins has Python installed
which python3

# Verify Jenkins workspace permissions
sudo chown -R jenkins:jenkins /var/lib/jenkins/workspace

# Check Jenkins logs
sudo journalctl -u jenkins -f
```

---

## Data Versioning with DVC

### Adding New Data
```bash
# Add new data file
dvc add data/new_dataset.csv

# Commit the .dvc file
git add data/new_dataset.csv.dvc data/.gitignore
git commit -m "Add new dataset"

# Push to DVC remote
dvc push

# Push to Git
git push origin main
```

### Retrieving Specific Version
```bash
# Checkout specific git commit
git checkout <commit-hash>

# Pull corresponding data version
dvc checkout
```

### Updating Dataset
```bash
# Modify the dataset
# ... make changes to data/iris.csv ...

# Update DVC tracking
dvc add data/iris.csv

# Commit changes
git add data/iris.csv.dvc
git commit -m "Update iris dataset"
dvc push
git push
```

---

## Pipeline Parameters

The pipeline accepts the following parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `repo_url` | string | `https://github.com/D3aThNdDeMiSe/mlops-kubeflow-assignment.git` | GitHub repository URL |
| `data_path` | string | `data/iris.csv` | Path to dataset in repository |
| `test_size` | float | `0.2` | Proportion of data for testing (0.0-1.0) |
| `n_estimators` | int | `100` | Number of trees in Random Forest |
| `max_depth` | int | `10` | Maximum depth of trees |
| `random_state` | int | `42` | Random seed for reproducibility |

---

## Model Performance

### Baseline Results
With default parameters, the model achieves:
- **Overall Accuracy**: 96-98%
- **Per-class Performance**:
  - Setosa: F1-score ~1.00 (perfect classification)
  - Versicolor: F1-score ~0.93-0.97
  - Virginica: F1-score ~0.93-0.97

### Hyperparameter Tuning
To improve performance, experiment with:
```python
# Deeper trees
max_depth: 15-20

# More estimators
n_estimators: 200-500

# Different train/test split
test_size: 0.15-0.25
```

---

## Contributing

This is an academic project for an MLOps assignment. However, suggestions and improvements are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

---

## License

This project is created for educational purposes as part of an MLOps course assignment.

---

## Contact

**Student**: Immad  
**Repository**: [github.com/D3aThNdDeMiSe/mlops-kubeflow-assignment](https://github.com/D3aThNdDeMiSe/mlops-kubeflow-assignment)

For questions or issues, please open an issue on GitHub.

---

## Acknowledgments

- **Kubeflow Community** for the excellent pipeline orchestration framework
- **DVC Team** for data versioning capabilities
- **Scikit-learn** for machine learning tools
- **Course Instructors** for guidance on MLOps best practices

---

## References

- [Kubeflow Pipelines Documentation](https://www.kubeflow.org/docs/components/pipelines/)
- [DVC Documentation](https://dvc.org/doc)
- [Scikit-learn Documentation](https://scikit-learn.org/stable/)
- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
