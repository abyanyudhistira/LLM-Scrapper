"""
Embedding-based Matching System
Menggunakan sentence embeddings untuk semantic similarity
"""

from typing import List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from app.schemas.profile_schema import LinkedInProfile
from app.schemas.requirement_schema import JobRequirement
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingMatcher:
    """Matcher menggunakan sentence embeddings"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedding model
        
        Args:
            model_name: Nama model dari sentence-transformers
                       'all-MiniLM-L6-v2' - cepat, ringan (default)
                       'all-mpnet-base-v2' - lebih akurat tapi lebih berat
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("Embedding model loaded")
    
    def encode_texts(self, texts: List[str]) -> np.ndarray:
        """Encode texts menjadi embeddings"""
        return self.model.encode(texts, convert_to_numpy=True)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Hitung similarity antara dua text
        
        Returns:
            Similarity score 0-1
        """
        embeddings = self.encode_texts([text1, text2])
        similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return float(similarity)
    
    def match_skills_semantic(
        self, 
        profile_skills: List[str], 
        required_skills: List[str]
    ) -> Tuple[float, List[Tuple[str, str, float]]]:
        """
        Match skills menggunakan semantic similarity
        
        Returns:
            (average_similarity, matches)
            matches: List of (profile_skill, required_skill, similarity)
        """
        if not profile_skills or not required_skills:
            return 0.0, []
        
        # Encode semua skills
        profile_embeddings = self.encode_texts(profile_skills)
        required_embeddings = self.encode_texts(required_skills)
        
        # Hitung similarity matrix
        similarity_matrix = cosine_similarity(required_embeddings, profile_embeddings)
        
        matches = []
        total_similarity = 0.0
        
        for i, req_skill in enumerate(required_skills):
            # Cari profile skill dengan similarity tertinggi
            max_sim_idx = np.argmax(similarity_matrix[i])
            max_similarity = similarity_matrix[i][max_sim_idx]
            
            from app.utils.config import EMBEDDING_SIMILARITY_THRESHOLD
            if max_similarity > EMBEDDING_SIMILARITY_THRESHOLD:  # Threshold untuk dianggap match
                matches.append((
                    profile_skills[max_sim_idx],
                    req_skill,
                    float(max_similarity)
                ))
                total_similarity += max_similarity
        
        avg_similarity = total_similarity / len(required_skills) if required_skills else 0.0
        
        return avg_similarity, matches
    
    def match_job_description(
        self,
        profile: LinkedInProfile,
        requirement: JobRequirement
    ) -> float:
        """
        Match keseluruhan profile dengan job description
        
        Returns:
            Similarity score 0-1
        """
        # Buat summary dari profile
        profile_text = self._create_profile_summary(profile)
        
        # Buat summary dari requirement
        requirement_text = self._create_requirement_summary(requirement)
        
        # Hitung similarity
        similarity = self.calculate_similarity(profile_text, requirement_text)
        
        return similarity
    
    def _create_profile_summary(self, profile: LinkedInProfile) -> str:
        """Buat summary text dari profile"""
        parts = []
        
        # Headline
        if profile.headline:
            parts.append(profile.headline)
        
        # Experience
        for exp in profile.experiences[:3]:  # Top 3 experiences
            parts.append(f"{exp.title} at {exp.company}")
            if exp.description:
                parts.append(exp.description)
        
        # Skills
        if profile.skills:
            parts.append("Skills: " + ", ".join(profile.skills[:10]))
        
        # Education
        for edu in profile.education:
            parts.append(f"{edu.degree} in {edu.field_of_study or 'N/A'}")
        
        return " ".join(parts)
    
    def _create_requirement_summary(self, requirement: JobRequirement) -> str:
        """Buat summary text dari requirement"""
        parts = [
            requirement.job_title,
            f"at {requirement.company_name}"
        ]
        
        if requirement.job_description:
            parts.append(requirement.job_description)
        
        if requirement.required_skills:
            parts.append("Required skills: " + ", ".join(requirement.required_skills))
        
        if requirement.min_experience_years:
            parts.append(f"{requirement.min_experience_years} years experience")
        
        return " ".join(parts)
    
    def hybrid_score(
        self,
        profile: LinkedInProfile,
        requirement: JobRequirement
    ) -> dict:
        """
        Kombinasi skill matching dan job description matching
        
        Returns:
            Dictionary dengan detail scoring
        """
        # Skills matching
        skills_sim, skills_matches = self.match_skills_semantic(
            profile.skills,
            requirement.required_skills
        )
        
        # Overall job matching
        job_sim = self.match_job_description(profile, requirement)
        
        # Weighted average (skills 60%, overall 40%)
        final_score = (skills_sim * 0.6 + job_sim * 0.4) * 100
        
        return {
            'total_score': int(final_score),
            'skills_similarity': skills_sim,
            'job_similarity': job_sim,
            'matched_skills': skills_matches
        }


# Singleton instance
_embedding_matcher = None

def get_embedding_matcher() -> EmbeddingMatcher:
    """Get atau create embedding matcher instance"""
    global _embedding_matcher
    if _embedding_matcher is None:
        _embedding_matcher = EmbeddingMatcher()
    return _embedding_matcher
