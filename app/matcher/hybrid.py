"""
Hybrid Matching System
Menggabungkan Rule-based, Embedding, dan LLM
"""

from app.schemas.profile_schema import LinkedInProfile
from app.schemas.requirement_schema import JobRequirement
from app.schemas.result_schema import MatchResult, RequirementDetail
from app.matcher.rule_based import rule_based_scoring, should_use_llm
from app.matcher.embedding import get_embedding_matcher
from app.matcher.evaluate import evaluate_match
from app.utils.logger import get_logger

logger = get_logger(__name__)


class HybridMatcher:
    """
    Hybrid matching system dengan 3 tahap:
    1. Rule-based filtering (cepat)
    2. Embedding-based scoring (semantic)
    3. LLM evaluation (detail & reasoning)
    """
    
    def __init__(self, use_embedding: bool = True, use_llm: bool = True):
        """
        Initialize hybrid matcher
        
        Args:
            use_embedding: Gunakan embedding matching
            use_llm: Gunakan LLM evaluation
        """
        self.use_embedding = use_embedding
        self.use_llm = use_llm
        
        if use_embedding:
            self.embedding_matcher = get_embedding_matcher()
        else:
            self.embedding_matcher = None
    
    def match(
        self,
        profile: LinkedInProfile,
        requirement: JobRequirement
    ) -> MatchResult:
        """
        Lakukan matching dengan hybrid approach
        
        Returns:
            MatchResult dengan score dan detail
        """
        logger.info(f"Starting hybrid matching for {profile.name} - {requirement.job_title}")
        
        # Stage 1: Rule-based filtering
        logger.info("Stage 1: Rule-based filtering")
        rule_result = rule_based_scoring(profile, requirement)
        
        # Jika score terlalu rendah, langsung reject
        if not rule_result['passed_threshold']:
            logger.info(f"Failed rule-based threshold: {rule_result['total_score']}")
            return self._create_reject_result(rule_result)
        
        # Stage 2: Embedding-based scoring (optional)
        embedding_score = 0
        if self.use_embedding and self.embedding_matcher:
            logger.info("Stage 2: Embedding-based scoring")
            embedding_result = self.embedding_matcher.hybrid_score(profile, requirement)
            embedding_score = embedding_result['total_score']
            logger.info(f"Embedding score: {embedding_score}")
        
        # Stage 3: LLM evaluation (optional)
        if self.use_llm and should_use_llm(rule_result):
            logger.info("Stage 3: LLM detailed evaluation")
            llm_result = evaluate_match(profile, requirement)
            
            # Combine scores (weighted average)
            # Rule: 30%, Embedding: 20%, LLM: 50%
            if self.use_embedding:
                final_score = int(
                    rule_result['total_score'] * 0.3 +
                    embedding_score * 0.2 +
                    llm_result.score * 0.5
                )
            else:
                # Rule: 40%, LLM: 60%
                final_score = int(
                    rule_result['total_score'] * 0.4 +
                    llm_result.score * 0.6
                )
            
            llm_result.score = final_score
            logger.info(f"Final hybrid score: {final_score}")
            return llm_result
        
        # Jika tidak pakai LLM, gunakan rule + embedding
        if self.use_embedding:
            final_score = int(
                rule_result['total_score'] * 0.6 +
                embedding_score * 0.4
            )
        else:
            final_score = rule_result['total_score']
        
        logger.info(f"Final score (without LLM): {final_score}")
        return self._create_result_from_rules(rule_result, final_score)
    
    def _create_reject_result(self, rule_result: dict) -> MatchResult:
        """Buat MatchResult untuk kandidat yang ditolak"""
        matched_reqs = []
        
        # Experience requirement
        exp = rule_result['experience']
        matched_reqs.append(RequirementDetail(
            requirement=f"Minimal {exp['required_years']} tahun pengalaman",
            status="tidak_terpenuhi" if not exp['matched'] else "terpenuhi",
            explanation=f"Kandidat memiliki {exp['profile_years']:.1f} tahun pengalaman"
        ))
        
        # Skills requirement
        skills = rule_result['skills']
        matched_reqs.append(RequirementDetail(
            requirement=f"Menguasai {skills['total_required']} skills yang dibutuhkan",
            status="tidak_terpenuhi",
            explanation=f"Hanya {skills['matched_count']} dari {skills['total_required']} skills yang cocok"
        ))
        
        return MatchResult(
            score=rule_result['total_score'],
            matched_requirements=matched_reqs,
            summary=f"Kandidat tidak memenuhi kriteria minimum dengan score {rule_result['total_score']}/100",
            should_send_message=False
        )
    
    def _create_result_from_rules(self, rule_result: dict, final_score: int) -> MatchResult:
        """Buat MatchResult dari rule-based result"""
        matched_reqs = []
        
        # Experience
        exp = rule_result['experience']
        matched_reqs.append(RequirementDetail(
            requirement=f"Minimal {exp['required_years']} tahun pengalaman",
            status="terpenuhi" if exp['matched'] else "tidak_terpenuhi",
            explanation=f"Kandidat memiliki {exp['profile_years']:.1f} tahun pengalaman"
        ))
        
        # Skills
        skills = rule_result['skills']
        matched_reqs.append(RequirementDetail(
            requirement=f"Menguasai skills yang dibutuhkan",
            status="terpenuhi" if skills['matched_count'] >= skills['total_required'] * 0.6 else "tidak_terpenuhi",
            explanation=f"{skills['matched_count']} dari {skills['total_required']} skills cocok: {', '.join(skills['matched_skills'][:5])}"
        ))
        
        # Education
        edu = rule_result['education']
        matched_reqs.append(RequirementDetail(
            requirement="Pendidikan yang sesuai",
            status="terpenuhi" if edu['matched'] else "tidak_terpenuhi",
            explanation="Pendidikan kandidat sesuai dengan requirement" if edu['matched'] else "Pendidikan tidak sepenuhnya sesuai"
        ))
        
        return MatchResult(
            score=final_score,
            matched_requirements=matched_reqs,
            summary=f"Kandidat memiliki score {final_score}/100 berdasarkan rule-based dan embedding analysis",
            should_send_message=final_score >= 70
        )


# Singleton instance
_hybrid_matcher = None

def get_hybrid_matcher(use_embedding: bool = True, use_llm: bool = True) -> HybridMatcher:
    """Get atau create hybrid matcher instance"""
    global _hybrid_matcher
    if _hybrid_matcher is None:
        _hybrid_matcher = HybridMatcher(use_embedding, use_llm)
    return _hybrid_matcher
