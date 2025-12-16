from app.core.supabase import supabase
from app.utils.logger import logger

def update_post_tags(post_id: str, tags: list[str]):
    tag_string = ",".join(tags)

    supabase.table("Post").update({
        "tag":tag_string,
        "tag_error": None
    }).eq("id",post_id).execute()

def update_post_tag_error(post_id: str, error: str):
    supabase.table("Post").update({
        "tag_error": error
    }).eq("id",post_id).execute()