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
    
    def get_member_stats(self, name, daily_db, weekly_db, monthly_db, point_values):
        """Calculate member statistics from chest databases"""
        stats = {
            'name': name,
            'daily_chests': 0,
            'weekly_chests': 0,
            'monthly_chests': 0,
            'daily_points': 0,
            'weekly_points': 0,
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
        
        # Get monthly stats
        monthly_data = self._get_chests_for_member(monthly_db, name)
        stats['monthly_chests'] = monthly_data['count']
        stats['monthly_points'] = self._calculate_points(monthly_data['chests'], point_values)
        
        # Total points is monthly (cumulative for the month)
        stats['total_points'] = stats['monthly_points']
        
        return stats
    
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
        total = 0
        for chest in chests:
            chest_type = chest['type']
            count = chest['count']
            points = point_values.get(chest_type, 10)  # Default 10 points
            total += points * count
        return total
    
    def get_all_member_stats(self, daily_db, weekly_db, monthly_db, point_values):
        """Get statistics for all members"""
        members = self.get_all_members()
        stats = []
        
        for member in members:
            member_stats = self.get_member_stats(
                member['name'],
                daily_db,
                weekly_db,
                monthly_db,
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
