from typing import Annotated
from langchain_core.tools import tool
import boto3
from botocore.client import Config
import logging
from typing import Dict, Any
import json
from datetime import datetime

# Lo necesito porque 'last_modified' viene en formato fecha
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Custom log handler to capture logs in the result dictionary
class DictLogHandler(logging.Handler):
    def __init__(self, log_list):
        super().__init__()
        self.log_list = log_list

    def emit(self, record):
        log_entry = {"level": record.levelname, "message": self.format(record)}
        self.log_list.append(log_entry)

# S3 Client setup
class S3Client:
    def __init__(self, access_key, secret_key, endpoint_url, region_name):
        self.client = self._create_s3_client(access_key, secret_key, endpoint_url, region_name)

    def _create_s3_client(self, access_key, secret_key, endpoint_url, region_name):
        try:
            return boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                config=Config(signature_version="s3v4"),
                region_name=region_name,
            )
        except Exception as e:
            return None
    
    def get_object_metadata(self, bucket_name: str, file_path: str) -> Dict[str, Any]:
        try:
            response = self.client.head_object(Bucket=bucket_name, Key=file_path)
            metadata = { #se puede ampliar si miramos Response Syntax
                "ContentLength": response.get("ContentLength"),
                "ContentType": response.get("ContentType"),
                "LastModified": response.get("LastModified"),
                "ETag": response.get("ETag"),
                "VersionId": response.get("VersionId"),
                "ServerSideEncryption": response.get("ServerSideEncryption")
                #"Metadata": response.get("Metadata", {}),
            }
            return metadata
        except self.client.exceptions.ClientError:
            return {} #devuelve diccioario vacio donde se almacenan error de mercurio sino da error 

@tool
def hermes(bucket_name,file_path) -> str:
    """
    Extracts metadata for a specific file in an S3 bucket.
    Returns a JSON string containing the file path, its metadata, and any logs or errors.
    """
    # Initialize result dictionary
    result = {"status": "success", "file_path": file_path, "metadata": None, "logs": [], "errors": []}
    # Set up logging to capture in the result dictionary
    logger = logging.getLogger(__name__)
    handler = DictLogHandler(result["logs"])
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Initialize S3 client
    s3_client = S3Client(
        access_key="0030e94285353960000000012",
        secret_key="K003HiIvvB32rxCRH4bC///m7cV1+3Q",
        endpoint_url="https://s3.eu-central-003.backblazeb2.com",
        region_name="eu-central-003",
    )
    if s3_client.client is None:
        error_message = "S3 client initialization failed"
        logger.error(error_message)
        result["status"] = "error"
        result["errors"].append({"message": error_message})
        return json.dumps(result)

    metadata = s3_client.get_object_metadata(bucket_name, file_path)
    if metadata:
        # logger.info(f"Metadata extracted successfully for file: {file_path}")
        result["metadata"] = metadata
    else:
        result["status"] = "error" #dudas: mercurio file_content handling 
        return json.dumps(result)
    
    return json.dumps([result], cls= DateTimeEncoder)

#usamos invoke para usar la Tool a traves de un diccionario 
#ejemplo: chain.invoke({"topic": "bears"}) 
#bucket_name = "EWA-S3-APP-IA-UPLOAD"
#file_path = "2020-12-Huge Database Collection/Chessmate.com_findings.csv"
#result = hermes.invoke({"bucket_name": bucket_name, "file_path": file_path})
#print(result)
