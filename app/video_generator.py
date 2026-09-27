import uuid
import base64
import logging
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

# Hardcoded constants as required
BUCKET_NAME = "greenhouse-inventory-assets-qwiklabs-gcp-03-4796b5681dc3"
PROJECT_ID = "qwiklabs-gcp-03-4796b5681dc3"
MODEL_NAME = "gemini-omni-flash-preview"
LOCATION = "global"

def generate_plant_video(prompt: str, tool_context: ToolContext) -> str:
    """Generates a short AI video for a greenhouse plant or item, saves it to Playground Artifacts, and uploads to public Cloud Storage.

    Args:
        prompt: Description of the plant item or scene to generate as a video (e.g. 'a healthy Monstera plant swaying in a greenhouse breeze').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        The public HTTPS URL of the uploaded video on Cloud Storage.
    """
    try:
        # Initialize Gemini Client for global region with vertexai=True
        client = genai.Client(vertexai=True, location=LOCATION)
        
        # Generate video using gemini-omni-flash-preview via Interactions API
        res = client.interactions.create(
            model=MODEL_NAME,
            input=f"Generate a short video of {prompt}",
            response_modalities=["text", "video"]
        )
        
        # Safely extract video bytes from interaction steps
        video_bytes = None
        for step in getattr(res, "steps", []) or []:
            try:
                step_dict = step.model_dump()
            except Exception:
                step_dict = {}
                
            contents = step_dict.get("content", [])
            if not isinstance(contents, list):
                contents = [contents]
                
            for item in contents:
                if isinstance(item, dict):
                    b64_data = item.get("bytes_base64_encoded") or item.get("data")
                    if b64_data:
                        if isinstance(b64_data, bytes):
                            video_bytes = b64_data
                        elif isinstance(b64_data, str):
                            video_bytes = base64.b64decode(b64_data)
                        break
            if video_bytes:
                break
                
        if not video_bytes:
            return "Error: Failed to generate video bytes from gemini-omni-flash-preview model."
            
        filename = f"plant_video_{uuid.uuid4().hex[:8]}.mp4"
        
        # 1. Save artifact with tool_context.save_artifact so it shows up in Playground Artifacts
        try:
            artifact_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
            tool_context.save_artifact(filename, artifact_part)
            logger.info(f"Saved video artifact {filename} to ToolContext.")
        except Exception as e:
            logger.warning(f"Failed to save video artifact in ToolContext: {e}")
            
        # 2. Upload video bytes to public Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(video_bytes, content_type="video/mp4")
        
        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
        return f"Successfully generated plant video! Public URL: {public_url}"
        
    except Exception as e:
        logger.error(f"Video generation tool error: {e}")
        return f"Error generating plant video: {str(e)}"
