pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3'
        PIPELINE_FILE = 'components/pipeline.yaml'
    }
    
    options {
        // Keep only last 10 builds to save space
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // Timeout if pipeline takes more than 30 minutes
        timeout(time: 30, unit: 'MINUTES')
        // Timestamps in console output
        timestamps()
    }
    
    stages {
        stage('Environment Setup') {
            steps {
                echo '================================================'
                echo 'Stage 1: Environment Setup'
                echo '================================================'
                
                // Display build information
                script {
                    echo "Build #${env.BUILD_NUMBER}"
                    echo "Branch: ${env.GIT_BRANCH}"
                    echo "Commit: ${env.GIT_COMMIT}"
                }
                
                // Checkout code from GitHub
                checkout scm
                
                // Create virtual environment and install dependencies
                sh '''
                    echo "Setting up Python virtual environment..."
                    
                    # Remove old venv if exists
                    rm -rf venv
                    
                    # Try to create virtual environment
                    echo "Creating virtual environment..."
                    if python3 -m venv venv 2>/dev/null; then
                        echo "✅ Virtual environment created successfully"
                    else
                        echo "⚠️ Standard venv creation failed, trying with --without-pip..."
                        
                        # Try creating venv without pip
                        if python3 -m venv venv --without-pip 2>/dev/null; then
                            echo "✅ Virtual environment created without pip"
                            
                            # Activate venv
                            . venv/bin/activate
                            
                            # Install pip manually
                            echo "Installing pip manually..."
                            curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
                            python get-pip.py --quiet
                            rm get-pip.py
                            echo "✅ Pip installed manually"
                        else
                            echo "❌ Failed to create virtual environment"
                            echo "Trying alternative method with virtualenv..."
                            
                            # Try using virtualenv
                            if command -v virtualenv &> /dev/null || pip install virtualenv --quiet; then
                                virtualenv -p python3 venv
                                echo "✅ Virtual environment created with virtualenv"
                            else
                                echo "❌ All virtual environment creation methods failed"
                                exit 1
                            fi
                        fi
                    fi
                    
                    # Activate virtual environment
                    . venv/bin/activate
                    
                    echo "Python version in virtual environment:"
                    python --version
                    
                    echo "Upgrading pip and installing build tools..."
                    pip install --upgrade pip setuptools wheel --quiet
                    
                    echo "Installing project dependencies..."
                    if [ -f "requirements.txt" ]; then
                        echo "Found requirements.txt, installing packages..."
                        pip install -r requirements.txt --quiet
                        echo "✅ Dependencies installed from requirements.txt"
                    else
                        echo "⚠️ requirements.txt not found, installing core packages..."
                        # Install core packages if no requirements.txt
                        pip install kfp pandas scikit-learn numpy dvc pygit2 joblib --quiet
                        echo "✅ Core packages installed"
                    fi
                    
                    echo "✅ Virtual environment setup complete!"
                '''
                
                // Display environment info
                sh '''
                    . venv/bin/activate
                    echo ""
                    echo "Environment Information:"
                    echo "========================"
                    echo "Python version:"
                    python --version
                    echo ""
                    echo "Pip version:"
                    pip --version
                    echo ""
                    echo "Virtual environment location:"
                    which python
                    echo ""
                    echo "Installed packages:"
                    echo "-------------------"
                    pip list | grep -E "Package|kfp|dvc|scikit|pandas|numpy|joblib|pygit" | head -20
                '''
            }
        }
        
        stage('Pipeline Compilation') {
            steps {
                echo '================================================'
                echo 'Stage 2: Pipeline Compilation'
                echo '================================================'
                
                // Compile the Kubeflow pipeline using venv
                sh '''
                    # Activate virtual environment
                    . venv/bin/activate
                    
                    echo "📦 Compiling Kubeflow pipeline..."
                    
                    # Check if pipeline.py exists
                    if [ ! -f "pipeline.py" ]; then
                        echo "❌ pipeline.py not found!"
                        echo "Looking for Python files..."
                        find . -name "*.py" -type f | head -10
                        exit 1
                    fi
                    
                    # Create components directory if it doesn't exist
                    mkdir -p components
                    
                    # Run the pipeline compilation
                    python pipeline.py 2>&1
                    
                    # Check the exit status
                    if [ $? -eq 0 ]; then
                        echo "✅ Pipeline compilation completed"
                    else
                        echo "❌ Pipeline compilation failed!"
                        exit 1
                    fi
                    
                    # Verify the pipeline YAML was created
                    if [ -f "${PIPELINE_FILE}" ]; then
                        echo "✅ Pipeline YAML file created successfully!"
                        echo "📄 Pipeline YAML file: ${PIPELINE_FILE}"
                        echo "📏 File size: $(du -h ${PIPELINE_FILE} | cut -f1)"
                        ls -lh ${PIPELINE_FILE}
                    else
                        echo "❌ Pipeline YAML file not found at ${PIPELINE_FILE}"
                        echo "Looking for YAML files..."
                        find . -name "*.yaml" -o -name "*.yml" | head -10
                        exit 1
                    fi
                '''
            }
        }
        
        stage('Pipeline Validation') {
            steps {
                echo '================================================'
                echo 'Stage 3: Pipeline Validation'
                echo '================================================'
                
                // Validate pipeline YAML structure using venv
                sh '''
                    # Activate virtual environment
                    . venv/bin/activate
                    
                    echo "🔍 Validating pipeline YAML structure..."
                    
                    # Check if file exists
                    if [ ! -f "${PIPELINE_FILE}" ]; then
                        echo "❌ Pipeline file not found: ${PIPELINE_FILE}"
                        exit 1
                    fi
                    
                    # Validate YAML structure
                    python << 'EOF'
import yaml
import sys
import os

try:
    pipeline_file = os.environ.get('PIPELINE_FILE', 'components/pipeline.yaml')
    
    print(f"Validating: {pipeline_file}")
    
    with open(pipeline_file, 'r') as f:
        pipeline = yaml.safe_load(f)
    
    # Check required fields
    required_fields = ['pipelineInfo', 'components', 'deploymentSpec']
    
    for field in required_fields:
        if field not in pipeline:
            print(f"❌ Missing required field: {field}")
            sys.exit(1)
    
    print('✅ Pipeline YAML structure is valid')
    print(f"Pipeline name: {pipeline['pipelineInfo'].get('name', 'N/A')}")
    print(f"Pipeline description: {pipeline['pipelineInfo'].get('description', 'N/A')}")
    print(f"Number of components: {len(pipeline['components'])}")
    print(f"SDK version: {pipeline.get('sdkVersion', 'N/A')}")
    
    # List components
    print("\\nPipeline Components:")
    for comp_name in pipeline['components'].keys():
        print(f"  - {comp_name}")
    
    sys.exit(0)
    
except yaml.YAMLError as e:
    print(f'❌ YAML parsing error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Pipeline validation failed: {e}')
    sys.exit(1)
EOF
                '''
                
                // Count pipeline components and check structure
                sh '''
                    echo ""
                    echo "📊 Pipeline Statistics:"
                    
                    # Count components
                    component_count=$(grep -c "executorLabel:" ${PIPELINE_FILE} 2>/dev/null || echo "0")
                    echo "  - Number of execution steps: $component_count"
                    
                    # Count tasks
                    task_count=$(grep -c "taskInfo:" ${PIPELINE_FILE} 2>/dev/null || echo "0")
                    echo "  - Number of tasks: $task_count"
                    
                    # File size
                    line_count=$(wc -l < ${PIPELINE_FILE} 2>/dev/null || echo "0")
                    echo "  - Total lines in pipeline: $line_count"
                    
                    # Check for common issues
                    echo ""
                    echo "🔍 Checking for common issues..."
                    
                    if grep -q "YOUR_USERNAME" ${PIPELINE_FILE}; then
                        echo "⚠️  Warning: Found placeholder 'YOUR_USERNAME' in pipeline"
                    fi
                    
                    if grep -q "REPLACE_ME" ${PIPELINE_FILE}; then
                        echo "⚠️  Warning: Found placeholder 'REPLACE_ME' in pipeline"
                    fi
                    
                    echo "✅ Basic checks completed"
                '''
            }
        }
    }
    
    post {
        success {
            echo '================================================'
            echo '✅ Pipeline CI completed successfully!'
            echo '================================================'
            
            // Archive the compiled pipeline
            archiveArtifacts artifacts: 'components/pipeline.yaml', fingerprint: true
            
            echo 'The compiled pipeline has been archived and is ready for deployment to Kubeflow.'
            
            // Optional: Display final summary
            sh '''
                echo ""
                echo "📋 Build Summary:"
                echo "================="
                echo "Build Number: ${BUILD_NUMBER}"
                echo "Status: SUCCESS"
                echo "Artifact: components/pipeline.yaml"
                echo "Pipeline ready for deployment"
            '''
            
            // Optional: Send notification (if configured)
            // emailext subject: "Jenkins: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER} - Success",
            //          body: "Pipeline compiled successfully!",
            //          to: "your-email@example.com"
        }
        
        failure {
            echo '================================================'
            echo '❌ Pipeline CI failed!'
            echo '================================================'
            
            // Display helpful error information
            sh '''
                echo "Debug Information:"
                echo "=================="
                echo "Python version available:"
                python3 --version 2>/dev/null || echo "Python3 not found"
                echo ""
                echo "Directory structure:"
                ls -la
                echo ""
                echo "Python files found:"
                find . -name "*.py" -type f | head -10
                echo ""
                echo "Check if pipeline.py exists:"
                ls -la pipeline.py 2>/dev/null || echo "pipeline.py not found"
            '''
            
            echo 'Please check the logs above for error details.'
            
            // Optional: Send notification (if configured)
            // emailext subject: "Jenkins: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER} - Failed",
            //          body: "Pipeline compilation failed. Check Jenkins for details.",
            //          to: "your-email@example.com"
        }
        
        always {
            echo '================================================'
            echo 'Cleaning up workspace...'
            echo '================================================'
            // Clean up Python cache files and virtual environment
            sh '''
                echo "Cleaning Python cache..."
                find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
                find . -type f -name "*.pyc" -delete 2>/dev/null || true
                find . -type f -name "*.pyo" -delete 2>/dev/null || true
                
                echo "Removing virtual environment..."
                rm -rf venv 2>/dev/null || true
                
                echo "Cleaning other temporary files..."
                rm -f get-pip.py 2>/dev/null || true
                
                echo "Cleanup complete!"
            '''
        }
    }
}