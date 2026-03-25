import logging
import time
from typing import Any, Dict, List

from google.api_core.exceptions import GoogleAPIError, NotFound
from google.cloud import bigquery
from pydantic import BaseModel, Field, ValidationError

from .base import BaseSink

logger = logging.getLogger(__name__)


class BigQuerySinkError(Exception):
    """Base exception for BigQuery sink errors."""
    pass


class BigQueryConnectionError(BigQuerySinkError):
    """Raised when connection to BigQuery fails."""
    pass


class BigQueryInsertError(BigQuerySinkError):
    """Raised when inserting rows to BigQuery fails."""
    pass


class BigQueryTableError(BigQuerySinkError):
    """Raised when table operations fail."""
    pass


class BigQuerySinkParams(BaseModel):
    project_id: str = Field(..., description="GCP project ID")
    dataset: str = Field(..., description="BigQuery dataset name")
    table: str = Field(..., description="BigQuery table name")
    credentials_path: str | None = Field(
        default=None, description="Path to service account JSON credentials"
    )


class BigQuerySink(BaseSink):
    """
    A sink that writes data to Google BigQuery tables.
    """

    def __init__(self, sink_params: Dict[str, Any]):
        try:
            params = BigQuerySinkParams.model_validate(sink_params)
        except ValidationError as e:
            logger.error(f"Invalid sink parameters: {e}")
            raise BigQueryConnectionError(
                f"Invalid sink parameters: {e}"
            ) from e

        self.project_id = params.project_id
        self.dataset = params.dataset
        self.table = params.table
        self.client: bigquery.Client | None = None

        # Initialize BigQuery client
        if params.credentials_path:
            try:
                self.client = bigquery.Client.from_service_account_json(
                    params.credentials_path, project=self.project_id
                )
                logger.info(
                    f"BigQuery client initialized for project: {self.project_id}"
                )
            except FileNotFoundError as e:
                logger.error(f"Credentials file not found: {params.credentials_path}")
                raise BigQueryConnectionError(
                    f"Credentials file not found: {params.credentials_path}"
                ) from e
            except Exception as e:
                logger.error(f"Failed to initialize BigQuery client: {e}")
                raise BigQueryConnectionError(
                    f"Failed to initialize BigQuery client: {e}"
                ) from e
        else:
            raise BigQueryConnectionError(
                "Invalid credentials for BigQuerySink: credentials_path is required"
            )

        self.table_ref = f"{self.project_id}.{self.dataset}.{self.table}"

    def publish(self, record: Dict[str, Any]) -> None:
        """Publish a single record to BigQuery."""
        self.publish_bulk([record])

    def publish_bulk(self, records: List[Dict[str, Any]]) -> None:
        """Publish records to BigQuery using streaming inserts."""
        if not records:
            logger.debug("No records to publish, skipping")
            return

        if self.client is None:
            raise BigQueryConnectionError("BigQuery client is not initialized")

        self._ensure_table_exists(records[0])

        try:
            errors = self.client.insert_rows_json(self.table_ref, records)
            if errors:
                error_messages = "; ".join(str(e) for e in errors)
                logger.error(f"Failed to insert some rows: {error_messages}")
                raise BigQueryInsertError(
                    f"Failed to insert rows to BigQuery: {error_messages}"
                )
            logger.debug(f"Successfully inserted {len(records)} records to BigQuery")
        except GoogleAPIError as e:
            logger.error(f"BigQuery API error during insert: {e}")
            raise BigQueryInsertError(
                f"Failed to insert rows to BigQuery: {e}"
            ) from e


    def _ensure_table_exists(self, sample_record: Dict[str, Any]) -> None:
        """Check if table exists, create it if not based on sample record schema."""
        if self.client is None:
            raise BigQueryConnectionError("BigQuery client is not initialized")

        try:
            self.client.get_table(self.table_ref)
            logger.debug(f"Table {self.table_ref} exists")
        except NotFound:
            logger.info(f"Table {self.table_ref} not found, creating...")
            self._create_table(sample_record)
        except GoogleAPIError as e:
            logger.error(f"Failed to check table existence: {e}")
            raise BigQueryTableError(
                f"Failed to check if table exists: {e}"
            ) from e

    def _create_table(self, sample_record: Dict[str, Any]) -> None:
        """Create the BigQuery table based on sample record schema."""
        if self.client is None:
            raise BigQueryConnectionError("BigQuery client is not initialized")

        try:
            schema = self._infer_schema(sample_record)
            table = bigquery.Table(self.table_ref, schema=schema)
            self.client.create_table(table)
            logger.info(f"Table {self.table_ref} created successfully")

            # Wait for table to be available
            self._wait_for_table()
        except GoogleAPIError as e:
            logger.error(f"Failed to create table: {e}")
            raise BigQueryTableError(
                f"Failed to create table {self.table_ref}: {e}"
            ) from e

    def _wait_for_table(self, max_retries: int = 3, delay: float = 1.0) -> None:
        """Wait for the table to become available after creation."""
        if self.client is None:
            raise BigQueryConnectionError("BigQuery client is not initialized")

        for attempt in range(max_retries):
            time.sleep(delay)
            try:
                self.client.get_table(self.table_ref)
                logger.debug(f"Table {self.table_ref} is now available")
                return
            except NotFound:
                logger.debug(
                    f"Table not yet available, retry {attempt + 1}/{max_retries}"
                )
                continue
            except GoogleAPIError as e:
                logger.warning(f"Error checking table availability: {e}")
                continue

        logger.warning(
            f"Table {self.table_ref} may not be fully available "
            f"after {max_retries} retries"
        )

    def _infer_schema(self, record: Dict[str, Any]) -> List[bigquery.SchemaField]:
        """Infer BigQuery schema from a sample record."""
        type_mapping = {
            str: "STRING",
            int: "INTEGER",
            float: "FLOAT",
            bool: "BOOLEAN",
            dict: "JSON",
            list: "ARRAY",
        }
        schema = []
        for key, value in record.items():
            try:
                if isinstance(value, list):
                    if value:
                        element_type = type_mapping.get(type(value[0]), "STRING")
                    else:
                        element_type = "STRING"
                    schema.append(
                        bigquery.SchemaField(key, element_type, mode="REPEATED")
                    )
                else:
                    bq_type = type_mapping.get(type(value), "STRING")
                    schema.append(bigquery.SchemaField(key, bq_type, mode="NULLABLE"))
            except Exception as e:
                logger.warning(
                    f"Failed to infer schema for field '{key}', "
                    f"defaulting to STRING: {e}"
                )
                schema.append(bigquery.SchemaField(key, "STRING", mode="NULLABLE"))
        return schema

    def close(self) -> None:
        """Close the BigQuery client."""
        if self.client is not None:
            try:
                self.client.close()
                logger.info("BigQuery client closed successfully")
            except Exception as e:
                logger.warning(f"Error closing BigQuery client: {e}")
            finally:
                self.client = None
