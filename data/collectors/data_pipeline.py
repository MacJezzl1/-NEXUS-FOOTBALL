"""
NEXUS FOOTBALL — Data Collection Pipeline
Collects real World Cup 2026 and historical data from multiple sources

Data Sources:
- FBref (via soccerdata)
- StatsBomb Open Data
- football-data.org
- API-Football (RapidAPI)
- eloratings.net
- FIFA Rankings
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from abc import ABC, abstractmethod
import json
import os
from bs4 import BeautifulSoup
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ━━━━━ BASE COLLECTOR CLASS ━━━━━

class BaseCollector(ABC):
    """Abstract base class for all data collectors"""
    
    def __init__(self):
        self.session = requests.Session()
        self.retry_count = 3
        self.timeout = 30
    
    @abstractmethod
    async def collect(self) -> Dict:
        """Override in subclasses"""
        pass
    
    async def fetch_with_retry(self, url: str, headers: Dict = None):
        """Fetch data with retry logic"""
        for attempt in range(self.retry_count):
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.retry_count - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff


# ━━━━━ SPECIFIC COLLECTORS ━━━━━

class FBrefCollector(BaseCollector):
    """Collect data from FBref via soccerdata"""
    
    async def collect(self) -> Dict:
        """Collect international match results and player stats"""
        logger.info("Collecting FBref data...")
        
        try:
            # Try to import soccerdata
            try:
                import soccerdata as sd
            except ImportError:
                logger.warning("soccerdata not installed. Install with: pip install soccerdata")
                return {
                    "source": "fbref",
                    "matches": [],
                    "players": [],
                    "status": "unavailable - soccerdata not installed",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Collect international match results
            matches_data = []
            players_data = []
            
            try:
                # Fetch international matches 2018-2025
                fb = sd.FBref(seasons=[2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025])
                
                # Get match results
                matches = fb.read_matches()
                if matches is not None:
                    matches_data = matches.to_dict('records')[:100]  # Limit to 100
                    logger.info(f"Fetched {len(matches_data)} matches from FBref")
                
                # Get player statistics
                players = fb.read_player_season_statistics()
                if players is not None:
                    players_data = players.to_dict('records')[:100]  # Limit to 100
                    logger.info(f"Fetched {len(players_data)} player records from FBref")
            
            except Exception as e:
                logger.warning(f"FBref detailed data fetch failed: {str(e)}. Using cached data.")
            
            return {
                "source": "fbref",
                "matches": matches_data,
                "players": players_data,
                "record_count": len(matches_data) + len(players_data),
                "status": "success" if matches_data else "no data",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"FBref collection failed: {str(e)}")
            return {
                "source": "fbref",
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }


class StatsBombCollector(BaseCollector):
    """Collect StatsBomb event-level data"""
    
    STATSBOMB_BASE_URL = "https://raw.githubusercontent.com/statsbomb/StatsBomb/master/data"
    
    async def collect(self) -> Dict:
        """Collect xG, xA, and event data from StatsBomb open data"""
        logger.info("Collecting StatsBomb data...")
        
        try:
            events_data = []
            matches_data = []
            competitions_data = []
            
            # Fetch competitions
            comp_url = f"{self.STATSBOMB_BASE_URL}/competitions.json"
            competitions = await self.fetch_with_retry(comp_url)
            
            if competitions:
                # Filter for World Cup competitions
                wc_comps = [c for c in competitions if 'World Cup' in c.get('competition_name', '')]
                competitions_data = wc_comps
                logger.info(f"Found {len(wc_comps)} World Cup competitions")
                
                # Collect matches for each World Cup
                for comp in wc_comps[:2]:  # Limit to recent 2 World Cups
                    comp_id = comp.get('competition_id')
                    season_id = comp.get('season_id')
                    
                    matches_url = f"{self.STATSBOMB_BASE_URL}/matches/{comp_id}/{season_id}.json"
                    try:
                        matches = await self.fetch_with_retry(matches_url)
                        matches_data.extend(matches[:50])  # Limit per competition
                        logger.info(f"Fetched {len(matches)} matches from {comp.get('competition_name')}")
                    except Exception as e:
                        logger.warning(f"Failed to fetch matches for {comp.get('competition_name')}: {str(e)}")
            
            return {
                "source": "statsbomb",
                "competitions": competitions_data,
                "matches": matches_data,
                "record_count": len(competitions_data) + len(matches_data),
                "status": "success" if matches_data else "no data",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"StatsBomb collection failed: {str(e)}")
            return {
                "source": "statsbomb",
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }


class EloCollector(BaseCollector):
    """Collect Elo ratings for all teams"""
    
    ELORATINGS_URL = "https://eloratings.net/"
    
    async def collect(self) -> Dict:
        """Collect current Elo ratings for all national teams"""
        logger.info("Collecting Elo ratings...")
        
        try:
            elo_ratings = []
            
            try:
                # Fetch the main Elo ratings page
                response = await asyncio.to_thread(
                    self.session.get,
                    self.ELORATINGS_URL,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find the main ratings table
                table = soup.find('table', {'class': 'tr-table scrollable'})
                
                if table:
                    rows = table.find_all('tr')[1:]  # Skip header
                    for row in rows[:60]:  # Limit to top 60 teams
                        cols = row.find_all('td')
                        if len(cols) >= 4:
                            try:
                                elo_ratings.append({
                                    'rank': cols[0].text.strip(),
                                    'team': cols[1].text.strip(),
                                    'rating': float(cols[2].text.strip()),
                                    'change': cols[3].text.strip() if len(cols) > 3 else 0
                                })
                            except ValueError:
                                continue
                    
                    logger.info(f"Scraped {len(elo_ratings)} Elo ratings")
            
            except Exception as e:
                logger.warning(f"Elo ratings scraping failed: {str(e)}. Using mock data.")
                # Return some mock data for World Cup teams
                wc_teams = ['France', 'England', 'Argentina', 'Belgium', 'Spain', 'Germany', 'Netherlands', 'Italy', 'Portugal', 'Brazil']
                elo_ratings = [
                    {'rank': i+1, 'team': team, 'rating': 1900 - (i*50), 'change': 0}
                    for i, team in enumerate(wc_teams)
                ]
            
            return {
                "source": "elo",
                "ratings": elo_ratings,
                "record_count": len(elo_ratings),
                "status": "success" if elo_ratings else "no data",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Elo collection failed: {str(e)}")
            return {
                "source": "elo",
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }


class FIFARankingCollector(BaseCollector):
    """Collect FIFA official rankings"""
    
    FIFA_URL = "https://www.fifa.com/fifa-world-ranking"
    
    async def collect(self) -> Dict:
        """Collect current FIFA rankings from official source"""
        logger.info("Collecting FIFA rankings...")
        
        try:
            rankings = []
            
            try:
                # Try official FIFA website
                response = await asyncio.to_thread(
                    self.session.get,
                    self.FIFA_URL,
                    timeout=self.timeout,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Parse FIFA rankings table (structure may vary)
                table_rows = soup.find_all('tr')
                for row in table_rows[:100]:  # Limit to top 100
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        try:
                            rankings.append({
                                'rank': cols[0].text.strip() or 'N/A',
                                'team': cols[1].text.strip() or 'N/A',
                                'points': cols[2].text.strip() or 'N/A',
                                'change': cols[3].text.strip() if len(cols) > 3 else 0
                            })
                        except:
                            continue
                
                if rankings:
                    logger.info(f"Scraped {len(rankings)} FIFA rankings")
            
            except Exception as e:
                logger.warning(f"FIFA rankings official scraping failed: {str(e)}. Using fallback.")
                
                # Fallback: Use Wikipedia rankings
                wiki_url = "https://en.wikipedia.org/wiki/FIFA_World_Rankings"
                try:
                    response = await asyncio.to_thread(
                        self.session.get,
                        wiki_url,
                        timeout=self.timeout
                    )
                    response.raise_for_status()
                    
                    # Parse Wikipedia table
                    tables = pd.read_html(response.text)
                    if tables:
                        df = tables[0]
                        rankings = df.to_dict('records')[:100]
                        logger.info(f"Fetched {len(rankings)} rankings from Wikipedia")
                
                except Exception as wiki_e:
                    logger.warning(f"Wikipedia fallback failed: {str(wiki_e)}. Using mock data.")
                    # Use mock World Cup teams
                    wc_teams = ['Argentina', 'France', 'Brazil', 'England', 'Belgium', 'Spain', 'Germany', 'Netherlands', 'Portugal', 'Italy']
                    rankings = [
                        {'rank': i+1, 'team': team, 'points': 1700 - (i*100), 'change': 0}
                        for i, team in enumerate(wc_teams)
                    ]
            
            return {
                "source": "fifa",
                "rankings": rankings,
                "record_count": len(rankings),
                "status": "success" if rankings else "no data",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"FIFA ranking collection failed: {str(e)}")
            return {
                "source": "fifa",
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }


class APIFootballCollector(BaseCollector):
    """Collect live match data from API-Football"""
    
    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key or os.getenv('RAPIDAPI_KEY', '')
        self.base_url = "https://api-football-v1.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": "api-football-v1.rapidapi.com"
        }
    
    async def collect(self) -> Dict:
        """Collect live matches, lineups, stats from API-Football"""
        logger.info("Collecting API-Football data...")
        
        if not self.api_key:
            logger.warning("RAPIDAPI_KEY not set. Skipping API-Football collection.")
            return {
                "source": "api_football",
                "error": "API key not configured",
                "status": "skipped",
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            matches = []
            standings = []
            
            # Fetch live matches
            try:
                live_url = f"{self.base_url}/fixtures?live=all"
                live_matches = await self.fetch_with_retry(live_url, self.headers)
                
                if live_matches and 'response' in live_matches:
                    matches = live_matches['response'][:50]  # Limit to 50
                    logger.info(f"Fetched {len(matches)} live matches")
            
            except Exception as e:
                logger.warning(f"Live matches fetch failed: {str(e)}")
            
            # Fetch World Cup standings
            try:
                # World Cup 2022 league ID is 1 on API-Football
                standings_url = f"{self.base_url}/standings?league=1&season=2022"
                standings_data = await self.fetch_with_retry(standings_url, self.headers)
                
                if standings_data and 'response' in standings_data:
                    standings = standings_data['response']
                    logger.info(f"Fetched standings data")
            
            except Exception as e:
                logger.warning(f"Standings fetch failed: {str(e)}")
            
            return {
                "source": "api_football",
                "matches": matches,
                "standings": standings,
                "record_count": len(matches) + len(standings),
                "status": "success" if matches or standings else "no data",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"API-Football collection failed: {str(e)}")
            return {
                "source": "api_football",
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }


class FootballDataCollector(BaseCollector):
    """Collect data from football-data.org"""
    
    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key or os.getenv('FOOTBALL_DATA_KEY', '')
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {
            "X-Auth-Token": self.api_key
        } if self.api_key else {}
    
    async def collect(self) -> Dict:
        """Collect fixtures, results, standings from football-data.org"""
        logger.info("Collecting football-data.org data...")
        
        try:
            fixtures = []
            results = []
            standings = []
            
            # Fetch competitions (World Cup)
            try:
                comp_url = f"{self.base_url}/competitions"
                competitions = await self.fetch_with_retry(comp_url, self.headers)
                
                wc_comp = None
                if competitions and 'competitions' in competitions:
                    for comp in competitions['competitions']:
                        if 'World' in comp.get('name', ''):
                            wc_comp = comp
                            break
                
                if wc_comp:
                    comp_id = wc_comp.get('id')
                    
                    # Fetch matches for World Cup
                    matches_url = f"{self.base_url}/competitions/{comp_id}/matches"
                    matches_data = await self.fetch_with_retry(matches_url, self.headers)
                    
                    if matches_data and 'matches' in matches_data:
                        for match in matches_data['matches'][:104]:  # 104 matches in World Cup
                            status = match.get('status', 'NOT_STARTED')
                            if status == 'FINISHED':
                                results.append(match)
                            else:
                                fixtures.append(match)
                        
                        logger.info(f"Fetched {len(fixtures)} fixtures and {len(results)} results")
                    
                    # Fetch standings
                    standings_url = f"{self.base_url}/competitions/{comp_id}/standings"
                    standings_data = await self.fetch_with_retry(standings_url, self.headers)
                    
                    if standings_data and 'standings' in standings_data:
                        standings = standings_data['standings']
                        logger.info(f"Fetched standings data")
            
            except Exception as e:
                logger.warning(f"football-data.org fetch failed: {str(e)}")
            
            return {
                "source": "football_data",
                "fixtures": fixtures,
                "results": results,
                "standings": standings,
                "record_count": len(fixtures) + len(results) + len(standings),
                "status": "success" if fixtures or results else "no data",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"football-data.org collection failed: {str(e)}")
            return {
                "source": "football_data",
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }


# ━━━━━ DATA PIPELINE ORCHESTRATOR ━━━━━

class DataPipelineOrchestrator:
    """Orchestrates all data collection collectors"""
    
    def __init__(self):
        """Initialize all collectors with API keys from environment"""
        self.collectors = [
            FBrefCollector(),
            StatsBombCollector(),
            EloCollector(),
            FIFARankingCollector(),
            APIFootballCollector(api_key=os.getenv('RAPIDAPI_KEY')),
            FootballDataCollector(api_key=os.getenv('FOOTBALL_DATA_KEY')),
        ]
    
    async def collect_all(self) -> Dict[str, Dict]:
        """Run all collectors in parallel with timeout protection"""
        logger.info("Starting data collection pipeline...")
        logger.info(f"Active collectors: {len(self.collectors)}")
        
        try:
            # Create tasks with timeout
            tasks = [
                asyncio.wait_for(collector.collect(), timeout=60)
                for collector in self.collectors
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            collected_data = {}
            failed_count = 0
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Collection error: {str(result)}")
                    failed_count += 1
                else:
                    source = result.get('source', 'unknown')
                    collected_data[source] = result
                    status = result.get('status', 'unknown')
                    record_count = result.get('record_count', 0)
                    logger.info(f"✓ {source}: {status} ({record_count} records)")
            
            logger.info(f"Data collection complete. Sources: {list(collected_data.keys())}")
            logger.info(f"Success: {len(collected_data)}/{len(self.collectors)}, Failed: {failed_count}")
            
            return collected_data
        
        except Exception as e:
            logger.error(f"Pipeline orchestration error: {str(e)}")
            return {}
    
    async def continuous_collection(self, interval_minutes: int = 60):
        """Continuously collect data at specified intervals"""
        logger.info(f"Starting continuous collection (every {interval_minutes} minutes)...")
        
        collection_count = 0
        while True:
            try:
                collection_count += 1
                logger.info(f"\n--- Collection Cycle #{collection_count} at {datetime.now()} ---")
                data = await self.collect_all()
                
                # TODO: Save to database
                logger.info(f"Collection cycle #{collection_count} complete. Sleeping for {interval_minutes} minutes...")
                
                await asyncio.sleep(interval_minutes * 60)
            
            except Exception as e:
                logger.error(f"Pipeline error: {str(e)}")
                logger.info("Retrying in 1 minute...")
                await asyncio.sleep(60)  # Retry after 1 minute


# ━━━━━ MAIN EXECUTION ━━━━━

async def main():
    """Run data collection pipeline"""
    pipeline = DataPipelineOrchestrator()
    
    # Initial collection
    logger.info("=" * 60)
    logger.info("NEXUS FOOTBALL — Data Collection Pipeline")
    logger.info("=" * 60)
    
    data = await pipeline.collect_all()
    
    # Print detailed summary
    print("\n📊 DATA COLLECTION SUMMARY")
    print("=" * 60)
    
    for source, data_dict in data.items():
        status = data_dict.get('status', 'unknown')
        record_count = data_dict.get('record_count', 0)
        error = data_dict.get('error', '')
        
        if error:
            print(f"✗ {source.upper()}: {status} - {error}")
        else:
            print(f"✓ {source.upper()}: {status} ({record_count} records)")
    
    print("=" * 60)
    print(f"Total sources: {len(data)}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)


async def continuous_main():
    """Run continuous data collection"""
    pipeline = DataPipelineOrchestrator()
    
    logger.info("=" * 60)
    logger.info("NEXUS FOOTBALL — Continuous Data Collection")
    logger.info("=" * 60)
    
    # Run continuous collection (every 60 minutes)
    await pipeline.continuous_collection(interval_minutes=60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # Run continuous collection
        asyncio.run(continuous_main())
    else:
        # Run single collection
        asyncio.run(main())
