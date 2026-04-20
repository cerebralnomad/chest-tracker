"""
Database Manager for Total Battle Chest Tracker
Handles daily, weekly, and monthly chest tracking with automatic aggregation
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import json


class DatabaseManager:
    """Manage chest tracking databases with time-based aggregation"""
    
    def __init__(self, db_dir='databases'):
        self.db_dir = Path(db_dir)
        self.db_dir.mkdir(exist_ok=True)
        
        # Initialize current period databases
        self.daily_db = self._get_daily_db()
        self.weekly_db = self._get_weekly_db()
        self.monthly_db = self._get_monthly_db()
        
        self._init_databases()
        self._cleanup_old_databases()
    
    def _get_daily_db(self):
        """Get the current daily database path"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.db_dir / f"daily_{date_str}.db"
    
    def _get_weekly_db(self):
        """Get the current weekly database path"""
        # Week runs Monday 12:00 AM (midnight) to Sunday 11:59 PM
        # The week switches at Monday 12:00 AM (start of new week)
        now = datetime.now()
        
        # Get the Monday of current week
        # weekday() returns 0=Monday, 6=Sunday
        days_since_monday = now.weekday()
        week_start = now - timedelta(days=days_since_monday)
        
        # Use %W (Monday as first day) instead of %U (Sunday as first day)
        week_str = week_start.strftime("%Y-W%W")
        return self.db_dir / f"weekly_{week_str}.db"
    
    def _get_monthly_db(self):
        """Get the current monthly database path"""
        month_str = datetime.now().strftime("%Y-%m")
        return self.db_dir / f"monthly_{month_str}.db"
    
    def _init_databases(self):
        """Initialize database schemas"""
        for db_path in [self.daily_db, self.weekly_db, self.monthly_db]:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Player chests table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    chest_type TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            # Player summary table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS player_summary (
                    player_name TEXT PRIMARY KEY,
                    total_chests INTEGER DEFAULT 0,
                    chest_types TEXT,
                    last_updated TEXT
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_player ON chests(player_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON chests(timestamp)')
            
            conn.commit()
            conn.close()
    
    def add_chest(self, player_name, chest_type):
        """Add a chest to all relevant databases"""
        timestamp = datetime.now().isoformat()
        
        # Add to daily database
        self._add_to_db(self.daily_db, player_name, chest_type, timestamp)
        
        # Add to weekly database
        self._add_to_db(self.weekly_db, player_name, chest_type, timestamp)
        
        # Add to monthly database
        self._add_to_db(self.monthly_db, player_name, chest_type, timestamp)
        
        # Update summaries
        self._update_summary(self.daily_db, player_name)
        self._update_summary(self.weekly_db, player_name)
        self._update_summary(self.monthly_db, player_name)
    
    def _add_to_db(self, db_path, player_name, chest_type, timestamp):
        """Add a chest entry to a specific database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chests (player_name, chest_type, timestamp)
            VALUES (?, ?, ?)
        ''', (player_name, chest_type, timestamp))
        
        conn.commit()
        conn.close()
    
    def _update_summary(self, db_path, player_name=None):
        """Update player summary in a database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if player_name is None:
            # Update all players (for bulk corrections)
            cursor.execute('SELECT DISTINCT player_name FROM chests')
            players = [row[0] for row in cursor.fetchall()]
        else:
            players = [player_name]
        
        for pname in players:
            # Get total chests for player
            cursor.execute('''
                SELECT COUNT(*), GROUP_CONCAT(chest_type)
                FROM chests
                WHERE player_name = ?
            ''', (pname,))
            
            result = cursor.fetchone()
            total_chests = result[0]
            chest_types_str = result[1] if result[1] else ""
            
            # Count chest types
            chest_types_dict = {}
            if chest_types_str:
                for chest_type in chest_types_str.split(','):
                    chest_types_dict[chest_type] = chest_types_dict.get(chest_type, 0) + 1
            
            chest_types_json = json.dumps(chest_types_dict)
            
            # Update or insert summary
            cursor.execute('''
                INSERT OR REPLACE INTO player_summary (player_name, total_chests, chest_types, last_updated)
                VALUES (?, ?, ?, ?)
            ''', (pname, total_chests, chest_types_json, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_daily_stats(self):
        """Get statistics from daily database"""
        return self._get_stats(self.daily_db)
    
    def get_weekly_stats(self):
        """Get statistics from weekly database"""
        return self._get_stats(self.weekly_db)
    
    def get_monthly_stats(self):
        """Get statistics from monthly database"""
        return self._get_stats(self.monthly_db)
    
    def _get_stats(self, db_path):
        """Get statistics from a specific database"""
        if not db_path.exists():
            return {}
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT player_name, total_chests, chest_types FROM player_summary')
        results = cursor.fetchall()
        
        # List of chest name prefixes to filter out (OCR artifacts)
        chest_name_prefixes = [
            'Fire Chest', 'Stone Chest', 'Barbarian Chest', 'Bone Chest',
            'Cobra Chest', 'Orc Chest', 'Elegant Chest', 'Infernal Chest',
            'Mayan Chest', 'Gnome Workshop Chest', 'Gladiator\'s Chest'
        ]
        
        stats = {}
        for player_name, total_chests, chest_types_json in results:
            raw_chest_types = json.loads(chest_types_json) if chest_types_json else {}
            
            # Normalize chest types by extracting source portion (after " - ")
            # This groups "Barbarian Chest - Level 5 Crypt" and "Bone Chest - Level 5 Crypt" 
            # into a single "Level 5 Crypt" entry
            normalized_chest_types = {}
            for chest_type, count in raw_chest_types.items():
                # Skip obvious OCR garbage
                if (chest_type.startswith('From:') or 
                    chest_type in ['Clan', 'ar', 'lar', ''] or
                    len(chest_type) < 3):
                    continue
                
                # Skip standalone chest name prefixes (OCR picked up just the name without source)
                if chest_type in chest_name_prefixes:
                    continue
                
                # Extract source portion if format is "Name - Source"
                if " - " in chest_type:
                    normalized_name = chest_type.split(" - ", 1)[1]
                else:
                    normalized_name = chest_type
                
                # Add to normalized dict, combining counts
                if normalized_name in normalized_chest_types:
                    normalized_chest_types[normalized_name] += count
                else:
                    normalized_chest_types[normalized_name] = count
            
            stats[player_name] = {
                'total_chests': total_chests,
                'chest_types': normalized_chest_types,
                'total_points': 0  # Will be calculated by caller with point values
            }
        
        conn.close()
        return stats
    
    def get_detailed_stats(self, db_path, point_values):
        """Get detailed statistics with points calculation"""
        if not db_path.exists():
            return {}
        
        stats = self._get_stats(db_path)
        
        # Create case-insensitive lookup dictionary
        case_insensitive_points = {k.lower(): v for k, v in point_values.items()}
        
        # List of chest name prefixes to filter out (should match _get_stats)
        chest_name_prefixes = [
            'fire chest', 'stone chest', 'barbarian chest', 'bone chest',
            'cobra chest', 'orc chest', 'elegant chest', 'infernal chest',
            'mayan chest', 'gnome workshop chest', 'gladiator\'s chest'
        ]
        
        # Calculate points for each player
        for player_name, player_data in stats.items():
            total_points = 0
            for chest_type, count in player_data['chest_types'].items():
                # Skip obvious OCR garbage
                if (chest_type.startswith('From:') or 
                    chest_type in ['Clan', 'ar', 'lar'] or
                    chest_type.lower() in chest_name_prefixes):
                    print(f"DEBUG: Skipping OCR garbage: '{chest_type}'")
                    continue
                
                # Fix common OCR errors: letter O -> digit 0
                corrected_type = chest_type.replace(' 1o ', ' 10 ').replace(' 2o ', ' 20 ')
                corrected_type = corrected_type.replace('Level 1o ', 'Level 10 ')
                corrected_type = corrected_type.replace('Level 2o ', 'Level 20 ')
                corrected_type = corrected_type.replace('Level 10o ', 'Level 100 ')
                
                # Try case-insensitive match
                points = case_insensitive_points.get(corrected_type.lower(), None)
                
                # If no exact match, try to extract the source portion (after " - ")
                if points is None and " - " in corrected_type:
                    source_portion = corrected_type.split(" - ", 1)[1]
                    points = case_insensitive_points.get(source_portion.lower(), None)
                    if points:
                        print(f"DEBUG: Matched '{chest_type}' via source portion '{source_portion}' = {points}")
                
                # If still no match, try to match just the first part (before " - ")
                if points is None and " - " in corrected_type:
                    chest_name_portion = corrected_type.split(" - ", 1)[0]
                    points = case_insensitive_points.get(chest_name_portion.lower(), None)
                    if points:
                        print(f"DEBUG: Matched '{chest_type}' via chest name '{chest_name_portion}' = {points}")
                
                # Try fuzzy match for truncated text (e.g., "Ancien" -> "Ancient")
                if points is None:
                    for key, value in case_insensitive_points.items():
                        # Check if the key starts with the corrected type (truncation match)
                        if key.startswith(corrected_type.lower()) or corrected_type.lower().startswith(key):
                            points = value
                            print(f"DEBUG: Fuzzy matched '{chest_type}' to '{key}' = {points}")
                            break
                
                # Default to 10 points if no match found
                if points is None:
                    print(f"DEBUG: No match found for '{chest_type}', defaulting to 10 points")
                    points = 10
                else:
                    print(f"DEBUG: {player_name} - {chest_type} x{count} = {points} points each")
                
                total_points += points * count
            player_data['total_points'] = total_points
            print(f"DEBUG: {player_name} total points = {total_points}")
        
        return stats
    
    def get_all_chests(self, db_path):
        """Get all chest entries from a database"""
        if not db_path.exists():
            return []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT player_name, chest_type, timestamp FROM chests ORDER BY timestamp')
        results = cursor.fetchall()
        
        conn.close()
        
        return [
            {
                'player_name': r[0],
                'chest_type': r[1],
                'timestamp': r[2]
            }
            for r in results
        ]
    
    def _cleanup_old_databases(self):
        """Delete databases older than 1 month"""
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for db_file in self.db_dir.glob("*.db"):
            # Get file modification time
            mtime = datetime.fromtimestamp(db_file.stat().st_mtime)
            
            if mtime < cutoff_date:
                try:
                    db_file.unlink()
                    print(f"Deleted old database: {db_file}")
                except Exception as e:
                    print(f"Error deleting {db_file}: {e}")
    
    def export_to_json(self, db_path):
        """Export database to JSON format"""
        stats = self._get_stats(db_path)
        chests = self.get_all_chests(db_path)
        
        return {
            'summary': stats,
            'all_chests': chests,
            'exported_at': datetime.now().isoformat()
        }
