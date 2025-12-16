from app.models.schemas import PostInput
from app.utils.logger import logger

def generate_tags(post: PostInput):
    logger.info("Running fake ML Trigger")

    text = f"{post.title} {post.description or ''}".lower()

    tags = []

    if "ai" in text or "ml" in text:
        tags.append("machine-learning")
    if "nextjs" in text or "react" in text:
        tags.append("frontend")
    if "fastapi" in text or "backend" in text:
        tags.append("backend")

    if not tags:
        tags.append("general")

    return tags[:3]
