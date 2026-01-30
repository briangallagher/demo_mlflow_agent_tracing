from pathlib import Path

from demo_mlflow_agent_tracing.constants import DIRECTORY_PATH
from demo_mlflow_agent_tracing.settings import Settings
from openai import OpenAI
from pydantic import BaseModel


class QuestionAnswerPair(BaseModel):
    index: int
    question: str
    answer: str


class QuestionAnswerPairs(BaseModel):
    pairs: list[QuestionAnswerPair]


class GenerationResult(BaseModel):
    file: Path
    index: int
    question: str
    answer: str


PROMPT_TEMPLATE = """
You are an expert in AI system testing. Your task is to create question and answer pairs based on a given document.

Each question should be related to a relevant part of the document and should be clear and concise. Each answer should be a short, relevant sentence that directly answers the question.

Questions must not ask about document structure, headers, authors, metadata, or other such information. Questions should be focused on the content of the document and the information it is conveying.

Here is the document:

## START DOCUMENT ##

{document}

## END DOCUMENT ##

Please provide your {num_pairs} question and answer pairs about this document. Provide your response in JSON format as follows:

{{
    "pairs": [
        {{"question": "Question 1", "answer": "Answer 1"}},
        {{"question": "Question 2", "answer": "Answer 2"}},
        ...
    ]
}}

""".strip()


def sanitize_result(result: GenerationResult):
    """Sanitize the results of the generation process."""
    sanitized = result
    sanitized.question = sanitized.question.replace("‑", "-").replace("’", "'").replace(" ", " ")
    sanitized.answer = sanitized.answer.replace("‑", "-").replace("’", "'").replace(" ", " ")
    return sanitized


def main():
    """Generate synthetic QnA pairs."""
    # Set up OpenAI Client
    settings = Settings()
    model = settings.OPENAI_MODEL_NAME
    client = OpenAI(
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
    )

    # Fetch document paths
    directory = DIRECTORY_PATH / "public" / "oscorp_policies"
    paths = list(directory.glob("*.md"))

    # Generate QnA pairs
    num_pairs = 5
    generation_results: list[GenerationResult] = []
    for path in paths:
        # Prepare system prompt
        document = path.read_text()
        prompt = PROMPT_TEMPLATE.format(num_pairs=num_pairs, document=document)

        # Generate QnAs
        messages = [{"role": "user", "content": prompt}]
        response = client.beta.chat.completions.parse(
            messages=messages,
            response_format=QuestionAnswerPairs,
            model=model,
        )
        qna_pairs = response.choices[0].message.parsed

        # Save generation result
        results = [
            GenerationResult(question=pair.question, answer=pair.answer, file=path.name, index=i+1) for i, pair in enumerate(qna_pairs.pairs)
        ]
        results = [sanitize_result(result=result) for result in results]
        generation_results.extend(results)

    # Save pairs to a jsonl file
    with open(path.parent / f"qna_pairs.jsonl", "w") as f:
        for generation_result in generation_results:
            f.write(generation_result.model_dump_json() + "\n")


if __name__ == "__main__":
    main()
