from app.schemas.result_schema import MatchResult
from app.utils.config import MATCH_THRESHOLD

def apply_threshold(result: MatchResult) -> MatchResult:
    """Tentukan apakah pesan harus dikirim berdasarkan threshold"""
    result.should_send_message = result.score >= MATCH_THRESHOLD
    return result
