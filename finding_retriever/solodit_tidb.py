"""
Solodit TiDB Finding Retriever module.
Handles retrieving Solodit findings from TiDB database.
"""

import logging
import mysql.connector
import pandas as pd
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

logger = logging.getLogger(__name__)

class SoloditTiDBRetriever:
    """Component to retrieve Solodit findings from TiDB database."""
    
    def __init__(self, host: str, user: str, password: str, port: int = 4000, 
                 database: str = "shield_alds_stg"):
        """
        Initialize the Solodit TiDB retriever with connection parameters.
        
        Args:
            host: TiDB server hostname
            user: Database username
            password: Database password
            port: TiDB server port (default: 4000)
            database: Database name (default: shield_alds_stg)
        """
        self.connection_params = {
            "host": host,
            "user": user,
            "password": password,
            "port": port,
            "database": database
        }
        
    def connect_to_database(self) -> Optional[MySQLConnection]:
        """
        Establish a connection to the TiDB database.
        
        Returns:
            MySQL connection object or None if connection fails
        """
        try:
            connection = mysql.connector.connect(**self.connection_params)
            logger.info(f"Successfully connected to TiDB at {self.connection_params['host']}")
            return connection
        except mysql.connector.Error as err:
            logger.error(f"Failed to connect to TiDB: {err}")
            return None
    
    def _get_query_by_category(self, category: str) -> str:
        """
        Generate a SQL query based on the specified category.
        
        Args:
            category: The search category (e.g., 'vesting', 'reentrancy', etc.)
            
        Returns:
            SQL query string with the category search term
        """
        return f"""
        SELECT *
        FROM shield_alds_stg.t_solodit_findings
        WHERE impact IN ('HIGH')
        AND (LOWER(title) LIKE '%{category}%' OR LOWER(content) LIKE '%{category}%');
        """
    
    def _execute_query(self, cursor: MySQLCursor, query: str) -> List[Dict[str, Any]]:
        """
        Execute a query and return the results.
        
        Args:
            cursor: MySQL cursor object
            query: SQL query to execute
            
        Returns:
            List of dictionaries containing the query results
        """
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
            
        return results
            
    def retrieve_findings(self, category: Optional[str], custom_query: Optional[str] = None):
        """
        Retrieve Solodit findings from TiDB using either a custom query or
        a query generated based on the provided category.
        
        Args:
            category: Search category for findings
            custom_query: Optional custom SQL query that overrides the category-based query
            
        Returns:
            List of finding dictionaries
        """
        connection = self.connect_to_database()
        if not connection:
            logger.error("Cannot retrieve findings: database connection failed")
            return []
        
        try:
            # Determine which query to use
            if custom_query:
                query = custom_query
                logger.info("Using custom SQL query")
            else:
                query = self._get_query_by_category(category)
                logger.info(f"Using category-based query for '{category}'")
            
            logger.debug(f"Query: {query}")
            
            # Create a cursor and execute the query
            cursor = connection.cursor()
            findings = self._execute_query(cursor, query)
            
            logger.info(f"Retrieved {len(findings)} Solodit findings from TiDB")
            
            if findings:
                # Create findings directory if it doesn't exist
                findings_dir = Path(__file__).parent.parent / "findings"
                os.makedirs(findings_dir, exist_ok=True)
                
                # Save raw findings as CSV for reference
                output_filename = f"solodit_tidb_{category if not custom_query else 'custom'}.csv"
                output_file = findings_dir / output_filename
                
                # Convert findings to DataFrame and save
                df = pd.DataFrame(findings)
                df.to_csv(output_file, index=False)
                logger.info(f"Raw findings saved to {output_file}")
            else:
                logger.warning("No findings to save to CSV")
            
        except Exception as e:
            logger.error(f"Error retrieving Solodit findings from TiDB: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
            if connection:
                connection.close()
                logger.debug("Database connection closed")