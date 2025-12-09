The model training component takes four inputs:

1. train_data (Input[Dataset]): An artifact input containing the preprocessed training dataset from the data preprocessing component. This ensures separation of concerns and allows the preprocessing logic to be modified independently.
2. n_estimators (int, default=100): A hyperparameter controlling the number of decision trees in the Random Forest ensemble. This scalar parameter can be adjusted in the Kubeflow UI to tune model performance.
3. max_depth (int, default=10): A hyperparameter that limits tree depth to prevent overfitting. This regularization parameter balances model complexity with generalization.
4. random_state (int, default=42): A seed value for the random number generator, ensuring reproducible results across multiple pipeline runs.

The component produces one output:

model_output (Output[Model]): An artifact containing the trained Random Forest classifier, serialized using joblib. This model artifact is stored by Kubeflow and passed to the evaluation component, enabling model versioning, tracking, and potential deployment without retraining.