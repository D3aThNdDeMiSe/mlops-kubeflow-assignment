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
                
                sh '''
                    echo "Setting up Python virtual environment..."
                    
                    rm -rf venv
                    python3 -m venv venv
                    . venv/bin/activate
                    
                    echo "Upgrading pip, setuptools, and wheel..."
                    pip install --upgrade pip setuptools wheel
                    
                    echo "Installing project dependencies..."
                    pip install --upgrade cython  # ensure C extensions can build
                    pip install -r requirements.txt
                    
                    echo "✅ Dependencies installed successfully in virtual environment"
                '''
                
                sh '''
                    . venv/bin/activate
                    echo ""
                    echo "Environment Information:"
                    echo "========================"
                    python --version
                    which python
                    pip list | grep -E "kfp|dvc|scikit-learn|pandas"
                '''
            }
        }
        
        stage('Pipeline Compilation') {
            steps {
                sh '''
                    . venv/bin/activate
                    echo "📦 Compiling Kubeflow pipeline..."
                    python pipeline.py
                    
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
                sh '''
                    . venv/bin/activate
                    echo "🔍 Validating pipeline YAML structure..."
                    python << EOF
import yaml, sys
try:
    with open('${PIPELINE_FILE}', 'r') as f:
        pipeline = yaml.safe_load(f)
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
            archiveArtifacts artifacts: 'components/pipeline.yaml', fingerprint: true
        }
        
        failure {
            echo '================================================'
            echo '❌ Pipeline CI failed!'
            echo '================================================'
        }
        
        always {
            echo '================================================'
            echo 'Cleaning up workspace...'
            echo '================================================'
            sh '''
                find . -type d -name __pycache__ -exec rm -rf {} + || true
                find . -type f -name "*.pyc" -delete || true
                rm -rf venv || true
            '''
        }
    }
}
