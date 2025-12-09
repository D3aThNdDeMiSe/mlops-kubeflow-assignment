"""
Kubeflow Pipeline Definition for Iris Classification with DVC Integration

This pipeline demonstrates:
1. Data versioning with DVC - fetches data from DVC remote storage
2. Preprocessing with scikit-learn StandardScaler
3. Model training with Random Forest Classifier
4. Model evaluation with comprehensive metrics
"""
from kfp import dsl, compiler
from src.pipeline_components import (
    data_extraction,
    data_preprocessing,
    model_training,
    model_evaluation
)


@dsl.pipeline(
    name='Iris Classification Pipeline',
    description='End-to-end ML pipeline for Iris species classification using DVC'
)
def iris_classification_pipeline(
    repo_url: str = "https://github.com/D3aThNdDeMiSe/mlops-kubeflow-assignment.git",
    data_path: str = "data/iris.csv",
    test_size: float = 0.2,
    n_estimators: int = 100,
    max_depth: int = 10,
    random_state: int = 42
):
    
    # Step 1: Data Extraction from DVC
    extract_task = data_extraction(
        repo_url=repo_url,
        data_path=data_path
    )
    extract_task.set_display_name("Extract Data from DVC")
    
    # Step 2: Data Preprocessing
    preprocess_task = data_preprocessing(
        input_data=extract_task.outputs['dataset_path'],
        test_size=test_size,
        random_state=random_state
    )
    preprocess_task.set_display_name("Preprocess Data")
    preprocess_task.after(extract_task)
    
    # Step 3: Model Training
    train_task = model_training(
        train_data=preprocess_task.outputs['train_data'],
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state
    )
    train_task.set_display_name("Train Classifier")
    train_task.after(preprocess_task)
    
    # Step 4: Model Evaluation
    eval_task = model_evaluation(
        model_input=train_task.outputs['model_output'],
        test_data=preprocess_task.outputs['test_data']
    )
    eval_task.set_display_name("Evaluate Model")
    eval_task.after(train_task)


def compile_pipeline():
    compiler.Compiler().compile(
        pipeline_func=iris_classification_pipeline,
        package_path='components/pipeline.yaml'
    )
    print("Pipeline compiled successfully to pipeline.yaml")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    compile_pipeline()