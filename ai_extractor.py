import base64
import json
import os

from dotenv import load_dotenv
from openai import OpenAI


# Load local development configuration.
load_dotenv()


def extract_label_data(uploaded_file):
    """
    Send uploaded alcohol label artwork to the AI model and extract
    structured label information.

    The AI performs visual extraction only. Final comparison and
    compliance decisions remain deterministic application logic
    and reviewer responsibilities.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    if not model:
        raise RuntimeError("OPENAI_MODEL is not configured.")

    client = OpenAI(api_key=api_key)

    # Read the uploaded image and convert it to a base64 data URL.
    image_bytes = uploaded_file.getvalue()
    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    mime_type = uploaded_file.type or "image/jpeg"

    image_data_url = (
        f"data:{mime_type};base64,{encoded_image}"
    )

    extraction_prompt = """
You are analyzing alcohol beverage label artwork.

Extract only information that is visibly present in the supplied image.
Do not infer missing information.
Do not invent values.
Do not use outside knowledge to fill gaps.

Extract:

1. Brand name
2. Class or type of alcoholic beverage
3. Alcohol content, including ABV or proof when visible
4. Net contents
5. Bottler, producer, distiller, winery, brewery, or importer name
6. Bottler, producer, distiller, winery, brewery, or importer address
7. Country of origin when visible
8. Full Government Health Warning text when visible
9. Whether a Government Health Warning is visibly present

If a text field cannot be identified, return an empty string.

The purpose of this step is information extraction only.
Do not approve or reject the label.
"""

    response = client.responses.create(
        model=model,
        reasoning={"effort": "none"},
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": extraction_prompt
                    },
                    {
                        "type": "input_image",
                        "image_url": image_data_url,
                        "detail": "high"
                    }
                ]
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "alcohol_label_extraction",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "brand_name": {
                            "type": "string"
                        },
                        "class_type": {
                            "type": "string"
                        },
                        "alcohol_content": {
                            "type": "string"
                        },
                        "net_contents": {
                            "type": "string"
                        },
                        "producer_name": {
                            "type": "string"
                        },
                        "producer_address": {
                            "type": "string"
                        },
                        "country_of_origin": {
                            "type": "string"
                        },
                        "government_warning_text": {
                            "type": "string"
                        },
                        "government_warning_found": {
                            "type": "boolean"
                        }
                    },
                    "required": [
                        "brand_name",
                        "class_type",
                        "alcohol_content",
                        "net_contents",
                        "producer_name",
                        "producer_address",
                        "country_of_origin",
                        "government_warning_text",
                        "government_warning_found"
                    ],
                    "additionalProperties": False
                }
            }
        }
    )

    return json.loads(response.output_text)