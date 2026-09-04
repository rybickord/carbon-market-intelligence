"""
Repository for country data access.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from backend.database.models import CountryIntelligence, CountryScore


class CountryRepository:
    """Repository for accessing country intelligence and scores from database."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_countries(self) -> List[str]:
        """Get list of unique countries."""
        results = self.db.query(
            CountryIntelligence.country
        ).distinct().order_by(CountryIntelligence.country).all()
        return [r[0] for r in results]
    
    def get_country_intelligence(
        self, 
        country: Optional[str] = None,
        year: Optional[int] = None
    ) -> List[CountryIntelligence]:
        """
        Get country intelligence data.
        
        Args:
            country: Optional country name to filter
            year: Optional year to filter
        """
        query = self.db.query(CountryIntelligence)
        
        if country:
            query = query.filter(
                func.lower(CountryIntelligence.country) == country.lower()
            )
        
        if year:
            query = query.filter(CountryIntelligence.year == year)
        
        return query.order_by(CountryIntelligence.year).all()
    
    def get_country_latest(self, country: str) -> Optional[CountryIntelligence]:
        """Get latest intelligence data for a specific country."""
        return self.db.query(CountryIntelligence).filter(
            func.lower(CountryIntelligence.country) == country.lower()
        ).order_by(desc(CountryIntelligence.year)).first()
    
    def get_country_score(self, country: str) -> Optional[CountryScore]:
        """Get risk and opportunity scores for a specific country."""
        return self.db.query(CountryScore).filter(
            func.lower(CountryScore.country) == country.lower()
        ).first()
    
    def get_risk_ranking(self, limit: Optional[int] = None) -> List[CountryScore]:
        """
        Get countries ranked by risk score (highest first).
        
        Args:
            limit: Optional limit on number of results
        """
        query = self.db.query(CountryScore).filter(
            CountryScore.risk_score.isnot(None)
        ).order_by(desc(CountryScore.risk_score))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_opportunity_ranking(self, limit: Optional[int] = None) -> List[CountryScore]:
        """
        Get countries ranked by opportunity score (highest first).
        
        Args:
            limit: Optional limit on number of results
        """
        query = self.db.query(CountryScore).filter(
            CountryScore.opportunity_score.isnot(None)
        ).order_by(desc(CountryScore.opportunity_score))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def country_exists(self, country: str) -> bool:
        """Check if a country exists in the database."""
        count = self.db.query(CountryIntelligence).filter(
            func.lower(CountryIntelligence.country) == country.lower()
        ).count()
        return count > 0
    
    def get_countries_with_scores(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[tuple]:
        """
        Get countries with their latest intelligence and scores.
        
        Returns list of tuples: (CountryIntelligence, CountryScore)
        """
        # Subquery to get latest year for each country
        latest_year_subq = self.db.query(
            CountryIntelligence.country,
            func.max(CountryIntelligence.year).label('max_year')
        ).group_by(CountryIntelligence.country).subquery()
        
        # Join intelligence with scores
        results = self.db.query(
            CountryIntelligence,
            CountryScore
        ).join(
            latest_year_subq,
            (CountryIntelligence.country == latest_year_subq.c.country) &
            (CountryIntelligence.year == latest_year_subq.c.max_year)
        ).outerjoin(
            CountryScore,
            (CountryIntelligence.country == CountryScore.country) &
            (CountryIntelligence.year == CountryScore.year)
        ).order_by(
            CountryIntelligence.country
        ).offset(skip).limit(limit).all()
        
        return results
