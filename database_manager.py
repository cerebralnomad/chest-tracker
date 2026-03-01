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
        # Week starts Monday 12am, ends Sunday 12pm
        now = datetime.now()
        
        # If it's Sunday after noon, this is still previous week
        if now.weekday() == 6 and now.hour >= 12:
            # Use next Monday as week start
            days_ahead = 1
            week_start = now + timedelta(days=days_ahead)
        else:
            # Get the Monday of current week
            days_since_monday = now.weekday()
            week_start = now - timedelta(days=days_since_monday)
        
        week_str = week_start.strftime("%Y-W%U")
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
    
    def _update_summary(self, db_path, player_name):
        """Update player summary in a database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total chests for player
        cursor.execute('''
            SELECT COUNT(*), GROUP_CONCAT(chest_type)
            FROM chests
            WHERE player_name = ?
        ''', (player_name,))
        
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
        ''', (player_name, total_chests, chest_types_json, datetime.now().isoformat()))
        
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
        
        stats = {}
        for player_name, total_chests, chest_types_json in results:
            chest_types = json.loads(chest_types_json) if chest_types_json else {}
            
            stats[player_name] = {
                'total_chests': total_chests,
                'chest_types': chest_types,
                'total_points': 0  # Will be calculated by caller with point values
            }
        
        conn.close()
        return stats
    
    def get_detailed_stats(self, db_path, point_values):
        """Get detailed statistics with points calculation"""
        if not db_path.exists():
            return {}
        
        stats = self._get_stats(db_path)
        
        # Calculate points for each player
        for player_data in stats.values():
            total_points = 0
            for chest_type, count in player_data['chest_types'].items():
                points = point_values.get(chest_type, 10)  # Default 10 points
                total_points += points * count
            player_data['total_points'] = total_points
        
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
