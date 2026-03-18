from app.core.supabase import supabase
from app.utils.logger import logger
import math

def compute_post_score(post_quality:float, karma: int) ->float:
    """
    post_score = post_quality + tanh(karma)

    post_quality: [0,3]
    karma: (-inf, +inf)
    """

    try:
        karma_component = math.tanh(float(karma))
        score = post_quality + karma_component
        return score
    except Exception as e:
        logger.error(f"Score computation failed: {e}")
        return post_quality
    

def update_post_score(post_id: str, post_quality: float, karma:int):
    """
    Computes final score and stores it in database
    """

    score = compute_post_score(post_quality=post_quality,karma=karma)

    try:
        supabase.table("Post").update({
            "post_score": score
        }).eq("id", post_id).execute()

        logger.info(f"Post score updated: {post_id} -> {score}")

    except Exception as e:
        logger.error(f"Failed to update post score: {e}")

