from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App settings
    app_name: str = "ML Document Processing API"
    debug: bool = False
    secret_key: str = "super-secret-key-change-in-production"
    
    # Granite AI settings
    granite_api_key: Optional[str] = None
    granite_api_url: str = "https://granite-api.ibm.com"
    
    # Pinecone settings
    pinecone_api_key: Optional[str] = None
    pinecone_environment: str = "us-west1-gcp"
    pinecone_index_name: str = "ml-documents"
    
    # Redis settings
    redis_url: str = "redis://localhost:6379"
    
    # AWS settings
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_bucket_name: str = "ml-app-uploads"
    
    # Auth0 settings
    auth0_domain: Optional[str] = None
    auth0_client_id: Optional[str] = None
    auth0_client_secret: Optional[str] = None
    
    # File upload settings
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"


settings = Settings()