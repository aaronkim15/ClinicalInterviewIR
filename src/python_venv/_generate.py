from python_venv._transcribe import groq_client
from typing import List, Dict, Any
from pathlib import Path
import json


def get_generation(query:str, system_prompt:str) -> str:
    """
    Generates A LLM Response For Inputted Query Using Specified Prompt

    Arguments:
        query: The user query a response is generated for
        system_prompt: Instructional prompt instructing response behaviour

    Returns: LLM generated response
    """
    summary = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": query
            }
        ]
    )
    return summary.choices[0].message.content



def get_generated_roles(segments: List[Dict[str, Any]]) -> List[Dict[str,Any]]:

    query = "\n".join(
        f"{segment['speaker']}: {segment['text']}"
        for segment in segments[:10]
    )

    system_prompt = (Path(__file__).resolve().parents[2] / "prompts" / "CLASSIFIER.txt").read_text()

    clinician = get_generation(query=query, system_prompt=system_prompt)

    for segment in segments:
        if segment['speaker'] == clinician:
            segment['speaker'] = "CLINICIAN"
        else:
            segment['speaker'] = "PATIENT"

    return segments










