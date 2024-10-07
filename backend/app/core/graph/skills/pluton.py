from typing import Annotated
from langchain_core.tools import tool
import boto3
from botocore.client import Config
import re
import logging
from typing import Dict, Any, List
import json
from datetime import datetime
from io import StringIO  # nuevo
import csv

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DictLogHandler(logging.Handler):  # submodulo que manda los informes de log a el destino correcto
    def __init__(self, log_list):
        super().__init__()  # accedemos al constructor
        self.log_list = log_list  # almacenamos referencia a la lista de logs

    def emit(self, record):
        log_entry = {"level": record.levelname, "message": self.format(record)}  # sintaxis diccionario
        self.log_list.append(log_entry)  # añadimos a log list las log entry


# empezamos con numero y output es true/false
def luhn(number: str) -> bool:
    """
    Implementation of the Luhn algorithm for checking credit card validity
    """
    digits = [int(d) for d in str(number) if d.isdigit()]
    # convertimos numero en cadena texto
    # metodo comprension de listas para cojer letras

    for i in range(len(digits) - 2, -1, -2):  # empieza en numero 8, para en numero posicion 0 y se salta 2
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10 == 0  #modulo de la suma es 0 que es mas facil comprobar si son multiplos de 10


# la funcion devuelve un diccionario con si tarjeta es valida y el tipo de tarjeta
class CardChecker:
    def validate_cc(self, number: str) -> Dict[str, Any]:  # any porque no hay formato concreto
        if not number.isdigit() or len(number) < 13 or len(number) > 19:
            return {"is_valid": False, "card_type": "UNKNOWN"}

        if not luhn(number):
            return {"is_valid": False, "card_type": "UNKNOWN"}

        if re.match(r"^4", number):  # digit "4" is the start of the string
            return {"is_valid": True, "card_type": "VISA"}
        elif re.match(r"^5[1-5]", number):
            return {"is_valid": True, "card_type": "MASTERCARD"}
        elif re.match(r"^3[47]", number):
            return {"is_valid": True, "card_type": "AMEX"}
        elif re.match(r"^6(?:011|5)", number):
            return {"is_valid": True, "card_type": "DISCOVER"}
        else:
            return {"is_valid": True, "card_type": "UNKNOWN"}


# creamos cliente y se añade manejo de excepciones
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
            logger.error(f"Failed to create S3 client: {str(e)}")  # más rapido: print str(e)
            return None  # ya imprimi un mensaje

    # ejemplo usa 'Key' nombre del objecto pero eso tarda demasiado nosotros usaremos ruta del archivo
    def get_object(self, bucket_name: str, file_path: str) -> Dict[str, Any]:
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=file_path)
            return {
                "content": response["Body"].read(),  # imprime el fichero
                "metadata": response.get("Metadata", {}),  # si no hay nos da diccionario vacio
                "content_type": response.get("ContentType", ""),  # si no hay dar cadena vacia
            }
        except self.client.exceptions.ClientError as e:
            logger.error(f"Error getting object {file_path} from bucket {bucket_name}. {e}")
            return None


# se crean 3 funciones: buscar CSV, buscar coincidencias dentro del texto, comprobar coincidencias
# vamos a usar lista de diccionarios y cada diccioario es un registro
# comprobar que los nombres de los archivos son validos Unicode
def search_content(content: bytes, full_number: str, content_type: str = "text") -> List[Dict[str, Any]]:
    """
    Busca coincidencias del número de tarjeta de crédito en un archivo CSV o texto.
    :param content: El contenido del archivo en bytes.
    :param full_number: El número de tarjeta de crédito completo que buscamos.
    :param content_type: El tipo de contenido ('csv' o 'text').
    :return: Lista de diccionarios con las coincidencias encontradas.
    """
    matches = []
    content_str = content.decode("utf-8", errors="replace")

    if content_type == "csv":
        csv_file = StringIO(content_str)  # modulo IO nos permite trabajar con el fichero en memoria
        csv_reader = csv.reader(csv_file)  # con esto evitamos usar librerias como os.path o magic

        for row_num, row in enumerate(csv_reader, start=2):
            for col_num, value in enumerate(row, start=1):
                if is_valid_cc_match(value, full_number):
                    matches.append(
                        {
                            "row": row_num,
                            "column": col_num,
                            "value": f"****{value[-4:]}",  # Enmascarar número de tarjeta
                        }
                    )
    else:  # Asume que es texto si no es CSV
        for line_num, line in enumerate(content_str.split("\n"), start=1):
            if is_valid_cc_match(line, full_number):
                matches.append(
                    {
                        "line": line_num,
                        "content": re.sub(r"\b\d{13,19}\b", lambda m: f"****{m.group(0)[-4:]}", line.strip()),
                    }
                )

    return matches


def is_valid_cc_match(text: str, full_number: str) -> bool:
    # Use regex to find potential credit card numbers
    cc_pattern = r"\b\d{13,19}\b"
    potential_numbers = re.findall(cc_pattern, text)
    return any(num == full_number for num in potential_numbers)


# decorador tool para definir herramienta personalizada
# tenemos que usar credenciales
# comprobar si hay archivo similar usando get_object

# he eliminado full_number: Annotated[str, "Full credit card number"],bucket_name: Annotated[str, "S3 bucket name"],file_path: Annotated[str, "Path to the file in S3"],
@tool
def pluton(full_number, bucket_name, file_path) -> str:
    """
    Validates a partial credit card number and searches for it in an S3 file.
    Returns a JSON string containing the validation result, search results, and any logs or errors.
    """
    # Iniciamos valores diccionario
    result = {
        #"status": "success",
        #"file_path": file_path,
        #"is_valid": False,
        "card_type": "UNKNOWN",
        "s3_content_search_result": None,
        "logs": [],
        "errors": [],
    }

    # Crear un logging para capturar resultados diccionario
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = DictLogHandler(result["logs"])
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

        # Iniciamos cliente dentro de la tool porque sino no son validas las credenciales
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
        return json.dumps([result])

    # Validate full credit card
    card_checker = CardChecker()
    validation_result = card_checker.validate_cc(full_number)
    result["is_valid"] = validation_result["is_valid"]
    result["card_type"] = validation_result["card_type"]

    if not result["is_valid"]:
        result["errors"].append({"message": "Invalid credit card number"})
        return json.dumps([result])

    # Search S3 content
    s3_object = s3_client.get_object(bucket_name, file_path)
    if s3_object is None:
        error_message = f"Failed to retrieve file from S3: {file_path}"
        logger.error(error_message)
        result["status"] = "error"
        result["errors"].append({"message": error_message})
        return json.dumps([result])

    content = s3_object["content"]
    content_type = s3_object["content_type"]
    matches = search_content(content, full_number, content_type)

    result["s3_content_search_result"] = {
        "status": "success",
        "file_path": file_path,
        "matches": matches,
    }
    return json.dumps([result])

# Example usage
#bucket_name = "EWA-S3-APP-IA-UPLOAD"
#file_path = "results_money/2022-06-13-Dropbox_9.8m/Dropbox_9.8m_mail_pass.txt_money.csv"
#full_number = "5105105105105100"
#result = pluton.invoke({"full_number": full_number, "bucket_name": bucket_name, "file_path": file_path})
#print(result)
