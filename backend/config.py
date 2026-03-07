from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, computed_field, Field, AliasChoices


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # LLM API config
    yunwu_base_url: str = "https://yunwu.ai"
    gemini_api_key: SecretStr = Field(
        validation_alias=AliasChoices("gemini_api_key", "GEMINI_API_KEY")
    )

    # Model config
    llm_model: str = Field(
        default="gemini-2.5-pro",
        validation_alias=AliasChoices("llm_model", "GEMINI_ANALYZE_MODEL", "gemini_analyze_model")
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
    def openai_base_url(self) -> str:
        """Append /v1 to base URL for OpenAI-compatible ChatOpenAI"""
        return f"{self.yunwu_base_url}/v1"


def get_settings() -> Settings:
    return Settings()
