"""
Kubeflow Pipeline Components for Iris Classification
"""
from kfp import dsl
from kfp.dsl import component, Input, Output, Dataset, Model, Metrics


@component(
    base_image="python:3.9",
    packages_to_install=["pandas==2.1.3", "dvc==3.30.1", "pygit2==1.13.3"]
)
def data_extraction(
    dataset_path: Output[Dataset],
    repo_url: str = "https://github.com/YOUR_USERNAME/mlops-kubeflow-assignment.git",
    data_path: str = "data/iris.csv"
):

    import pandas as pd
    import dvc.api
    import os
    
    print(f"Fetching DVC tracked data from repository...")
    print(f"Repo: {repo_url}")
    print(f"Path: {data_path}")
    
    try:
        # Use DVC API to fetch the data directly from remote storage
        with dvc.api.open(data_path, repo=repo_url, mode='r') as f:
            df = pd.read_csv(f)
        
        print(f"Data fetched successfully from DVC remote!")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
    except Exception as e:
        print(f"Warning: Could not fetch from DVC remote: {e}")
        print("Falling back to local Iris dataset for demonstration...")
        
        # Fallback: Load Iris dataset locally
        from sklearn.datasets import load_iris
        iris = load_iris()
        df = pd.DataFrame(iris.data, columns=iris.feature_names)
        df['target'] = iris.target
        print(f"Using fallback data. Shape: {df.shape}")
    
    # Save to output path
    df.to_csv(dataset_path.path, index=False)
    print(f"Data extraction complete!")


@component(
    base_image="python:3.9",
    packages_to_install=["pandas==2.1.3", "scikit-learn==1.3.2", "numpy==1.26.4"]
)
def data_preprocessing(
    input_data: Input[Dataset],
    train_data: Output[Dataset],
    test_data: Output[Dataset],
    test_size: float = 0.2,
    random_state: int = 42
):

    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    
    print("Starting data preprocessing...")
    
    # Load data
    df = pd.read_csv(input_data.path)
    print(f"Loaded data shape: {df.shape}")
    
    # Handle missing values
    df = df.dropna()
    
    # Separate features and target
    X = df.drop('target', axis=1)
    y = df['target']
    
    print(f"Features: {list(X.columns)}")
    print(f"Class distribution: {y.value_counts().to_dict()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Convert back to DataFrame
    train_df = pd.DataFrame(X_train_scaled, columns=X.columns)
    train_df['target'] = y_train.values
    
    test_df = pd.DataFrame(X_test_scaled, columns=X.columns)
    test_df['target'] = y_test.values
    
    # Save processed data
    train_df.to_csv(train_data.path, index=False)
    test_df.to_csv(test_data.path, index=False)
    
    print(f"Preprocessing complete. Train: {train_df.shape}, Test: {test_df.shape}")


@component(
    base_image="python:3.9",
    packages_to_install=["pandas==2.1.3", "scikit-learn==1.3.2", "joblib==1.3.2"]
)
def model_training(
    train_data: Input[Dataset],
    model_output: Output[Model],
    n_estimators: int = 100,
    max_depth: int = 10,
    random_state: int = 42
):

    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    import joblib
    
    print("Starting model training...")
    
    # Load training data
    train_df = pd.read_csv(train_data.path)
    X_train = train_df.drop('target', axis=1)
    y_train = train_df['target']
    
    print(f"Training data shape: {X_train.shape}")
    print(f"Number of classes: {len(y_train.unique())}")
    
    # Train classifier model
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Save model
    joblib.dump(model, model_output.path)
    
    print(f"Model trained successfully with {n_estimators} estimators")
    print(f"Training accuracy: {model.score(X_train, y_train):.4f}")


@component(
    base_image="python:3.9",
    packages_to_install=["pandas==2.1.3", "scikit-learn==1.3.2", "joblib==1.3.2"]
)
def model_evaluation(
    model_input: Input[Model],
    test_data: Input[Dataset],
    metrics_output: Output[Metrics]
):

    import pandas as pd
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
    import joblib
    import json
    
    print("Starting model evaluation...")
    
    # Load model and test data
    model = joblib.load(model_input.path)
    test_df = pd.read_csv(test_data.path)
    
    X_test = test_df.drop('target', axis=1)
    y_test = test_df['target']
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, y_pred, average='weighted'
    )
    
    # Prepare metrics dictionary
    metrics = {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1)
    }
    
    print(f"Evaluation Metrics:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    
    # Detailed classification report
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, 
                                target_names=['setosa', 'versicolor', 'virginica']))
    
    # Log metrics for Kubeflow
    metrics_output.log_metric("accuracy", accuracy)
    metrics_output.log_metric("precision", precision)
    metrics_output.log_metric("recall", recall)
    metrics_output.log_metric("f1_score", f1)
    
    # Save metrics to file
    with open(metrics_output.path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("Evaluation complete!")