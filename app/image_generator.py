import uuid
import logging
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

# Hardcoded constants as required
BUCKET_NAME = "greenhouse-inventory-assets-qwiklabs-gcp-03-4796b5681dc3"
PROJECT_ID = "qwiklabs-gcp-03-4796b5681dc3"
MODEL_NAME = "gemini-3.1-flash-lite-image"
LOCATION = "global"

def generate_plant_image(prompt: str, tool_context: ToolContext) -> str:
    """Generates an AI image for a plant item, saves it to Playground Artifacts, and uploads to public Cloud Storage.

    Args:
        prompt: Description of the plant item to generate (e.g. 'a healthy Monstera Deliciosa in a terracotta pot').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        The public HTTPS URL of the uploaded image on Cloud Storage.
    """
    try:
        # Initialize Gemini Client for global region
        client = genai.Client(vertexai=True, location=LOCATION)
        
        # Generate image using gemini-3.1-flash-lite-image
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"Generate an image of {prompt}",
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"]
            )
        )
        
        # Extract image bytes
        image_bytes = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    break
                    
        if not image_bytes:
            return "Error: Failed to generate image bytes from Gemini model."
            
        filename = f"plant_{uuid.uuid4().hex[:8]}.jpg"
        
        # 1. Save artifact for Playground Artifacts panel
        try:
            artifact_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            tool_context.save_artifact(filename, artifact_part)
            logger.info(f"Saved artifact {filename} to ToolContext.")
        except Exception as e:
            logger.warning(f"Failed to save artifact in ToolContext: {e}")
            
        # 2. Upload image bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(image_bytes, content_type="image/jpeg")
        
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return f"Successfully generated plant image! Public URL: {public_url}"
        
    except Exception as e:
        logger.error(f"Image generation tool error: {e}")
        return f"Error generating plant image: {str(e)}"
