import os
import json
import pandas as pd

from ml.entity.post_quality_feature.config_entity import DataValidationConfig
from ml.entity.post_quality_feature.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact
)


class DataValidation:

    def __init__(self, config: DataValidationConfig, ingestion_artifact: DataIngestionArtifact):
        self.config = config
        self.ingestion_artifact = ingestion_artifact


    def validate_missing_column(self, df: pd.DataFrame) -> dict:

        missing_columns = [
            col for col in self.config.required_columns
            if col not in df.columns
        ]

        if missing_columns:
            return {
                "error": True,
                "msg": f"Missing columns found: {missing_columns}"
            }

        return {
            "error": False,
            "msg": "All required columns are present."
        }


    def handle_null_values(self, df: pd.DataFrame) -> tuple:

        cleaned_df = df.copy()

        # Only handle text columns explicitly
        if "body" in cleaned_df.columns:
            cleaned_df["body"] = cleaned_df["body"].fillna("")

        if "title" in cleaned_df.columns:
            cleaned_df["title"] = cleaned_df["title"].fillna("")

        return {
            "error": False,
            "msg": "Null values handled for text columns."
        }, cleaned_df


    def validate_imp_col_empty(self, df: pd.DataFrame) -> tuple:

        res = {}

        # Detect invalid rows
        title_empty = df["title"].str.strip() == ""
        label_null = df[["effort", "openness"]].isnull().any(axis=1)

        invalid_rows = title_empty | label_null

        # Collect ids
        if "id" in df.columns:
            invalid_ids = df.loc[invalid_rows, "id"].tolist()
        else:
            invalid_ids = df.index[invalid_rows].tolist()

        cleaned_df = df[~invalid_rows].copy()

        if invalid_ids:
            res["error"] = True
            res["msg"] = f"Invalid rows found for ids: {invalid_ids}"
        else:
            res["error"] = False
            res["msg"] = "No invalid rows detected in important columns."

        return res, cleaned_df


    def validate_labels(self, df: pd.DataFrame) -> tuple:

        res = {}

        valid_effort = df["effort"].isin([0, 1])
        valid_openness = df["openness"].isin([0, 1])

        invalid_rows = ~(valid_effort & valid_openness)

        cleaned_df = df[~invalid_rows].copy()

        if invalid_rows.any():
            res["error"] = True
            res["msg"] = "Found rows with invalid label values."
        else:
            res["error"] = False
            res["msg"] = "All labels are valid."

        return res, cleaned_df


    def validate_data(self) -> DataValidationArtifact:

        # Load dataset
        df = pd.read_csv(self.ingestion_artifact.dataset_path)

        dataset_size_before = len(df)

        # Schema validation
        missing_col_res = self.validate_missing_column(df)

        if missing_col_res["error"]:
            raise Exception(missing_col_res["msg"])

        # Handle null values
        null_res, df_cleaned = self.handle_null_values(df)

        # Validate important columns
        imp_col_res, df_cleaned = self.validate_imp_col_empty(df_cleaned)

        # Validate labels
        label_res, df_cleaned = self.validate_labels(df_cleaned)

        dataset_size_after = len(df_cleaned)

        # Save validated dataset
        os.makedirs(self.config.validation_artifact_dir, exist_ok=True)

        validated_path = os.path.join(
            self.config.validation_artifact_dir,
            "validated_dataset.csv"
        )

        df_cleaned.to_csv(validated_path, index=False)

        validation_status = not (
            missing_col_res["error"]
            or imp_col_res["error"]
            or null_res["error"]
            or label_res["error"]
        )

        # Create validation report
        report = {
            "dataset_size_before": dataset_size_before,
            "dataset_size_after": dataset_size_after,
            "missing_column_check": missing_col_res,
            "important_columns_empty_check": imp_col_res,
            "null_handling": null_res,
            "label_validation": label_res,
            "validation_status": validation_status
        }

        os.makedirs(os.path.dirname(self.config.validation_report_path), exist_ok=True)

        with open(self.config.validation_report_path, "w") as f:
            json.dump(report, f, indent=4)

        return DataValidationArtifact(
            validated_dataset_path=validated_path,
            validation_status=validation_status
        )