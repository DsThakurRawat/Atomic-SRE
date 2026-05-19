"""Configuration wizard option constants for the CLI."""

MODEL_PROVIDER_ENV = "MODEL_PROVIDER"
NOTIFICATION_PLATFORM_ENV = "NOTIFICATION_PLATFORM"
CODE_REPOSITORY_PROVIDER_ENV = "CODE_REPOSITORY_PROVIDER"
DEPLOYMENT_PLATFORM_ENV = "DEPLOYMENT_PLATFORM"
LOGGING_PLATFORM_ENV = "LOGGING_PLATFORM"
LEGACY_SELECTION_ENV_KEYS: tuple[str, ...] = (
    MODEL_PROVIDER_ENV,
    NOTIFICATION_PLATFORM_ENV,
    CODE_REPOSITORY_PROVIDER_ENV,
    DEPLOYMENT_PLATFORM_ENV,
    LOGGING_PLATFORM_ENV,
)

MODEL_PROVIDER_ANTHROPIC = "anthropic"
MODEL_PROVIDER_GROQ = "groq"
MODEL_PROVIDER_OLLAMA = "ollama"
MODEL_PROVIDER_OPENAI = "openai"
MODEL_PROVIDER_GEMINI = "gemini"
MODEL_PROVIDER_OPENROUTER = "openrouter"
MODEL_PROVIDER_BEDROCK = "bedrock"

NOTIFICATION_PLATFORM_SLACK = "slack"
CODE_REPOSITORY_PROVIDER_GITHUB = "github"
DEPLOYMENT_PLATFORM_AWS = "aws"
LOGGING_PLATFORM_CLOUDWATCH = "cloudwatch"

MODEL_PROVIDER_CHOICES: tuple[tuple[str, str], ...] = (
    ("Anthropic", MODEL_PROVIDER_ANTHROPIC),
    ("Groq", MODEL_PROVIDER_GROQ),
    ("Ollama", MODEL_PROVIDER_OLLAMA),
    ("OpenAI", MODEL_PROVIDER_OPENAI),
    ("Google Gemini", MODEL_PROVIDER_GEMINI),
    ("OpenRouter", MODEL_PROVIDER_OPENROUTER),
    ("Amazon Bedrock", MODEL_PROVIDER_BEDROCK),
)

MODEL_CHOICES_ANTHROPIC: tuple[tuple[str, str], ...] = (
    ("Claude 3.5 Sonnet", "anthropic:claude-3-5-sonnet-20241022"),
    ("Claude 3.5 Haiku", "anthropic:claude-3-5-haiku-20241022"),
    ("Claude 3 Opus", "anthropic:claude-3-opus-20240229"),
)

MODEL_CHOICES_GROQ: tuple[tuple[str, str], ...] = (
    ("Llama 3.3 70B (Versatile)", "groq:llama-3.3-70b-versatile"),
    ("Llama 3.1 70B (Versatile)", "groq:llama-3.1-70b-versatile"),
    ("Llama 3.1 8B (Instant)", "groq:llama-3.1-8b-instant"),
    ("Mixtral 8x7B", "groq:mixtral-8x7b-32768"),
)

MODEL_CHOICES_OPENAI: tuple[tuple[str, str], ...] = (
    ("GPT-4o", "openai:gpt-4o"),
    ("GPT-4o mini", "openai:gpt-4o-mini"),
    ("o1-preview", "openai:o1-preview"),
)

MODEL_CHOICES_GEMINI: tuple[tuple[str, str], ...] = (
    ("Gemini 1.5 Pro", "google-gla:gemini-1.5-pro"),
    ("Gemini 1.5 Flash", "google-gla:gemini-1.5-flash"),
)

NOTIFICATION_PLATFORM_CHOICES: tuple[tuple[str, str], ...] = (
    ("Slack", NOTIFICATION_PLATFORM_SLACK),
)
CODE_REPOSITORY_PROVIDER_CHOICES: tuple[tuple[str, str], ...] = (
    ("GitHub", CODE_REPOSITORY_PROVIDER_GITHUB),
)
DEPLOYMENT_PLATFORM_CHOICES: tuple[tuple[str, str], ...] = (("AWS", DEPLOYMENT_PLATFORM_AWS),)
AWS_LOGGING_PLATFORM_CHOICES: tuple[tuple[str, str], ...] = (
    ("CloudWatch", LOGGING_PLATFORM_CLOUDWATCH),
)
