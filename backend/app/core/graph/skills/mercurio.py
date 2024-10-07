from langchain_core.tools import tool
import boto3
from botocore.client import Config
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import requests
import random
from langchain_groq import ChatGroq  # Updated import
from langchain_core.prompts import ChatPromptTemplate  # New import
import logging
import json
from requests_toolbelt import MultipartEncoder
import os
from app.core.graph.skills.pluton import DictLogHandler
# from pluton import DateTimeEncoder

# Initialize Groq client
groq_client = ChatGroq(api_key="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", model_name="llama3-8b-8192")

# es diferente a la de mercurio por eso no la sustituyo
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

    # usamos BytesIO para operaciones de buffer
    # necesitamos el archivo en buffer para subirlo a la app 
    def get_s3_object(self, bucket_name: str, file_path: str):
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=file_path)
            return io.BytesIO(response["Body"].read()) #archivo se almacena archivo tipo BytesIO
        except Exception as e:
            return None

# desde hace un par de versiones poner "from messages sobra"
def analyze_csv_security(csv_content: str, logger) -> str:
    try:
        prompt = ChatPromptTemplate(
            [
                ("system", "You are a cybersecurity expert analyzing CSV data for security implications."),
                (
                    "user",
                    f"Analyze this CSV data and provide a detailed 'Key Findings' report:\n\n{csv_content[:1000]}...",
                ),
            ]
        )  # se envian los mensajes formateados al cliente groq
        response = groq_client.invoke(prompt.format_messages()) #mensajes sigan el formato concreto
        return response.content
    except Exception as e:
        logger.error(f"Error in cybersecurity analysis: {str(e)}")
        return None


# usamos libreria reportlab y creamos fichero sencillo
# usamos un ejemplo general de los flowables que sirvan para dibujar en un lienzo
# argumentos basicos: estilo, parrafos y fichero (lienzo)
def create_findings_pdf(findings: str) -> BytesIO:
    styles = getSampleStyleSheet() #metodo mas sencillo
    content = [
        Paragraph("Cybersecurity Analysis: Key Findings", styles["Title"]),
        Paragraph(findings, styles["BodyText"]),
    ]
    pdf_buffer = BytesIO()  # almacenar el archivo temporal en el buffer 
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)  # evitamos definir manualmente las medidas
    pdf.build(content)
    pdf_buffer.seek(0) #si queremos leer el archivo desde el inicio hay que volver al principio del doc
    return pdf_buffer


# creo el token en la misma peticion en vez de almacenarlo como variable
def upload_to_app(file_object: BytesIO, filename: str, tribe_url: str, logger):
    """
    Se contruye url para obtener token acceso
    Se calcula tamaño del archivo llendo al principio y luego al final
    Ponemos los datos en el formato adecuado usando MultipartEncoder porque sino
    aparecia error de formato en la app. Documentacion API no está al dia.
    En encabezados ponemos el tipo y la longuitud
    """
    try:
        token_url = f"http://{tribe_url}/api/v1/login/access-token"
        token_data = {"username": "admin@example.com", "password": "changethis"}
        token_response = requests.post(token_url, data=token_data)
        token = token_response.json().get("access_token")
        upload_url = f"http://{tribe_url}/api/v1/uploads/"

        # Get file size
        file_object.seek(0, os.SEEK_END) #para obtener dimensiones vamos al final
        file_size = file_object.tell() #tell() nos dice la posicion final y es el tamaño en bytes del archivo
        file_object.seek(0)

        # Prepare multipart form data
        m = MultipartEncoder(
            fields={
                "name": filename,
                "description": "Cybersecurity analysis report",
                "chunk_size": "200", #se puede aumentar o disminuir 
                "chunk_overlap": "50", #lo mismo 
                "file": (filename, file_object, "application/pdf"), 
            }
        )
        # mando la solicitud como un diccionario
        headers = {
                    "Authorization": f"Bearer {token}", 
                    "Content-Type": m.content_type, 
                    "Content-Length": str(file_size)
                }

        response = requests.post(upload_url, headers=headers, data=m)

        if response.status_code != 200:
            logger.error(f"Upload failed with status {response.status_code}: {response.text}")
            return False, f"Upload failed: {response.text}"

        return True, filename
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to upload file: {str(e)}")
        return False, str(e)

@tool
def mercurio(bucket_name, file_path) -> str:
    """
    Analyzes a CSV file for cybersecurity implications, creates a PDF report, and uploads it to the app.
    Returns a JSON string containing the analysis status, file path, and any logs or errors.
    """
    # Initialize result dictionary
    result = {"status": "success", "file_path": file_path, "analysis_result": None, "logs": [], "errors": []}

    # Set up logging to capture in the result dictionary
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = DictLogHandler(result["logs"])
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Quito mensajes que no ayudan al debuggin como siguiente
    # logger.info(f"Function called with bucket_name: {bucket_name}, file_path: {file_path}")
    # pero mantengo otros que son importantes
    
    # Initialize S3 client
    s3_client = S3Client(
        access_key="0030e94285353960000000012",
        secret_key="K003HiIvvB32rxCRH4bC///m7cV1+3Q",
        endpoint_url="https://s3.eu-central-003.backblazeb2.com",
        region_name="eu-central-003",
    )
    # si el cliente falla imprimir un log
    if s3_client.client is None:
        error_message = "Error al iniciar cliente S3"
        logger.error(error_message)
        result["status"] = "error"
        result["errors"].append({"message": error_message})
        return json.dumps([result])

    # Obtener objeto y añadir log si algo falla
    file_content = s3_client.get_s3_object(bucket_name, file_path)
    if file_content is None:
        error_message = f"Failed to retrieve file from S3: {file_path}"
        logger.error(error_message)
        result["status"] = "error"
        result["errors"].append({"message": error_message})
        return json.dumps([result])

    # Perform cybersecurity analysis
    csv_content = file_content.getvalue().decode("utf-8")
    key_findings = analyze_csv_security(csv_content, logger)

    if key_findings is None:
        result["status"] = "error"
        return json.dumps([result])

    # Create PDF with findings
    pdf_buffer = create_findings_pdf(key_findings)
    filename = f"security_findings_{random.randint(1, 1000)}.pdf" # Subir el pdf no con el mismo nombre porque sino da error 
    upload_success, upload_result = upload_to_app(pdf_buffer, filename, "localhost", logger)

    if upload_success:
        # logger.info(f"File uploaded successfully: {filename}")
        result["analysis_result"] = {"uploaded_file": filename}
    else:
        result["status"] = "error"
        result["errors"].append({"message": f"Failed to upload file: {upload_result}"}) 
        return json.dumps([result])
    return json.dumps([result])

# Example usage
# bucket_name = "EWA-S3-APP-IA-UPLOAD"
# file_path = "2020-12-Huge Database Collection/Chessmate.com_findings.csv"
# result = mercurio.invoke({"bucket_name": bucket_name, "file_path": file_path})
# print(result)
