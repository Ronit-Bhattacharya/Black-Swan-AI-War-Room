import asyncio
import json

from app.llm_client import generate_json


async def main():
    result = await generate_json(
        """
Return exactly one JSON object.

Required structure:

{
  "status": "ok",
  "message": "The local LLM client is working."
}
""",
        required_fields=[
            "status",
            "message",
        ],
        num_predict=150,
        retry_count=0,
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())