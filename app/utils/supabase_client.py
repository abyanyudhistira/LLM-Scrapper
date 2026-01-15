"""
Supabase Client for database operations
Menggunakan existing database schema
"""

from supabase import create_client, Client
from app.utils.config import SUPABASE_URL, SUPABASE_KEY
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for Supabase database operations"""
    
    def __init__(self):
        self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # ========================================================================
    # SCRAPED LEADS
    # ========================================================================
    
    def get_scraped_lead(self, lead_id: str) -> Optional[Dict]:
        """Get scraped lead by ID"""
        try:
            response = self.client.table('scraped_leads').select('*').eq('id', lead_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting scraped lead {lead_id}: {e}")
            return None
    
    def update_lead_score(self, lead_id: str, score: int, profile_data: dict = None):
        """Update score and profile_data of scraped lead"""
        try:
            data = {'score': score}
            
            if profile_data:
                data['profile_data'] = profile_data
            
            self.client.table('scraped_leads').update(data).eq('id', lead_id).execute()
            logger.info(f"Updated lead {lead_id} score to {score}")
        except Exception as e:
            logger.error(f"Error updating lead score: {e}")
    
    def get_leads_by_template(self, template_id: str, limit: int = 100) -> List[Dict]:
        """Get leads by template_id"""
        try:
            response = (
                self.client.table('scraped_leads')
                .select('*')
                .eq('template_id', template_id)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error getting leads by template: {e}")
            return []
    
    def get_unscored_leads(self, template_id: str = None, limit: int = 100) -> List[Dict]:
        """Get leads yang belum di-score (score is null)"""
        try:
            query = self.client.table('scraped_leads').select('*').is_('score', 'null')
            
            if template_id:
                query = query.eq('template_id', template_id)
            
            response = query.limit(limit).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting unscored leads: {e}")
            return []
    
    # ========================================================================
    # SEARCH TEMPLATES
    # ========================================================================
    
    def get_search_template(self, template_id: str) -> Optional[Dict]:
        """Get search template by ID"""
        try:
            response = self.client.table('search_templates').select('*').eq('id', template_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting search template: {e}")
            return None
    
    def get_template_with_company(self, template_id: str) -> Optional[Dict]:
        """Get search template with company info"""
        try:
            response = (
                self.client.table('search_templates')
                .select('*, companies(*)')
                .eq('id', template_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting template with company: {e}")
            return None
    
    # ========================================================================
    # COMPANIES
    # ========================================================================
    
    def get_company(self, company_id: str) -> Optional[Dict]:
        """Get company by ID"""
        try:
            response = self.client.table('companies').select('*').eq('id', company_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting company: {e}")
            return None
    
    def get_all_companies(self) -> List[Dict]:
        """Get all companies"""
        try:
            response = self.client.table('companies').select('*').execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting companies: {e}")
            return []
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    def get_template_stats(self, template_id: str) -> Dict:
        """Get statistics for a template"""
        try:
            # Get all leads for template
            leads = self.get_leads_by_template(template_id)
            
            total = len(leads)
            scored = sum(1 for lead in leads if lead.get('score') is not None)
            unscored = total - scored
            
            scores = [lead['score'] for lead in leads if lead.get('score') is not None]
            avg_score = sum(scores) / len(scores) if scores else 0
            max_score = max(scores) if scores else 0
            
            return {
                'total_leads': total,
                'scored': scored,
                'unscored': unscored,
                'avg_score': round(avg_score, 2),
                'max_score': max_score
            }
        except Exception as e:
            logger.error(f"Error getting template stats: {e}")
            return {'total_leads': 0, 'scored': 0, 'unscored': 0, 'avg_score': 0, 'max_score': 0}
    
    def get_top_candidates(self, template_id: str, limit: int = 10) -> List[Dict]:
        """Get top candidates for a template, sorted by score"""
        try:
            response = (
                self.client.table('scraped_leads')
                .select('*')
                .eq('template_id', template_id)
                .not_.is_('score', 'null')
                .order('score', desc=True)
                .limit(limit)
                .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Error getting top candidates: {e}")
            return []


# Singleton instance
_supabase_client = None

def get_supabase_client() -> SupabaseClient:
    """Get singleton Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
