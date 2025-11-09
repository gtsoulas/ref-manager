"""
Output Comparison and Duplicate Detection System
For REF Manager Django Application

This module provides advanced comparison between spreadsheet data and 
database outputs with fuzzy matching and interactive review.
"""

from difflib import SequenceMatcher
from django.db.models import Q
from django.utils.dateparse import parse_date
from datetime import timedelta
import re


class OutputComparator:
    """
    Compare spreadsheet outputs against database with intelligent matching.
    """
    
    # Thresholds for similarity matching
    TITLE_SIMILARITY_THRESHOLD = 0.85  # 85% similar titles
    AUTHOR_OVERLAP_THRESHOLD = 0.5     # 50% author overlap
    DATE_PROXIMITY_DAYS = 180          # Within 6 months
    
    def __init__(self, outputs_queryset):
        """
        Initialize with existing outputs from database.
        
        Args:
            outputs_queryset: Django QuerySet of Output objects
        """
        self.db_outputs = list(outputs_queryset)
        self.results = {
            'new': [],           # Completely new outputs
            'duplicates': [],    # Potential duplicates with matches
            'exact': [],         # Exact matches (skip)
        }
        
    def compare_spreadsheet(self, spreadsheet_rows):
        """
        Compare each row from spreadsheet against database.
        
        Args:
            spreadsheet_rows: List of dicts with keys: 
                'title', 'all_authors', 'doi', 'publication_date', etc.
        
        Returns:
            dict with 'new', 'duplicates', 'exact' keys
        """
        for row in spreadsheet_rows:
            self._process_row(row)
        
        return self.results
    
    def _process_row(self, row):
        """Process a single spreadsheet row."""
        # First check for exact DOI match (most reliable)
        if row.get('doi'):
            doi_match = self._find_doi_match(row['doi'])
            if doi_match:
                self.results['exact'].append({
                    'spreadsheet_row': row,
                    'database_match': doi_match,
                    'match_type': 'doi',
                    'confidence': 1.0
                })
                return
        
        # Check for potential duplicates using multiple criteria
        potential_matches = self._find_potential_matches(row)
        
        if potential_matches:
            self.results['duplicates'].append({
                'spreadsheet_row': row,
                'potential_matches': potential_matches,
                'best_match': potential_matches[0] if potential_matches else None
            })
        else:
            self.results['new'].append({
                'spreadsheet_row': row
            })
    
    def _find_doi_match(self, doi):
        """Find exact DOI match in database."""
        if not doi:
            return None
        
        # Clean DOI
        doi_clean = doi.strip().lower()
        
        for output in self.db_outputs:
            if output.doi and output.doi.strip().lower() == doi_clean:
                return output
        return None
    
    def _find_potential_matches(self, row):
        """
        Find potential duplicate matches using multiple criteria.
        
        Returns sorted list of matches with confidence scores.
        """
        matches = []
        
        for db_output in self.db_outputs:
            confidence = self._calculate_match_confidence(row, db_output)
            
            if confidence > 0:
                matches.append({
                    'output': db_output,
                    'confidence': confidence,
                    'match_reasons': self._get_match_reasons(row, db_output, confidence)
                })
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Only return matches above a minimum threshold
        return [m for m in matches if m['confidence'] >= 0.3]
    
    def _calculate_match_confidence(self, row, db_output):
        """
        Calculate confidence score (0-1) that row matches db_output.
        
        Uses multiple signals:
        - Title similarity (weighted 0.5)
        - Author overlap (weighted 0.3)  
        - Date proximity (weighted 0.2)
        """
        confidence = 0.0
        
        # Title similarity
        title_sim = self._string_similarity(
            self._normalize_title(row.get('title', '')),
            self._normalize_title(db_output.title)
        )
        if title_sim > self.TITLE_SIMILARITY_THRESHOLD:
            confidence += title_sim * 0.5
        
        # Author overlap
        author_overlap = self._calculate_author_overlap(
            row.get('all_authors', ''),
            db_output.all_authors
        )
        if author_overlap > self.AUTHOR_OVERLAP_THRESHOLD:
            confidence += author_overlap * 0.3
        
        # Date proximity
        date_proximity = self._calculate_date_proximity(
            row.get('publication_date'),
            db_output.publication_date
        )
        if date_proximity > 0:
            confidence += date_proximity * 0.2
        
        return confidence
    
    def _get_match_reasons(self, row, db_output, confidence):
        """Get human-readable reasons why this is a potential match."""
        reasons = []
        
        title_sim = self._string_similarity(
            self._normalize_title(row.get('title', '')),
            self._normalize_title(db_output.title)
        )
        if title_sim > self.TITLE_SIMILARITY_THRESHOLD:
            reasons.append(f"Title {int(title_sim*100)}% similar")
        
        author_overlap = self._calculate_author_overlap(
            row.get('all_authors', ''),
            db_output.all_authors
        )
        if author_overlap > self.AUTHOR_OVERLAP_THRESHOLD:
            reasons.append(f"{int(author_overlap*100)}% author overlap")
        
        date_proximity = self._calculate_date_proximity(
            row.get('publication_date'),
            db_output.publication_date
        )
        if date_proximity > 0.5:
            reasons.append("Similar publication date")
        
        return reasons
    
    @staticmethod
    def _string_similarity(str1, str2):
        """Calculate similarity ratio between two strings (0-1)."""
        if not str1 or not str2:
            return 0.0
        return SequenceMatcher(None, str1, str2).ratio()
    
    @staticmethod
    def _normalize_title(title):
        """Normalize title for comparison."""
        if not title:
            return ""
        
        # Lowercase, remove punctuation, extra spaces
        title = title.lower()
        title = re.sub(r'[^\w\s]', '', title)
        title = re.sub(r'\s+', ' ', title)
        return title.strip()
    
    def _calculate_author_overlap(self, authors1, authors2):
        """
        Calculate overlap between two author lists.
        
        Returns ratio (0-1) of overlapping authors.
        """
        if not authors1 or not authors2:
            return 0.0
        
        # Split and normalize author names
        list1 = self._parse_authors(authors1)
        list2 = self._parse_authors(authors2)
        
        if not list1 or not list2:
            return 0.0
        
        # Find overlapping surnames (most reliable part)
        surnames1 = {self._get_surname(a) for a in list1}
        surnames2 = {self._get_surname(a) for a in list2}
        
        overlap = len(surnames1 & surnames2)
        total = max(len(surnames1), len(surnames2))
        
        return overlap / total if total > 0 else 0.0
    
    @staticmethod
    def _parse_authors(authors_string):
        """Parse author string into list of individual authors."""
        if not authors_string:
            return []
        
        # Handle different separators
        authors = authors_string.replace('//', ';').replace(';;', ';')
        authors = [a.strip() for a in authors.split(';') if a.strip()]
        
        return authors
    
    @staticmethod
    def _get_surname(full_name):
        """Extract and normalize surname from full name."""
        if not full_name:
            return ""
        
        # Typically last word is surname
        parts = full_name.strip().split()
        surname = parts[-1] if parts else ""
        
        # Normalize
        surname = surname.lower().strip('.,')
        return surname
    
    def _calculate_date_proximity(self, date1, date2):
        """
        Calculate how close two dates are.
        
        Returns 1.0 if same date, decreasing to 0 as dates diverge.
        """
        if not date1 or not date2:
            return 0.0
        
        # Parse if string
        if isinstance(date1, str):
            date1 = parse_date(date1)
        if isinstance(date2, str):
            date2 = parse_date(date2)
        
        if not date1 or not date2:
            return 0.0
        
        # Calculate days difference
        days_diff = abs((date1 - date2).days)
        
        if days_diff == 0:
            return 1.0
        elif days_diff <= self.DATE_PROXIMITY_DAYS:
            # Linear decay from 1.0 to 0.0 over DATE_PROXIMITY_DAYS
            return 1.0 - (days_diff / self.DATE_PROXIMITY_DAYS)
        else:
            return 0.0


def parse_csv_to_dict(csv_file):
    """
    Parse uploaded CSV file into list of dictionaries.
    
    Args:
        csv_file: Django UploadedFile object
    
    Returns:
        List of dicts with standardized keys
    """
    import csv
    import io
    
    # Decode file
    csv_text = csv_file.read().decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_text))
    
    rows = []
    for row in csv_reader:
        # Standardize keys (handle different CSV formats)
        standardized = {
            'title': row.get('title') or row.get('Title') or row.get('Proposed_Title', ''),
            'all_authors': row.get('all_authors') or row.get('Authors') or row.get('All_Authors', ''),
            'doi': row.get('doi') or row.get('DOI', ''),
            'publication_date': row.get('publication_date') or row.get('Publication_Date') or row.get('Proposed_Publication_Date', ''),
            'publication_venue': row.get('publication_venue') or row.get('Venue') or row.get('Proposed_Publisher_Journal', ''),
            'publication_type': row.get('publication_type') or row.get('Type') or row.get('Publication_Type', ''),
            'raw_row': row  # Keep original data
        }
        rows.append(standardized)
    
    return rows
