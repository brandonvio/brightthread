"""Prompt service for loading and managing prompt templates.

This module provides functionality for loading YAML-based prompt templates,
replacing placeholders with parameters, and listing available prompts.

Example YAML structure for prompts:
    name: simple-branch-mr
    description: Clone repo, create a new branch, make changes, and open a merge request
    instructions:
      - "Clone the repository at `{git_repo_url}` to the `{working_dir}` folder"
      - "Checkout the `integration` branch"
      - "Create a branch called `{branch_name}`"

Example usage:
    from pathlib import Path
    from services.prompt_service import PromptService

    # Initialize service
    prompts_dir = Path("prompts/main")
    service = PromptService(prompts_dir=prompts_dir)

    # List all available prompts
    prompts = service.list_prompts()
    # Returns: [PromptSummary(name="simple-branch-mr", description="...")]

    # Load a prompt with parameters
    prompt_text = service.load_prompt(
        "simple-branch-mr",
        git_repo_url="https://github.com/user/repo.git",
        working_dir="/tmp/work",
        branch_name="feature-123"
    )
    # Returns: "Clone the repository at `https://github.com/user/repo.git`..."

    # Get placeholders for a prompt
    placeholders = service.get_prompt_placeholders("simple-branch-mr")
    # Returns: {"git_repo_url", "working_dir", "branch_name"}
"""

import re
import yaml
from pathlib import Path
from pydantic import BaseModel, Field


class PromptSummary(BaseModel):
    """Summary information for a prompt template.

    Attributes:
        name: The name identifier for the prompt
        description: Brief description of what the prompt does

    Example:
        summary = PromptSummary(
            name="simple-branch-mr",
            description="Clone repo, create a new branch, make changes, and open a merge request"
        )
    """

    name: str = Field(..., description="Name identifier for the prompt")
    description: str = Field(..., description="Description of the prompt")


class PromptConfig(BaseModel):
    """Pydantic model for prompt configuration.

    Attributes:
        name: The name identifier for the prompt
        description: Brief description of what the prompt does
        instructions: List of instruction strings with optional placeholders
        output_type: Optional output type hint (e.g., "json" for structured output)

    Example:
        config = PromptConfig(
            name="simple-branch-mr",
            description="Clone repo and create MR",
            instructions=["Clone {repo}", "Create branch {name}"]
        )
    """

    name: str = Field(..., description="Name identifier for the prompt")
    description: str = Field(..., description="Description of the prompt")
    instructions: list[str] = Field(..., description="List of instruction strings")
    output_type: str | None = Field(
        default=None,
        description="Output type hint (e.g., 'json' for structured output)",
    )


# Wrapper instruction for JSON output prompts
JSON_OUTPUT_WRAPPER = (
    "CRITICAL: Your response must be ONLY valid JSON. "
    "Do NOT include markdown code blocks (```), explanations, or any other text. "
    "Output the raw JSON object directly."
)


class PromptService:
    """Service for loading and managing prompt templates.

    This service handles loading YAML-based prompt templates from the prompts/main
    directory and replacing placeholders with provided parameters.
    """

    def __init__(self, prompts_dir: Path) -> None:
        """Initialize the prompt service.

        Args:
            prompts_dir: Path to the directory containing prompt YAML files
        """
        self.prompts_dir = prompts_dir

    def list_prompts(self) -> list[PromptSummary]:
        """List all available prompts in the prompts directory.

        Returns:
            List of PromptSummary models containing name and description for each prompt

        Example:
            service = PromptService(Path("prompts/main"))
            prompts = service.list_prompts()
            # [PromptSummary(name="simple-branch-mr", description="Clone repo..."),
            #  PromptSummary(name="generate-regression-test", description="Generate...")]
        """
        prompts: list[PromptSummary] = []

        for yaml_file in self.prompts_dir.glob("*.yml"):
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                prompts.append(
                    PromptSummary(name=data["name"], description=data["description"])
                )

        return prompts

    def load_prompt(self, prompt_name: str, **params: str) -> str:
        """Load a prompt template and replace placeholders with parameters.

        Args:
            prompt_name: Name of the prompt file (without .yml extension)
            **params: Keyword arguments for placeholder replacement

        Returns:
            Formatted prompt string with all placeholders replaced

        Raises:
            FileNotFoundError: If the prompt file does not exist
            KeyError: If required placeholders are not provided in params

        Example:
            service = PromptService(Path("prompts/main"))
            prompt = service.load_prompt(
                "simple-branch-mr",
                git_repo_url="https://github.com/user/repo.git",
                working_dir="/tmp/work",
                branch_name="feature-123",
                now="2025-12-02 13:00:00"
            )
            # Returns: "Clone the repository at `https://github.com/user/repo.git`
            # to the `/tmp/work` folder Checkout the `integration` branch..."
        """
        yaml_file = self.prompts_dir / f"{prompt_name}.yml"

        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        prompt_config = PromptConfig(**data)

        formatted_instructions: list[str] = []
        for instruction in prompt_config.instructions:
            formatted_instructions.append(instruction.format(**params))

        return " ".join(formatted_instructions)

    def get_prompt_placeholders(self, prompt_name: str) -> set[str]:
        """Extract all unique placeholders from a prompt template.

        Args:
            prompt_name: Name of the prompt file (without .yml extension)

        Returns:
            Set of placeholder names (without braces)

        Raises:
            FileNotFoundError: If the prompt file does not exist

        Example:
            service = PromptService(Path("prompts/main"))
            placeholders = service.get_prompt_placeholders("simple-branch-mr")
            # Returns: {"git_repo_url", "working_dir", "branch_name", "now"}
        """
        yaml_file = self.prompts_dir / f"{prompt_name}.yml"

        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        prompt_config = PromptConfig(**data)

        placeholders: set[str] = set()
        placeholder_pattern = re.compile(r"\{(\w+)\}")

        for instruction in prompt_config.instructions:
            matches = placeholder_pattern.findall(instruction)
            placeholders.update(matches)

        return placeholders

    def load_system_prompt(self, prompt_name: str) -> str:
        """Load a system prompt from YAML file and return joined instructions.

        If the prompt has output_type: json, automatically appends a wrapper
        instruction to enforce clean JSON output (no markdown, no explanations).

        Args:
            prompt_name: Name of the prompt file (without .yml extension)

        Returns:
            Joined instructions as a single string

        Raises:
            FileNotFoundError: If the prompt file does not exist
            KeyError: If the 'instructions' field is not in the YAML file

        Example:
            service = PromptService(Path("prompts/agent-system"))
            prompt_text = service.load_system_prompt("analysis-agent")
            # Returns: "Use the vector search tool... Generate a well formatted..."
        """
        yaml_file = self.prompts_dir / f"{prompt_name}.yml"

        with open(yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        prompt_config = PromptConfig(**data)
        base_prompt = " ".join(prompt_config.instructions)

        # Add JSON wrapper for structured output prompts
        if prompt_config.output_type == "json":
            return f"{base_prompt} {JSON_OUTPUT_WRAPPER}"

        return base_prompt
