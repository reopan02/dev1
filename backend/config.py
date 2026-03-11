from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, computed_field, Field, AliasChoices


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Analyze model config
    gemini_analyze_api_key: SecretStr = Field(
        validation_alias=AliasChoices("gemini_analyze_api_key", "GEMINI_ANALYZE_API_KEY")
    )
    gemini_analyze_base_url: str = Field(
        default="https://yunwu.ai",
        validation_alias=AliasChoices("gemini_analyze_base_url", "GEMINI_ANALYZE_BASE_URL")
    )
    llm_model: str = Field(
        default="gemini-2.5-pro",
        validation_alias=AliasChoices("llm_model", "GEMINI_ANALYZE_MODEL", "gemini_analyze_model")
    )

    # Image model config
    gemini_image_api_key: SecretStr = Field(
        validation_alias=AliasChoices("gemini_image_api_key", "GEMINI_IMAGE_API_KEY")
    )
    gemini_image_base_url: str = Field(
        default="https://yunwu.ai",
        validation_alias=AliasChoices("gemini_image_base_url", "GEMINI_IMAGE_BASE_URL")
    )
    image_model: str = Field(
        default="gemini-3-pro-image-preview",
        validation_alias=AliasChoices("image_model", "GEMINI_IMAGE_MODEL", "gemini_image_model")
    )

    # Temperature config
    llm_temperature: float = 0.7
    llm_recognize_temperature: float = 0.3

    # Timeout (seconds)
    llm_timeout: int = 180

    @computed_field
    @property
    def analyze_openai_base_url(self) -> str:
        """Append /v1 to analyze base URL for OpenAI-compatible ChatOpenAI"""
        return f"{self.gemini_analyze_base_url}/v1"


def get_settings() -> Settings:
    return Settings()
