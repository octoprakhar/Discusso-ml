import os
from fastapi import Header, HTTPException
from app.core.config import settings
from app.utils.logger import logger

def verify_internet_secret(x_internal_secret: str = Header(...)):
    # logger.info(f"Got my logger server key as : {settings.ML_INTERNAL_SECRET}")
    # logger.info(f"Got key from request is {x_internal_secret}")
    if x_internal_secret != settings.ML_INTERNAL_SECRET:
        
        raise HTTPException(
            status_code=403,
            detail="Forbidden: invalid internal seret"
        )