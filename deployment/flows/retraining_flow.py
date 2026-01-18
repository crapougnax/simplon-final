from prefect import flow, task
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import mlflow
import mlflow.sklearn

@task
def load_data():
    mat = pd.read_csv('../../sources/student/student-mat.csv', sep=';')
    por = pd.read_csv('../../sources/student/student-por.csv', sep=';')
    df = pd.concat([mat, por], ignore_index=True)
    return df

@task
def filter_data(df):
    # Filter out G3 = 0 (Dropouts/Absences)
    return df[df['G3'] > 0]

@task
def train_model(df):
    X = df.drop(['G3'], axis=1)
    y = df['G3']
    
    categorical_features = ['school', 'sex', 'address', 'famsize', 'Pstatus', 'Mjob', 'Fjob', 'reason', 'guardian', 'schoolsup', 'famsup', 'paid', 'activities', 'nursery', 'higher', 'internet', 'romantic']
    numerical_features = [c for c in X.columns if c not in categorical_features]
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    
    lr = LinearRegression()
    rf = RandomForestRegressor(random_state=42)
    ensemble = VotingRegressor(estimators=[('lr', lr), ('rf', rf)])
    
    pipeline = Pipeline(steps=[('preprocessor', preprocessor), ('model', ensemble)])
    pipeline.fit(X, y)
    return pipeline

@task
def log_experiment(pipeline):
    mlflow.set_tracking_uri("http://mlflow:5000")
    mlflow.set_experiment("model_retraining")
    
    with mlflow.start_run():
        mlflow.log_param("model_type", "VotingRegressor (LR + RF)")
        mlflow.log_param("filtered_dropouts", True)
        
        mlflow.sklearn.log_model(pipeline, "model")
        print("Model logged to MLFlow")

@flow(name="Model Retraining Flow")
def retraining_flow():
    data = load_data()
    filtered_data = filter_data(data)
    model = train_model(filtered_data)
    log_experiment(model)

if __name__ == "__main__":
    retraining_flow()
