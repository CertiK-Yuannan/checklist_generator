#!/usr/bin/env python3
"""
Main entry point for the Checklist Generator system.
Controls the overall workflow of retrieving findings and generating checklists.
"""

import os
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

from finding_retriever.solodit_tidb import SoloditTiDBRetriever
# from checklist_generator.generator import ChecklistGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output to console
    ]
)
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        logger.info(f"Loading environment variables from {env_path}")
        load_dotenv(dotenv_path=env_path)
        logger.debug("Environment variables loaded successfully")
    else:
        logger.warning(f".env file not found at {env_path}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate checklists from findings.')
    parser.add_argument('--source', choices=['solodit_tidb'], default='solodit_tidb',
                        help='Source for retrieving findings (default: solodit_tidb)')
    parser.add_argument('--category', help='Category of findings to retrieve', required=True)
    # Note: this feature is not well implemented yet
    parser.add_argument('--query', type=str, default=None,
                        help='Optional custom SQL query to override the default query')
    
    args = parser.parse_args()
    logger.debug(f"Parsed arguments: source={args.source}, category={args.category}")
    return args

def main():
    # Load environment variables
    load_environment()
    
    # Parse command line arguments
    args = parse_arguments()
    category = args.category
    source = args.source
    
    logger.info(f"Retrieving findings for category: {category}")
    
    # Fetch findings from different sources
    findings = []
    if args.source == 'solodit_tidb':            
        logger.info("Initializing TiDB retriever")
        retriever = SoloditTiDBRetriever(
            host=os.getenv("TIDB_HOST"),
            user=os.getenv("TIDB_USER"),
            password=os.getenv("TIDB_PASSWORD"),
            port=int(os.getenv("TIDB_PORT")),
            database=os.getenv("TIDB_DATABASE"),
        )
        
        # Retrieve findings
        retriever.retrieve_findings(category=category, custom_query=args.query)
        
        if findings:
            logger.info(f"Successfully retrieved {len(findings)} findings")
        else:
            logger.warning("No findings were retrieved")
    else:
        logger.error(f"Invalid source: {args.source}")
    
    # Generate checklist based on the findings
    # generator = ChecklistGenerator(category=category, api_key=os.getenv("OPENAI_API_KEY"))

    
    logger.info("Checklist generator completed successfully")

if __name__ == "__main__":
    main()