from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from app.models.schemas import PostInput, TagResponse
from app.core.security import verify_internet_secret
from app.services.tagger import generate_tags
from app.services.tag_writer import update_post_tag_error,update_post_tags
from app.utils.logger import logger
from app.models.schemas import TagRequest,PostInput


router = APIRouter()

def process_tagging(payload: TagRequest):
    try:
        post_input = PostInput(
            title=payload.title,
            description=payload.description
        )

        tags = generate_tags(post_input)
        logger.info(f"Got tags as: {tags}")

        update_post_tags(payload.post_id, tags=tags)
        logger.info("Successfully added tags")

    except Exception as e:
        logger.error(f"Tagging failed: {e}")
        update_post_tag_error(payload.post_id, str(e))


@router.get("/health")
def health():
    return {"status":"ok"}



# Just for testing of ml model purposes
@router.post("/generate-tags", response_model=TagResponse, dependencies=[Depends(verify_internet_secret)])
def generate_tags_endpoint(
    payload : PostInput,
    background_tasks: BackgroundTasks
):
    logger.info("Received tag generation request")

    try:
        tags = generate_tags(payload)
        logger.info(f"Logger generated tag as: {tags}")
        return TagResponse(tags=tags)
    except Exception as e:
        logger.error(f"Tag generation failed: {e}")
        raise HTTPException(status_code=500, detail="Tag generation failed")
    

# Trigger async tag generation + DB update
@router.post("/tag", dependencies=[Depends(verify_internet_secret)])
async def tag_post(payload: TagRequest, background_tasks: BackgroundTasks):
    logger.info(f"got post request as: {payload}")
    requestData = TagRequest(post_id=payload.post_id,title=payload.title, description=payload.description)
    background_tasks.add_task(process_tagging, requestData)
    return {"status": "accepted"}
