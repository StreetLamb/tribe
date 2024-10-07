from langchain_core.tools import tool
import boto3
from botocore.client import Config
import logging
from typing import Dict, Any
import json
from datetime import datetime, timedelta
import io
import random
from app.core.graph.skills.hermes import DictLogHandler
from app.core.graph.skills.mercurio import analyze_csv_security, create_findings_pdf, upload_to_app  # asi evito tener que copiarlas

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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

    # nueva funcion que busca el archivo mas reciente
    def find_most_recent_file(
        self, bucket_name: str, folder_path: str, file_prefix: str, days_to_check: int
    ) -> Dict[str, Any]:
        today = datetime.now()
        for i in range(1, days_to_check):
            date = today - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")  # Si cambia el formato de fecha hay que cambiar esto
            file_name = f"{folder_path}/{date_str}-{file_prefix}"  # concateno usando el patron en carpeta UPLOADS
            # referencia: {results_money}/{2023-12-18}-{Spain}
            try:
                respuesta = self.client.list_objects_v2(
                    Bucket=bucket_name, Prefix=file_name, MaxKeys=1
                )  # le pido que me de un objecto pero si quiero mas cambio maxkeys
                if "Contents" in respuesta:
                    file_info = respuesta["Contents"][
                        0
                    ]  # para quedarnos con el primer objecto en el que esta tambien LastModified, etc..
                    logger.info(f"Found file: {file_info['Key']}")
                    return {
                        "file_path": file_info[
                            "Key"
                        ]  # es una string y tiene el nombre del archivo se pueden añadir mas
                    }
            except Exception as e:
                logger.error(f"Error accessing S3: {str(e)}")
                continue
        return None

    def get_s3_object(self, bucket_name: str, file_path: str):
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=file_path)
            return io.BytesIO(response["Body"].read())
        except Exception as e:
            logger.error(f"Error retrieving S3 object: {str(e)}")
            return None


@tool
def hades(bucket_name, folder_path, file_prefix, days_to_check) -> str:
    """
    Searches for the most recent file in S3 with a specific prefix and date pattern,
    Analyzes its content, creates a PDF report, and uploads it to the app.
    """
    # Initialize result dictionary
    result = {
        "status": "success",
        "folder_path": folder_path,
        "analysis_result": None,
        "logs": [],
        "errors": [],
    }  # dejo los logs porque me imprimen el archivo encontrado

    logger = logging.getLogger(__name__)  # seguro que se pueden hacer los logs mas sencillos
    logger.setLevel(logging.CRITICAL)
    formatter = logging.Formatter("%(message)s")  # simplificando esta parte se quito la fecha que no aportaba nada

    handler = DictLogHandler(
        result["logs"]
    )  # si quiero ver el archivo en pantalla tengo que dejar el log's si no hacen falta es quitar log
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    s3_client = S3Client(
        access_key="0030e94285353960000000012",
        secret_key="K003HiIvvB32rxCRH4bC///m7cV1+3Q",
        endpoint_url="https://s3.eu-central-003.backblazeb2.com",
        region_name="eu-central-003",
    )
    # DEBUGGIN
    if s3_client.client is None:
        error_message = "S3 client initialization failed"
        logger.error(error_message)
        result["status"] = "error"
        result["errors"].append({"message": error_message})
        return json.dumps([result])

    recent_file = s3_client.find_most_recent_file(bucket_name, folder_path, file_prefix, days_to_check)
    if recent_file is None:
        error_message = f"No matching files found in {days_to_check} days"
        logger.error(error_message)
        result["status"] = "error"
        result["errors"].append({"message": error_message})
        return json.dumps([result])

    file_path = recent_file["file_path"]
    file_content = s3_client.get_s3_object(bucket_name, file_path)
    if file_content is None:
        result["status"] = "error"
        return json.dumps([result])

    data_content = file_content.getvalue().decode("utf-8")
    analysis_report = analyze_csv_security(data_content, logger)

    if analysis_report is None:
        result["status"] = "error"
        return json.dumps([result])

    pdf_buffer = create_findings_pdf(analysis_report)
    filename = f"data_analysis_report_{random.randint(1, 1000)}.pdf"
    upload_success, upload_result = upload_to_app(pdf_buffer, filename, "localhost", logger)

    if upload_success:
        result["analysis_result"] = {"uploaded_file": filename}
    else:
        result["error"] = f"Failed to upload file: {upload_result}"

    return json.dumps([result])


# Example usage
# bucket_name = "EWA-S3-APP-IA-UPLOAD"
# folder_path = "results_money"
# file_prefix = "Spain"
# days_to_check = 1000
# result = hades.invoke(
#    {"bucket_name": bucket_name, "folder_path": folder_path, "file_prefix": file_prefix, "days_to_check": days_to_check}
# )
# print(result)
