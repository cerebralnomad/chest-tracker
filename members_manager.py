"""
Members Manager for Total Battle Chest Tracker
Manages the master list of clan members
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


class MembersManager:
    """Manage clan member list and calculate their statistics"""
    
    def __init__(self):
        self.db_dir = Path("databases")
        self.db_dir.mkdir(exist_ok=True)
        self.db_path = self.db_dir / "members.db"
        self._init_db()
    
    def _init_db(self):
        """Initialize members database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                name TEXT PRIMARY KEY,
                date_added TEXT NOT NULL,
                added_by TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_member(self, name, added_by='manual'):
        """Add a member to the list"""
        if not name or not name.strip():
            return False
        
        name = name.strip()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO members (name, date_added, added_by, is_active)
                VALUES (?, ?, ?, 1)
            ''', (name, datetime.now().isoformat(), added_by))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Member already exists
            return False
        finally:
            conn.close()
    
    def remove_member(self, name):
        """Remove a member from the list"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM members WHERE name = ?', (name,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_all_members(self):
        """Get list of all members"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, date_added, added_by, is_active 
            FROM members 
            ORDER BY name
        ''')
        
        members = []
        for row in cursor.fetchall():
            members.append({
                'name': row[0],
                'date_added': row[1],
                'added_by': row[2],
                'is_active': row[3]
            })
        
        conn.close()
        return members
    
    def member_exists(self, name):
        """Check if a member exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM members WHERE name = ?', (name,))
        exists = cursor.fetchone()[0] > 0
        
        conn.close()
        return exists
    
    def get_member_stats(self, name, daily_db, weekly_db, monthly_db, last_weekly_db, point_values):
        """Calculate member statistics from chest databases"""
        stats = {
            'name': name,
            'daily_chests': 0,
            'weekly_chests': 0,
            'monthly_chests': 0,
            'daily_points': 0,
            'weekly_points': 0,
            'last_week_points': 0,
            'monthly_points': 0,
            'total_points': 0
        }
        
        # Get daily stats
        daily_data = self._get_chests_for_member(daily_db, name)
        stats['daily_chests'] = daily_data['count']
        stats['daily_points'] = self._calculate_points(daily_data['chests'], point_values)
        
        # Get weekly stats
        weekly_data = self._get_chests_for_member(weekly_db, name)
        stats['weekly_chests'] = weekly_data['count']
        stats['weekly_points'] = self._calculate_points(weekly_data['chests'], point_values)
        
        # Get last week stats
        if last_weekly_db:
            last_week_data = self._get_chests_for_member(last_weekly_db, name)
            stats['last_week_points'] = self._calculate_points(last_week_data['chests'], point_values)
        
        # Get monthly stats
        monthly_data = self._get_chests_for_member(monthly_db, name)
        stats['monthly_chests'] = monthly_data['count']
        stats['monthly_points'] = self._calculate_points(monthly_data['chests'], point_values)
        
        # Total points is monthly (cumulative for the month)
        stats['total_points'] = stats['monthly_points']
        
        return stats
    
    def get_member_detail(self, name, daily_db, weekly_db, monthly_db, last_weekly_db, point_values):
        """Get detailed member statistics including chest type breakdowns"""
        # Get basic stats
        stats = self.get_member_stats(name, daily_db, weekly_db, monthly_db, last_weekly_db, point_values)
        
        # Get detailed chest breakdowns (normalized by source)
        daily_data = self._get_chests_for_member(daily_db, name)
        weekly_data = self._get_chests_for_member(weekly_db, name)
        last_week_data = self._get_chests_for_member(last_weekly_db, name) if last_weekly_db and Path(last_weekly_db).exists() else {'count': 0, 'chests': []}
        monthly_data = self._get_chests_for_member(monthly_db, name)
        
        # Normalize chest types (extract source portion)
        stats['daily_chest_details'] = self._normalize_chest_types(daily_data['chests'])
        stats['weekly_chest_details'] = self._normalize_chest_types(weekly_data['chests'])
        stats['last_week_chest_details'] = self._normalize_chest_types(last_week_data['chests'])
        stats['monthly_chest_details'] = self._normalize_chest_types(monthly_data['chests'])
        
        return stats
    
    def _normalize_chest_types(self, chests):
        """Normalize chest types by extracting source portion and grouping"""
        normalized = {}
        for chest in chests:
            chest_type = chest['type']
            count = chest['count']
            
            # Extract source portion if format is "Name - Source"
            if " - " in chest_type:
                normalized_name = chest_type.split(" - ", 1)[1]
            else:
                normalized_name = chest_type
            
            # Combine counts for same normalized name
            if normalized_name in normalized:
                normalized[normalized_name] += count
            else:
                normalized[normalized_name] = count
        
        # Return sorted by count descending
        return sorted(normalized.items(), key=lambda x: x[1], reverse=True)
    
    def _get_chests_for_member(self, db_path, member_name):
        """Get chest count and types for a member from a database"""
        if not Path(db_path).exists():
            return {'count': 0, 'chests': []}
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT chest_type, COUNT(*) 
            FROM chests 
            WHERE player_name = ? 
            GROUP BY chest_type
        ''', (member_name,))
        
        chests = []
        total_count = 0
        for row in cursor.fetchall():
            chest_type = row[0]
            count = row[1]
            chests.append({'type': chest_type, 'count': count})
            total_count += count
        
        conn.close()
        return {'count': total_count, 'chests': chests}
    
    def _calculate_points(self, chests, point_values):
        """Calculate total points from chest list"""
        # Create case-insensitive lookup dictionary
        case_insensitive_points = {k.lower(): v for k, v in point_values.items()}
        
        total = 0
        for chest in chests:
            chest_type = chest['type']
            count = chest['count']
            
            # Try case-insensitive match first
            points = case_insensitive_points.get(chest_type.lower(), None)
            
            # If no exact match, try to extract the source portion (after " - ")
            if points is None and " - " in chest_type:
                source_portion = chest_type.split(" - ", 1)[1]
                points = case_insensitive_points.get(source_portion.lower(), None)
            
            # If still no match, try to match just the first part (before " - ")
            if points is None and " - " in chest_type:
                chest_name_portion = chest_type.split(" - ", 1)[0]
                points = case_insensitive_points.get(chest_name_portion.lower(), None)
            
            # Default to 10 points if no match found
            if points is None:
                points = 10
            
            total += points * count
        return total
    
    def get_all_member_stats(self, daily_db, weekly_db, monthly_db, point_values):
        """Get statistics for all members"""
        members = self.get_all_members()
        stats = []
        
        # Calculate last week's database path using same method as database
        from datetime import datetime, timedelta
        current_date = datetime.now()
        days_since_monday = current_date.weekday()
        this_week_start = current_date - timedelta(days=days_since_monday)
        last_week_start = this_week_start - timedelta(weeks=1)
        last_week_str = last_week_start.strftime("%Y-W%W")
        last_weekly_db = Path(weekly_db).parent / f"weekly_{last_week_str}.db"
        
        # Only use last week db if it exists
        last_weekly_db = str(last_weekly_db) if last_weekly_db.exists() else None
        
        for member in members:
            member_stats = self.get_member_stats(
                member['name'],
                daily_db,
                weekly_db,
                monthly_db,
                last_weekly_db,
                point_values
            )
            member_stats['added_by'] = member['added_by']
            stats.append(member_stats)
        
        # Sort by total points descending
        stats.sort(key=lambda x: x['total_points'], reverse=True)
        
        return stats
    
    def sync_with_databases(self, daily_db, weekly_db, monthly_db):
        """Auto-add any new members found in chest databases"""
        new_members = []
        
        # Get unique player names from all databases
        all_players = set()
        
        for db_path in [daily_db, weekly_db, monthly_db]:
            if Path(db_path).exists():
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT DISTINCT player_name FROM chests')
                players = [row[0] for row in cursor.fetchall()]
                all_players.update(players)
                conn.close()
        
        # Add any new players to member list
        for player in all_players:
            if not self.member_exists(player):
                if self.add_member(player, added_by='auto'):
                    new_members.append(player)
        
        return new_members
