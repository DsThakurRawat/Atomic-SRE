"""Run the Agentic SRE to diagnose errors."""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

from agentic_sre import diagnose_error
from agentic_sre.config.paths import env_path

load_dotenv(env_path())

# Configure logging to see tool calls and agent thoughts
logging.basicConfig(level=logging.INFO)
# Set logger to INFO to see agent activity
logging.getLogger("deepagents").setLevel(logging.INFO)


def _load_request_from_args_or_env() -> tuple[str, str, int]:
    """Load diagnosis inputs from CLI args or environment."""
    if len(sys.argv) >= 3:
        log_group = sys.argv[1]
        service_name = sys.argv[2]
        time_range_minutes = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        return log_group, service_name, time_range_minutes

    log_group = os.getenv("LOG_GROUP", "").strip()
    service_name = os.getenv("SERVICE_NAME", "").strip()
    if not log_group or not service_name:
        print("Usage: python -m agentic_sre.run <log_group> <service_name> [time_range_minutes]")
        print(
            "Or set environment variables: LOG_GROUP, SERVICE_NAME, TIME_RANGE_MINUTES (optional)"
        )
        raise SystemExit(1)

    raw_time_range = os.getenv("TIME_RANGE_MINUTES", "10").strip()
    try:
        time_range_minutes = int(raw_time_range)
    except ValueError as exc:
        print("TIME_RANGE_MINUTES must be an integer.")
        raise SystemExit(1) from exc

    if time_range_minutes <= 0:
        print("TIME_RANGE_MINUTES must be greater than 0.")
        raise SystemExit(1)
    return log_group, service_name, time_range_minutes


async def _main() -> None:
    """Run the Agentic SRE."""
    log_group, service_name, time_range_minutes = _load_request_from_args_or_env()

    print(f"Diagnosing errors in {log_group}")
    print(f"Service: {service_name}")
    print(f"Time range: last {time_range_minutes} minutes")
    print("-" * 60)

    try:
        result = await diagnose_error(
            log_group=log_group,
            service_name=service_name,
            time_range_minutes=time_range_minutes,
        )

        print("-" * 60)
        print("DIAGNOSIS RESULT")
        print("-" * 60)
        print(f"\nSummary: {result.summary}")
        print(f"\nRoot cause: {result.root_cause}")

        if result.suggested_fixes:
            print("\nSuggested fixes:")
            for fix in result.suggested_fixes:
                print(f"- {fix.description}")
    except Exception as exc:  # noqa: BLE001
        print(f"\nFATAL ERROR: {exc}")
        sys.exit(1)


def main() -> None:
    """Sync entry point for the CLI."""
    asyncio.run(_main())


if __name__ == "__main__":
    main()
