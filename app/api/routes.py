from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends

from app.models.schemas import PostInput, TagResponse
from app.core.security import verify_internet_secret
from app.services.tagger import generate_tags
from app.services.tag_writer import update_post_tag_error,update_post_tags
from app.services.quality_estimator import update_post_score
from app.utils.logger import logger
from app.models.schemas import TagRequest,PostInput,PostRequest

from ml.pipelines.post_quality_feature.inference_pipeline import InferencePipeline
from ml.config.post_quality_feature.configuration import ConfigurationManager

router = APIRouter()

def process_tagging(payload: TagRequest):
    try:
        post_input = PostInput(
            title=payload.title,
            description=payload.description
        )

        result = generate_tags(post_input)
        tags = result["tags"]
        error = result["error"]

        logger.info(f"Tagging result: tags={tags}, error={error}")

        if error:
            update_post_tag_error(payload.post_id, error)
            logger.info("Stored tag error")
        else:
            update_post_tags(payload.post_id, tags)
            logger.info("Successfully added tags")

    except Exception as e:
        logger.error(f"Tagging failed: {e}")
        update_post_tag_error(payload.post_id, "internal_error")


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
        data = generate_tags(payload)
        tags = data["tags"]
        error = data["error"]
        logger.info(f"Logger generated tag as: {tags}")
        return TagResponse(tags=tags,error=error)
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


## Getting post quality
@router.post("/post-quality", dependencies=[Depends(verify_internet_secret)])
def check_post_quality(request: PostRequest):
    try:
        configs = ConfigurationManager()
        inference = InferencePipeline(config=configs.get_inference_config())

        result = inference.predict(request.title,request.body)

        post_quality = result["score"]

        logger.info(f"Post quality result: {result}")

        # Update database score
        update_post_score(
            post_id=request.postId,
            post_quality=post_quality,
            karma=request.karma
        )

        return {"status":200,"result":result}
    
    except Exception as e:
        logger.error(f"Post quality inference failed: {e}")
        raise HTTPException(status_code=500, detail = "Post quality failed")

    
