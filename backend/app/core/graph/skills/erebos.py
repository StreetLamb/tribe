from typing import Annotated
from langchain_core.tools import tool
import requests
import logging
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
import json
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from requests_toolbelt import MultipartEncoder
import os
import random
from app.core.graph.skills.hermes import DateTimeEncoder, DictLogHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)  # Testear si quito esto que se va a imprimir en pantalla

# Initialize Groq client
groq_client = ChatGroq(api_key="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", model_name="llama3-8b-8192")


def check_email_breach(email: str) -> Dict[str, Any]:
    url = f"https://api.xposedornot.com/v1/breach-analytics?email={email}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "success",
                "message": f"Successfully retrieved breach analytics for {email}.",
                "data": data,
            }
        return {
            "status": "error",
            "message": f"An error occurred while checking the email. Status code: {response.status_code}",
        }
    except requests.RequestException as e:
        logger.error(f"Error checking email breach: {str(e)}")
        return {"status": "error", "message": f"An error occurred while making the request: {str(e)}"}


def truncate_data(
    data: str, max_length: int = 4000
) -> str:  # lo he tenido que añadir porque los resultados son demasiado amplios
    """Truncate the data to a maximum length."""
    if len(data) > max_length:
        return data[:max_length] + "... (truncated)"
    else:
        return data


def summarize_breach_data(data: Dict[str, Any]) -> str:
    prompt = ChatPromptTemplate.from_template(  # tengo que añadir esa clase para añadir todos esos mensajes
        "Summarize the key insights from this breach data: {data}"
        "\nFocus on the most important information such as:"
        "\n- Number of breaches"
        "\n- Types of data exposed"
        "\n- Severity of breaches"
        "\n- Any notable or large-scale breaches"
        "\nProvide a concise summary in 3-5 bullet points."
        "\nStart the summary with 'Here is a summary of the breach data in 3-5 bullet points:'"
    )

    truncated_data = truncate_data(str(data))

    try:
        summary_chain = prompt | groq_client  # a partir de 3.9 une diccionarios
        content = summary_chain.invoke(
            {"data": truncated_data}
        )  # toma los datos como entrada y almacenamos los datos en content
        return content
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return f"Unable to generate summary due to an error: {str(e)}"


def get_breaches_summary(data: Dict[str, Any]) -> str:
    """Extract a list of breaches from the data and format as a comma-separated string."""
    breaches = []
    if (
        "ExposedBreaches" in data and "breaches_details" in data["ExposedBreaches"]
    ):  # es un diccionario con key:stry value:lista y los elementos de la lista es un diccionario con varios key-value
        for breach in data["ExposedBreaches"]["breaches_details"]:
            if isinstance(breach, dict) and "breach" in breach:
                breaches.append(breach["breach"])  # la manera mas rapida es almacenar resultados en lista
    return ", ".join(breaches)


def create_findings_pdf(summary: str, breaches_list: str) -> BytesIO:
    pdf_buffer = BytesIO()
    pdf = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    content = [
        Paragraph("Email Breach Analysis Report", styles["Title"]),
        Paragraph("Summary:", styles["Heading2"]),
        Paragraph(summary, styles["BodyText"]),
        Paragraph("List of Breaches:", styles["Heading2"]),
        Paragraph(breaches_list, styles["BodyText"]),
    ]
    pdf.build(content)
    pdf_buffer.seek(0)
    return pdf_buffer


# quizas podria importarla desde mercurio pero tendria que cambiar el nombre que le pongo a los archivos
def upload_to_app(file_object: BytesIO, filename: str, tribe_url: str, logger):
    try:
        token_url = f"http://{tribe_url}/api/v1/login/access-token"
        token_data = {"username": "admin@example.com", "password": "changethis"}
        token_response = requests.post(token_url, data=token_data)
        token = token_response.json().get("access_token")

        upload_url = f"http://{tribe_url}/api/v1/uploads/"
        headers = {"Authorization": f"Bearer {token}"}

        file_object.seek(0, os.SEEK_END)
        file_size = file_object.tell()
        file_object.seek(0)

        m = MultipartEncoder(
            fields={
                "name": filename,
                "description": "Email breach analysis report",
                "chunk_size": "200",
                "chunk_overlap": "50",
                "file": (filename, file_object, "application/pdf"),
            }
        )

        headers = {"Authorization": f"Bearer {token}", "Content-Type": m.content_type, "Content-Length": str(file_size)}
        response = requests.post(upload_url, headers=headers, data=m)

        if response.status_code != 200:
            logger.error(f"Upload failed with status {response.status_code}: {response.text}")
            return False, f"Upload failed: {response.text}"

        return True, filename
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to upload file: {str(e)}")
        return False, str(e)


@tool
def erebos(email: Annotated[str, "Email address to check for breaches"]) -> str:
    """
    Checks if an email address has been involved in any known data breaches, provides a summary of key insights,
    creates a PDF report, and uploads it to the app. Returns a JSON string containing the email, breach summary,
    list of breaches, upload status, and any logs or errors.
    """
    result = {
        "status": "success",
        "checked_email": email,
        "summary": None,
        "breaches_list": None,
        "upload_result": None,
        "logs": [],
        "errors": [],
    }

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = DictLogHandler(result["logs"])
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info(f"Function called with email: {email}")

    try:
        breach_data = check_email_breach(email)

        if breach_data["status"] == "success":
            result["summary"] = summarize_breach_data(breach_data["data"])
            result["breaches_list"] = get_breaches_summary(breach_data["data"])
            logger.info(f"Breach data retrieved and summarized for email: {email}")

            # Create PDF report
            pdf_buffer = create_findings_pdf(result["summary"], result["breaches_list"])

            # Upload PDF to app
            filename = f"email_breach_report_{random.randint(1, 1000)}.pdf"
            upload_success, upload_result = upload_to_app(pdf_buffer, filename, "localhost", logger)

            if upload_success:
                logger.info(f"File uploaded successfully: {filename}")
                result["upload_result"] = {"uploaded_file": filename}
            else:
                result["status"] = "warning"
                result["errors"].append({"message": f"Failed to upload file: {upload_result}"})
        else:
            error_message = f"Failed to retrieve breach data for email: {email}"
            logger.error(error_message)
            result["status"] = "error"
            result["errors"].append({"message": error_message})

    except Exception as e:
        error_message = f"An error occurred while processing the request: {str(e)}"
        logger.error(error_message)
        result["status"] = "error"
        result["errors"].append({"message": error_message})

    logger.removeHandler(handler)

    return json.dumps([result], cls=DateTimeEncoder)

    # Example usage
    # if __name__ == "__main__":
    test_email = "petrunichev86@mail.ru"
    result = erebos.invoke({"email": test_email})
    print(result)
