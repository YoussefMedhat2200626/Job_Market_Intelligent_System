import asyncio
import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["MONGODB_URI"] = "mongodb://localhost:27017"
os.environ["MONGODB_DB_NAME"] = "job_board_intelligence"

from src.models.database import connect_db, close_db
from src.controllers.scraper_controller import enqueue_scrape, run_scrape
from src.controllers.analytics_controller import (
    get_dashboard, get_skill_graph, get_salary_intelligence, 
    get_skill_clustering, get_company_hiring_patterns, 
    get_company_skill_matrix, get_category_hiring_trends
)
from src.controllers.jobs_controller import get_jobs

async def generate_json():
    print("Connecting to local MongoDB (GitHub Actions service)...")
    await connect_db()
    
    print("Running scraper and AI enricher...")
    # Scrape 5 pages for a good sample size.
    task_id = await enqueue_scrape(keywords=["software", "data", "engineer", "developer"], max_pages=5)
    await run_scrape(task_id, keywords=["software", "data", "engineer", "developer"], max_pages=5)
    print("Scraping completed.")

    print("Extracting data and analytics...")
    jobs, total_jobs = await get_jobs(limit=1000)
    
    dashboard = await get_dashboard()
    skill_graph = await get_skill_graph()
    salary = await get_salary_intelligence()
    clustering = await get_skill_clustering()
    company_patterns = await get_company_hiring_patterns()
    company_skills = await get_company_skill_matrix()
    category_trends = await get_category_hiring_trends()
    
    print("Writing to JSON files...")
    out_dir = Path("src/views/frontend/public/data")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Custom encoder for ObjectId and datetime
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            return str(obj)

    with open(out_dir / "jobs.json", "w", encoding="utf-8") as f:
        json.dump([j.model_dump() for j in jobs], f, cls=CustomEncoder, ensure_ascii=False)
        
    with open(out_dir / "insights.json", "w", encoding="utf-8") as f:
        json.dump({
            "dashboard": dashboard,
            "skill_graph": skill_graph,
            "salary_intelligence": salary,
            "clustering": clustering,
            "company_patterns": company_patterns,
            "company_skills": company_skills,
            "category_trends": category_trends
        }, f, cls=CustomEncoder, ensure_ascii=False)
        
    print("Done! Data written to src/views/frontend/public/data/")
    await close_db()

if __name__ == "__main__":
    asyncio.run(generate_json())
