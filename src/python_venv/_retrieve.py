from pathlib import Path
from typing import List, Dict, Any
from supabase import create_client
import os 
from dotenv import load_dotenv

load_dotenv()

supabase_client = create_client(supabase_url=os.getenv("SUPABASE_URL"), supabase_key=os.getenv("SUPABASE_KEY"))

def get_retrieval(query_vector:list[float], speaker: str = None, segment_count:int = 5) -> List[dict[str, Any]]:
    """
    Retrieves a subset of the most semantically similar transcripts segments from Supabase database
    
    Arguments:
        query_vector: The vector to compare similarity against
        speaker: An optional speaker filter
        segment_count: The number of most similar segments to return

    Returns: A list of dictionaries each representing a relevant transcript segment
    """
    response = supabase_client.rpc("match_segments", {
        "query_embedding": query_vector,
        "speaker_filter": speaker,
        "match_count": segment_count
    }).execute()
    return response.data
