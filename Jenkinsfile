pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.9'
        PIPELINE_FILE = 'components/pipeline.yaml'
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    stages {
        stage('Environment Setup') {
            steps {
                echo '================================================'
                echo 'Stage 1: Environment Setup'
                echo '================================================'
                
                script {
                    echo "Build #${env.BUILD_NUMBER}"
                    echo "Branch: ${env.GIT_BRANCH}"
                    echo "Commit: ${env.GIT_COMMIT}"
                }
                
                checkout scm
                
                // First, check if Python 3.9 is available
                sh '''
                    echo "Checking Python versions available..."
                    python3.9 --version || echo "Python 3.9 not found, will use python3"
                    
                    # Use python3.9 if available, otherwise fall back to python3
                    if command -v python3.9 &> /dev/null; then
                        PYTHON_CMD=python3.9
                        echo "Using Python 3.9"
                    else
                        PYTHON_CMD=python3
                        echo "Using default Python 3"
                        $PYTHON_CMD --version
                    fi
                    
                    echo "Setting up Python virtual environment..."
                    rm -rf venv
                    
                    # Create virtual environment with the chosen Python version
                    $PYTHON_CMD -m venv venv
                    
                    # Activate virtual environment
                    . venv/bin/activate
                    
                    echo "Python version in venv:"
                    python --version
                    
                    echo "Upgrading pip and installing build tools..."
                    pip install --upgrade pip setuptools wheel
                    
                    echo "Installing project dependencies..."
                    pip install -r requirements.txt
                    
                    echo "✅ Dependencies installed successfully in virtual environment"
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
                    echo "Virtual environment location:"
                    which python
                    echo ""
                    echo "Key packages installed:"
                    pip list | grep -E "kfp|dvc|scikit-learn|pandas|numpy"
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
                    python pipeline.py
                    
                    # Verify the pipeline YAML was created
                    if [ -f "${PIPELINE_FILE}" ]; then
                        echo "✅ Pipeline compiled successfully!"
                        echo "📄 Pipeline YAML file size: $(du -h ${PIPELINE_FILE} | cut -f1)"
                        ls -lh ${PIPELINE_FILE}
                    else
                        echo "❌ Pipeline compilation failed - pipeline.yaml not found"
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
                    python << EOF
import yaml
import sys

try:
    with open('${PIPELINE_FILE}', 'r') as f:
        pipeline = yaml.safe_load(f)
        
    # Check required fields
    assert 'pipelineInfo' in pipeline, 'Missing pipelineInfo section'
    assert 'components' in pipeline, 'Missing components section'
    assert 'deploymentSpec' in pipeline, 'Missing deploymentSpec section'
    
    print('✅ Pipeline YAML structure is valid')
    print(f'Pipeline name: {pipeline["pipelineInfo"]["name"]}')
    print(f'Pipeline description: {pipeline["pipelineInfo"]["description"]}')
    print(f'Number of components: {len(pipeline["components"])}')
    print(f'SDK version: {pipeline.get("sdkVersion", "N/A")}')
    
    sys.exit(0)
except Exception as e:
    print(f'❌ Pipeline validation failed: {e}')
    sys.exit(1)
EOF
                '''
                
                // Count pipeline components
                sh '''
                    echo ""
                    echo "📊 Pipeline Statistics:"
                    component_count=$(grep -c "executorLabel:" ${PIPELINE_FILE} || echo "0")
                    echo "  - Number of execution steps: $component_count"
                    
                    line_count=$(wc -l < ${PIPELINE_FILE})
                    echo "  - Total lines in pipeline: $line_count"
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
            
            // Optional: Send notification (if configured)
            // emailext subject: "Jenkins: ${env.JOB_NAME} - Build #${env.BUILD_NUMBER} - Success",
            //          body: "Pipeline compiled successfully!",
            //          to: "your-email@example.com"
        }
        
        failure {
            echo '================================================'
            echo '❌ Pipeline CI failed!'
            echo '================================================'
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
                find . -type d -name __pycache__ -exec rm -rf {} + || true
                find . -type f -name "*.pyc" -delete || true
                rm -rf venv || true
            '''
        }
    }
}