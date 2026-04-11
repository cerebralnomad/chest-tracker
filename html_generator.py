"""
HTML Dashboard Generator for Total Battle Chest Tracker
Creates self-contained, uploadable HTML reports with charts and rankings
"""

from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json


class HTMLGenerator:
    """Generate beautiful HTML dashboards for chest statistics"""
    
    def __init__(self, db_manager, config_manager, output_dir='html_reports'):
        self.db = db_manager
        self.config = config_manager
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_daily_report(self):
        """Generate daily HTML report"""
        from datetime import timedelta
        
        current_date = datetime.now()
        date_str = current_date.strftime("%Y-%m-%d")
        filename = f"daily_report_{date_str}.html"
        
        # Calculate previous and next day
        prev_day = current_date - timedelta(days=1)
        next_day = current_date + timedelta(days=1)
        
        prev_day_str = prev_day.strftime("%Y-%m-%d")
        next_day_str = next_day.strftime("%Y-%m-%d")
        
        # Check if previous/next day reports exist
        prev_report_exists = (self.output_dir / f"daily_report_{prev_day_str}.html").exists()
        next_report_exists = (self.output_dir / f"daily_report_{next_day_str}.html").exists()
        
        point_values = self.config.get('points', {})
        stats = self.db.get_detailed_stats(self.db.daily_db, point_values)
        
        html = self._create_html(
            title=f"Daily Report - {date_str}",
            stats=stats,
            period_type="daily",
            navigation={
                'prev_link': f"daily_report_{prev_day_str}.html" if prev_report_exists else None,
                'next_link': f"daily_report_{next_day_str}.html" if next_report_exists else None,
                'prev_label': prev_day_str,
                'next_label': next_day_str
            }
        )
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def generate_weekly_report(self):
        """Generate weekly HTML report"""
        current_date = datetime.now()
        week_str = current_date.strftime("%Y-W%U")
        filename = f"weekly_report_{week_str}.html"
        
        # Calculate previous and next week dates
        from datetime import timedelta
        prev_week_date = current_date - timedelta(weeks=1)
        next_week_date = current_date + timedelta(weeks=1)
        
        prev_week_str = prev_week_date.strftime("%Y-W%U")
        next_week_str = next_week_date.strftime("%Y-W%U")
        
        # Check if previous/next week reports exist
        prev_report_exists = (self.output_dir / f"weekly_report_{prev_week_str}.html").exists()
        next_report_exists = (self.output_dir / f"weekly_report_{next_week_str}.html").exists()
        
        point_values = self.config.get('points', {})
        stats = self.db.get_detailed_stats(self.db.weekly_db, point_values)
        
        html = self._create_html(
            title=f"Weekly Report - Week {week_str}",
            stats=stats,
            period_type="weekly",
            navigation={
                'prev_link': f"weekly_report_{prev_week_str}.html" if prev_report_exists else None,
                'next_link': f"weekly_report_{next_week_str}.html" if next_report_exists else None,
                'prev_label': f"Week {prev_week_str}",
                'next_label': f"Week {next_week_str}"
            }
        )
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def generate_monthly_report(self):
        """Generate monthly HTML report"""
        from dateutil.relativedelta import relativedelta
        
        current_date = datetime.now()
        month_str = current_date.strftime("%Y-%m")
        filename = f"monthly_report_{month_str}.html"
        
        # Calculate previous and next month
        prev_month = current_date - relativedelta(months=1)
        next_month = current_date + relativedelta(months=1)
        
        prev_month_str = prev_month.strftime("%Y-%m")
        next_month_str = next_month.strftime("%Y-%m")
        
        # Check if previous/next month reports exist
        prev_report_exists = (self.output_dir / f"monthly_report_{prev_month_str}.html").exists()
        next_report_exists = (self.output_dir / f"monthly_report_{next_month_str}.html").exists()
        
        point_values = self.config.get('points', {})
        stats = self.db.get_detailed_stats(self.db.monthly_db, point_values)
        
        html = self._create_html(
            title=f"Monthly Report - {month_str}",
            stats=stats,
            period_type="monthly",
            navigation={
                'prev_link': f"monthly_report_{prev_month_str}.html" if prev_report_exists else None,
                'next_link': f"monthly_report_{next_month_str}.html" if next_report_exists else None,
                'prev_label': prev_month_str,
                'next_label': next_month_str
            }
        )
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def generate_index(self):
        """Generate index.html landing page"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        week_str = datetime.now().strftime("%Y-W%U")
        month_str = datetime.now().strftime("%Y-%m")
        
        # Get quick stats
        point_values = self.config.get('points', {})
        daily_stats = self.db.get_detailed_stats(self.db.daily_db, point_values)
        weekly_stats = self.db.get_detailed_stats(self.db.weekly_db, point_values)
        monthly_stats = self.db.get_detailed_stats(self.db.monthly_db, point_values)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="300">
    <title>Total Battle - Clan Chest Tracker</title>
    <style>
        {self._get_css()}
        .report-card {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            border: 2px solid rgba(255,255,255,0.1);
            transition: transform 0.3s ease;
        }}
        .report-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        }}
        .report-card h3 {{
            color: #ffd700;
            font-size: 1.8em;
            margin-bottom: 15px;
        }}
        .report-card p {{
            color: #e4e4e4;
            font-size: 1.1em;
            margin: 10px 0;
        }}
        .report-card a {{
            display: inline-block;
            background: #ffd700;
            color: #1a1a2e;
            padding: 12px 30px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 700;
            margin-top: 15px;
            transition: all 0.3s ease;
        }}
        .report-card a:hover {{
            background: #ffed4e;
            transform: scale(1.05);
        }}
        .auto-refresh {{
            text-align: center;
            color: rgba(255,255,255,0.6);
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="background-pattern"></div>
    
    <div class="container">
        <header class="header">
            <div class="title-section">
                <h1 class="main-title">⚔️ TOTAL BATTLE</h1>
                <h2 class="sub-title">[ACE] Clan Chest Tracker Dashboard</h2>
            </div>
            <div class="timestamp">Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </header>

        <div class="stats-overview">
            <div class="stat-card">
                <div class="stat-value">{len(daily_stats)}</div>
                <div class="stat-label">Contributors Today</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(p['total_chests'] for p in daily_stats.values())}</div>
                <div class="stat-label">Chests Today</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(p['total_points'] for p in daily_stats.values()):,}</div>
                <div class="stat-label">Points Today</div>
            </div>
        </div>

        <div class="report-card">
            <h3>📅 Today's Report</h3>
            <p><strong>Date:</strong> {date_str}</p>
            <p><strong>Active Members:</strong> {len(daily_stats)}</p>
            <p><strong>Total Chests:</strong> {sum(p['total_chests'] for p in daily_stats.values())}</p>
            <p><strong>Total Points:</strong> {sum(p['total_points'] for p in daily_stats.values()):,}</p>
            <a href="daily_report_{date_str}.html">View Daily Report →</a>
        </div>

        <div class="report-card">
            <h3>📊 This Week's Report</h3>
            <p><strong>Week:</strong> {week_str}</p>
            <p><strong>Active Members:</strong> {len(weekly_stats)}</p>
            <p><strong>Total Chests:</strong> {sum(p['total_chests'] for p in weekly_stats.values())}</p>
            <p><strong>Total Points:</strong> {sum(p['total_points'] for p in weekly_stats.values()):,}</p>
            <a href="weekly_report_{week_str}.html">View Weekly Report →</a>
        </div>

        <div class="report-card">
            <h3>📈 This Month's Report</h3>
            <p><strong>Month:</strong> {month_str}</p>
            <p><strong>Active Members:</strong> {len(monthly_stats)}</p>
            <p><strong>Total Chests:</strong> {sum(p['total_chests'] for p in monthly_stats.values())}</p>
            <p><strong>Total Points:</strong> {sum(p['total_points'] for p in monthly_stats.values()):,}</p>
            <a href="monthly_report_{month_str}.html">View Monthly Report →</a>
        </div>

        <div class="report-card">
            <h3>📊 Chest Point Values</h3>
            <p><strong>Reference:</strong> Point value for each chest type</p>
            <p>See how different chests contribute to your score and understand the ranking system.</p>
            <a href="point_values.html">View Point Values →</a>
        </div>

        <div class="auto-refresh">
            <p>⟳ This page auto-refreshes every 5 minutes</p>
        </div>

        <footer class="footer">
            <p>Total Battle Clan Chest Tracker • Updated automatically</p>
        </footer>
    </div>
</body>
</html>"""
        
        filepath = self.output_dir / "index.html"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def generate_members_report(self, members_manager):
        """Generate all member reports with different sort orders"""
        # Get member stats
        point_values = self.config.get('points', {})
        member_stats = members_manager.get_all_member_stats(
            self.db.daily_db,
            self.db.weekly_db,
            self.db.monthly_db,
            point_values
        )
        
        # Generate all 5 variants
        self._generate_members_html(member_stats, 'total', 'members_report.html', 'Total Chests')
        self._generate_members_html(member_stats, 'daily', 'members_report_today.html', 'Points Today')
        self._generate_members_html(member_stats, 'weekly', 'members_report_weekly.html', 'Points This Week')
        self._generate_members_html(member_stats, 'last_week', 'members_report_last_week.html', 'Points Last Week')
        self._generate_members_html(member_stats, 'monthly', 'members_report_monthly.html', 'Points This Month')
        
        # Generate individual member detail pages
        self._generate_member_detail_pages(members_manager, point_values)
    
    def _generate_member_detail_pages(self, members_manager, point_values):
        """Generate individual detail page for each member"""
        members = members_manager.get_all_members()
        
        # Get last week's database path
        last_week = datetime.now() - timedelta(weeks=1)
        last_week_str = last_week.strftime("%Y-W%U")
        last_weekly_db = self.db.db_dir / f"weekly_{last_week_str}.db"
        
        for member in members:
            member_name = member['name']
            
            # Get detailed stats
            detail = members_manager.get_member_detail(
                member_name,
                self.db.daily_db,
                self.db.weekly_db,
                self.db.monthly_db,
                str(last_weekly_db),
                point_values
            )
            
            # Generate HTML for this member
            self._generate_member_detail_html(detail)
    
    def _generate_member_detail_html(self, detail):
        """Generate HTML page for individual member"""
        member_name = detail['name']
        safe_name = member_name.replace(' ', '_').replace("'", "")
        filename = f"member_{safe_name}.html"
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{member_name} - Member Details</title>
    <style>
        {self._get_css()}
        .back-link {{
            display: inline-block;
            margin: 20px 0;
            padding: 12px 30px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffd700;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 700;
            transition: all 0.3s ease;
        }}
        .back-link:hover {{
            background: linear-gradient(135deg, #2a5298 0%, #3a72b8 100%);
            transform: translateY(-2px);
        }}
        .period-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .period-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #ffd700;
        }}
        .period-title {{
            color: #ffd700;
            font-size: 1.2em;
            font-weight: 700;
            margin-bottom: 15px;
        }}
        .stat-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}
        .stat-label {{
            color: #e4e4e4;
        }}
        .stat-value {{
            color: #4CAF50;
            font-weight: 700;
        }}
        .chest-breakdown {{
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
        }}
        .breakdown-title {{
            color: #ffd700;
            font-size: 1.1em;
            font-weight: 700;
            margin-bottom: 15px;
        }}
        .chest-list {{
            display: grid;
            gap: 8px;
        }}
        .chest-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 15px;
            background: rgba(0,0,0,0.3);
            border-radius: 5px;
        }}
        .chest-name {{
            color: #e4e4e4;
        }}
        .chest-count {{
            color: #ffd700;
            font-weight: 700;
        }}
    </style>
</head>
<body>
    <div class="background-pattern"></div>
    
    <div class="container">
        <header class="header">
            <div class="title-section">
                <h1 class="main-title">⚔️ {member_name}</h1>
                <h2 class="sub-title">Member Performance Details</h2>
            </div>
            <div class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </header>

        <a href="members_report.html" class="back-link">← Back to Members List</a>

        <div class="period-stats">
            <div class="period-card">
                <div class="period-title">📅 Today</div>
                <div class="stat-row">
                    <span class="stat-label">Chests:</span>
                    <span class="stat-value">{detail['daily_chests']}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Points:</span>
                    <span class="stat-value">{detail['daily_points']:,}</span>
                </div>
            </div>

            <div class="period-card">
                <div class="period-title">📊 This Week</div>
                <div class="stat-row">
                    <span class="stat-label">Chests:</span>
                    <span class="stat-value">{detail['weekly_chests']}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Points:</span>
                    <span class="stat-value">{detail['weekly_points']:,}</span>
                </div>
            </div>

            <div class="period-card">
                <div class="period-title">⏮️ Last Week</div>
                <div class="stat-row">
                    <span class="stat-label">Points:</span>
                    <span class="stat-value">{detail['last_week_points']:,}</span>
                </div>
            </div>

            <div class="period-card">
                <div class="period-title">📈 This Month</div>
                <div class="stat-row">
                    <span class="stat-label">Chests:</span>
                    <span class="stat-value">{detail['monthly_chests']}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Points:</span>
                    <span class="stat-value">{detail['monthly_points']:,}</span>
                </div>
            </div>
        </div>

        <div class="chest-breakdown">
            <div class="breakdown-title">🗃️ Today's Chest Breakdown</div>
            <div class="chest-list">
"""
        
        if detail['daily_chest_details']:
            for chest_type, count in detail['daily_chest_details']:
                html += f"""
                <div class="chest-item">
                    <span class="chest-name">{chest_type}</span>
                    <span class="chest-count">{count}</span>
                </div>
"""
        else:
            html += """
                <div class="chest-item">
                    <span class="chest-name" style="color: #999;">No chests today</span>
                </div>
"""
        
        html += """
            </div>
        </div>

        <div class="chest-breakdown">
            <div class="breakdown-title">🗃️ This Week's Chest Breakdown</div>
            <div class="chest-list">
"""
        
        if detail['weekly_chest_details']:
            for chest_type, count in detail['weekly_chest_details']:
                html += f"""
                <div class="chest-item">
                    <span class="chest-name">{chest_type}</span>
                    <span class="chest-count">{count}</span>
                </div>
"""
        else:
            html += """
                <div class="chest-item">
                    <span class="chest-name" style="color: #999;">No chests this week</span>
                </div>
"""
        
        html += """
            </div>
        </div>

        <div class="chest-breakdown">
            <div class="breakdown-title">🗃️ This Month's Chest Breakdown</div>
            <div class="chest-list">
"""
        
        if detail['monthly_chest_details']:
            for chest_type, count in detail['monthly_chest_details']:
                html += f"""
                <div class="chest-item">
                    <span class="chest-name">{chest_type}</span>
                    <span class="chest-count">{count}</span>
                </div>
"""
        else:
            html += """
                <div class="chest-item">
                    <span class="chest-name" style="color: #999;">No chests this month</span>
                </div>
"""
        
        html += """
            </div>
        </div>

        <footer class="footer">
            <p>[ACE] Clan Member Details • For Leadership Use Only</p>
        </footer>
    </div>
</body>
</html>"""
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def _generate_members_html(self, member_stats, sort_by, filename, title):
        """Generate a member report HTML file sorted by specified column"""
        # Sort member stats based on sort_by parameter
        if sort_by == 'daily':
            sorted_stats = sorted(member_stats, key=lambda x: x['daily_points'], reverse=True)
        elif sort_by == 'weekly':
            sorted_stats = sorted(member_stats, key=lambda x: x['weekly_points'], reverse=True)
        elif sort_by == 'last_week':
            sorted_stats = sorted(member_stats, key=lambda x: x['last_week_points'], reverse=True)
        elif sort_by == 'monthly':
            sorted_stats = sorted(member_stats, key=lambda x: x['monthly_points'], reverse=True)
        else:  # total chests
            sorted_stats = sorted(member_stats, key=lambda x: x['monthly_chests'], reverse=True)
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[ACE] Clan Members Report - {title}</title>
    <style>
        {self._get_css()}
        .members-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            overflow: hidden;
        }}
        .members-table th {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffd700;
            padding: 15px;
            text-align: left;
            font-weight: 700;
            border-bottom: 2px solid #ffd700;
        }}
        .members-table th a {{
            color: #ffd700;
            text-decoration: none;
            display: block;
            transition: all 0.3s ease;
        }}
        .members-table th a:hover {{
            color: #ffed4e;
            text-decoration: underline;
        }}
        .members-table th.active {{
            background: linear-gradient(135deg, #2a5298 0%, #3a72b8 100%);
        }}
        .members-table th.active a {{
            color: #ffffff;
            font-weight: 900;
        }}
        .members-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            color: #e4e4e4;
        }}
        .members-table td a {{
            color: #e4e4e4;
            text-decoration: none;
            transition: color 0.3s ease;
        }}
        .members-table td a:hover {{
            color: #ffd700;
            text-decoration: underline;
        }}
        .members-table tr:hover {{
            background: rgba(255,215,0,0.1);
        }}
        .members-table tr:nth-child(even) {{
            background: rgba(0,0,0,0.2);
        }}
        .rank-cell {{
            font-weight: 700;
            color: #ffd700;
            text-align: center;
        }}
        .rank-1 {{ color: #FFD700; font-size: 1.2em; }}
        .rank-2 {{ color: #C0C0C0; font-size: 1.1em; }}
        .rank-3 {{ color: #CD7F32; font-size: 1.1em; }}
        .points-cell {{
            font-weight: 700;
            color: #4CAF50;
        }}
    </style>
</head>
<body>
    <div class="background-pattern"></div>
    
    <div class="container">
        <header class="header">
            <div class="title-section">
                <h1 class="main-title">⚔️ TOTAL BATTLE</h1>
                <h2 class="sub-title">[ACE] Clan Members Report - Sorted by {title}</h2>
            </div>
            <div class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </header>

        <div class="stats-overview">
            <div class="stat-card">
                <div class="stat-value">{len(sorted_stats)}</div>
                <div class="stat-label">Total Members</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(1 for m in sorted_stats if m['daily_chests'] > 0)}</div>
                <div class="stat-label">Active Today</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(1 for m in sorted_stats if m['weekly_chests'] > 0)}</div>
                <div class="stat-label">Active This Week</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(m['monthly_points'] for m in sorted_stats):,}</div>
                <div class="stat-label">Total Points (Month)</div>
            </div>
        </div>

        <table class="members-table">
            <thead>
                <tr>
                    <th style="width: 60px;">Rank</th>
                    <th>Member Name</th>
                    <th style="width: 120px; text-align: center;" class="{'active' if sort_by == 'daily' else ''}">
                        <a href="members_report_today.html">Points Today</a>
                    </th>
                    <th style="width: 140px; text-align: center;" class="{'active' if sort_by == 'weekly' else ''}">
                        <a href="members_report_weekly.html">Points This Week</a>
                    </th>
                    <th style="width: 140px; text-align: center;" class="{'active' if sort_by == 'last_week' else ''}">
                        <a href="members_report_last_week.html">Points Last Week</a>
                    </th>
                    <th style="width: 150px; text-align: center;" class="{'active' if sort_by == 'monthly' else ''}">
                        <a href="members_report_monthly.html">Points This Month</a>
                    </th>
                    <th style="width: 120px; text-align: center;" class="{'active' if sort_by == 'total' else ''}">
                        <a href="members_report.html">Total Chests</a>
                    </th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add member rows
        for rank, member in enumerate(sorted_stats, 1):
            rank_class = f"rank-{rank}" if rank <= 3 else ""
            safe_name = member['name'].replace(' ', '_').replace("'", "")
            html += f"""
                <tr>
                    <td class="rank-cell {rank_class}">#{rank}</td>
                    <td><a href="member_{safe_name}.html">{member['name']}</a></td>
                    <td class="points-cell" style="text-align: center;">{member['daily_points']:,}</td>
                    <td class="points-cell" style="text-align: center;">{member['weekly_points']:,}</td>
                    <td class="points-cell" style="text-align: center;">{member['last_week_points']:,}</td>
                    <td class="points-cell" style="text-align: center;">{member['monthly_points']:,}</td>
                    <td style="text-align: center;">{member['monthly_chests']}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>

        <footer class="footer">
            <p>[ACE] Clan Members Report • For Leadership Use Only</p>
        </footer>
    </div>
</body>
</html>"""
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def generate_point_values_page(self):
        """Generate point values reference page for clan members"""
        point_values = self.config.get('points', {})
        chest_types = self.config.get('chest_types', [])
        
        # Use the order from chest_types config, filter to only those with point values set
        # Also include any point values not in chest_types list (append at end)
        sorted_items = []
        
        # First, add all chest types in config order that have point values
        for chest_type in chest_types:
            if chest_type in point_values:
                sorted_items.append((chest_type, point_values[chest_type]))
        
        # Then add any additional point values not in the chest_types list
        for chest_type, points in point_values.items():
            if chest_type not in chest_types:
                sorted_items.append((chest_type, points))
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[ACE] Chest Point Values</title>
    <style>
        {self._get_css()}
        .points-table {{
            width: 100%;
            max-width: 800px;
            margin: 30px auto;
            border-collapse: collapse;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            overflow: hidden;
        }}
        .points-table th {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffd700;
            padding: 15px;
            text-align: left;
            font-weight: 700;
            border-bottom: 2px solid #ffd700;
        }}
        .points-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            color: #e4e4e4;
        }}
        .points-table tr:hover {{
            background: rgba(255,215,0,0.1);
        }}
        .points-table tr:nth-child(even) {{
            background: rgba(0,0,0,0.2);
        }}
        .chest-name {{
            font-weight: 600;
        }}
        .point-value {{
            text-align: center;
            font-weight: 700;
            color: #4CAF50;
            font-size: 1.2em;
        }}
        .back-link {{
            display: inline-block;
            margin: 20px 0;
            padding: 12px 30px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #ffd700;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 700;
            transition: all 0.3s ease;
        }}
        .back-link:hover {{
            background: linear-gradient(135deg, #2a5298 0%, #3a72b8 100%);
            transform: translateY(-2px);
        }}
        .info-box {{
            background: rgba(255,215,0,0.1);
            border-left: 4px solid #ffd700;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .info-box p {{
            margin: 5px 0;
            color: #e4e4e4;
        }}
    </style>
</head>
<body>
    <div class="background-pattern"></div>
    
    <div class="container">
        <header class="header">
            <div class="title-section">
                <h1 class="main-title">⚔️ TOTAL BATTLE</h1>
                <h2 class="sub-title">[ACE] Chest Point Values</h2>
            </div>
            <div class="timestamp">Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </header>

        <a href="index.html" class="back-link">← Back to Dashboard</a>

        <div class="info-box">
            <p><strong>ℹ️ How Points Work:</strong></p>
            <p>Each chest type is worth a specific number of points. Your ranking on the leaderboards is based on total points earned, not just the number of chests.</p>
            <p>Higher-level chests are worth more points to reflect their greater value to the clan.</p>
        </div>

        <table class="points-table">
            <thead>
                <tr>
                    <th>Chest Type</th>
                    <th style="width: 150px; text-align: center;">Point Value</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # Add rows for each chest type
        for chest_type, points in sorted_items:
            html += f"""
                <tr>
                    <td class="chest-name">{chest_type}</td>
                    <td class="point-value">{points}</td>
                </tr>
"""
        
        # If no point values set yet
        if not sorted_items:
            html += """
                <tr>
                    <td colspan="2" style="text-align: center; padding: 30px; color: #999;">
                        No point values configured yet. Contact clan leadership for point value assignments.
                    </td>
                </tr>
"""
        
        html += f"""
            </tbody>
        </table>

        <div class="info-box">
            <p><strong>💡 Tips:</strong></p>
            <p>• Focus on higher-point chests when possible to maximize your contribution</p>
            <p>• Check the daily/weekly reports to see where you rank</p>
            <p>• Every chest counts toward the clan's success!</p>
        </div>

        <footer class="footer">
            <p>[ACE] Clan Chest Tracker • Point values set by clan leadership</p>
        </footer>
    </div>
</body>
</html>"""
        
        filepath = self.output_dir / "point_values.html"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def cleanup_old_reports(self):
        """Delete HTML reports older than 30 days"""
        cutoff_date = datetime.now() - timedelta(days=30)
        
        deleted_count = 0
        for html_file in self.output_dir.glob("*.html"):
            # Don't delete index.html, member reports, or point values page
            if html_file.name in ["index.html", "members_report.html", 
                                   "members_report_today.html", "members_report_weekly.html", 
                                   "members_report_last_week.html", "members_report_monthly.html", 
                                   "point_values.html"]:
                continue
            
            # Get file modification time
            mtime = datetime.fromtimestamp(html_file.stat().st_mtime)
            
            if mtime < cutoff_date:
                try:
                    html_file.unlink()
                    deleted_count += 1
                    print(f"Deleted old report: {html_file.name}")
                except Exception as e:
                    print(f"Error deleting {html_file}: {e}")
        
        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} old HTML report(s)")
        
        return deleted_count
    
    def _generate_navigation_html(self, navigation, title):
        """Generate navigation arrows HTML"""
        if not navigation:
            # No navigation, just show the period badge
            return f'<div class="period-badge">{title}</div>'
        
        prev_link = navigation.get('prev_link')
        next_link = navigation.get('next_link')
        prev_label = navigation.get('prev_label', 'Previous')
        next_label = navigation.get('next_label', 'Next')
        
        # Left arrow SVG
        left_arrow = '''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
        </svg>'''
        
        # Right arrow SVG
        right_arrow = '''<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
        </svg>'''
        
        # Generate previous arrow
        if prev_link:
            prev_html = f'<a href="{prev_link}" class="nav-arrow">{left_arrow}<span>← {prev_label}</span></a>'
        else:
            prev_html = f'<span class="nav-arrow disabled">{left_arrow}<span>← {prev_label}</span></span>'
        
        # Generate next arrow
        if next_link:
            next_html = f'<a href="{next_link}" class="nav-arrow"><span>{next_label} →</span>{right_arrow}</a>'
        else:
            next_html = f'<span class="nav-arrow disabled"><span>{next_label} →</span>{right_arrow}</span>'
        
        # Combine with period badge in the middle
        return f'''
            {prev_html}
            <div class="period-badge">{title}</div>
            {next_html}
        '''
    
    def _create_html(self, title, stats, period_type, navigation=None):
        """Create complete HTML document"""
        
        # Sort players by points
        sorted_players = sorted(
            stats.items(),
            key=lambda x: x[1]['total_points'],
            reverse=True
        )
        
        # Prepare data for charts
        chart_data = self._prepare_chart_data(sorted_players)
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Total Battle Clan Chest Tracker</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="background-pattern"></div>
    
    <div class="container">
        <header class="header">
            <div class="title-section">
                <h1 class="main-title">⚔️ TOTAL BATTLE</h1>
                <h2 class="sub-title">[ACE] Clan Chest Tracker</h2>
            </div>
            <div class="navigation-container">
                {self._generate_navigation_html(navigation, title)}
            </div>
            <div class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </header>

        <div class="stats-overview">
            <div class="stat-card">
                <div class="stat-value">{len(stats)}</div>
                <div class="stat-label">Active Members</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(p['total_chests'] for p in stats.values())}</div>
                <div class="stat-label">Total Chests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(p['total_points'] for p in stats.values()):,}</div>
                <div class="stat-label">Total Points</div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('rankings')">📊 Rankings</button>
            <button class="tab-btn" onclick="showTab('charts')">📈 Charts</button>
            <button class="tab-btn" onclick="showTab('detailed')">📋 Detailed Stats</button>
        </div>

        <div id="rankings" class="tab-content active">
            <div class="leaderboard">
                <h3 class="section-title">🏆 Top Contributors</h3>
                {self._generate_leaderboard(sorted_players)}
            </div>
        </div>

        <div id="charts" class="tab-content">
            <div class="charts-grid">
                <div class="chart-container">
                    <h3 class="chart-title">Points by Player</h3>
                    <canvas id="pointsChart"></canvas>
                </div>
                <div class="chart-container">
                    <h3 class="chart-title">Chests by Player</h3>
                    <canvas id="chestsChart"></canvas>
                </div>
                <div class="chart-container">
                    <h3 class="chart-title">Chest Type Distribution</h3>
                    <canvas id="typeChart"></canvas>
                </div>
                <div class="chart-container">
                    <h3 class="chart-title">Top 10 Contributors</h3>
                    <canvas id="topPlayersChart"></canvas>
                </div>
            </div>
        </div>

        <div id="detailed" class="tab-content">
            <h3 class="section-title">Detailed Player Statistics</h3>
            {self._generate_detailed_table(sorted_players)}
        </div>

        <footer class="footer">
            <p>Total Battle Clan Chest Tracker • Generated on {datetime.now().strftime("%B %d, %Y")}</p>
        </footer>
    </div>

    <script>
        {self._get_javascript(chart_data)}
    </script>
</body>
</html>"""
        
        return html
    
    def _get_css(self):
        """Generate CSS styling"""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e4e4e4;
            min-height: 100vh;
            position: relative;
            overflow-x: hidden;
        }

        .background-pattern {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(255,255,255,.02) 35px, rgba(255,255,255,.02) 70px),
                repeating-linear-gradient(-45deg, transparent, transparent 35px, rgba(255,255,255,.02) 35px, rgba(255,255,255,.02) 70px);
            pointer-events: none;
            z-index: 0;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            z-index: 1;
        }

        .header {
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #0f3460 0%, #533483 100%);
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            border: 2px solid rgba(255,255,255,0.1);
        }

        .title-section {
            margin-bottom: 20px;
        }

        .main-title {
            font-size: 3.5em;
            font-weight: 900;
            letter-spacing: 8px;
            text-transform: uppercase;
            background: linear-gradient(45deg, #ffd700, #ffed4e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 30px rgba(255,215,0,0.5);
            margin-bottom: 10px;
        }

        .sub-title {
            font-size: 1.5em;
            color: #b8b8d1;
            letter-spacing: 4px;
            font-weight: 300;
            text-transform: uppercase;
        }

        .period-badge {
            display: inline-block;
            background: rgba(255,255,255,0.15);
            padding: 12px 30px;
            border-radius: 50px;
            font-size: 1.2em;
            font-weight: 600;
            margin-top: 20px;
            border: 2px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
        }

        .timestamp {
            margin-top: 15px;
            color: rgba(255,255,255,0.6);
            font-size: 0.9em;
        }

        .navigation-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
        }

        .nav-arrow {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            border: 2px solid rgba(255,215,0,0.3);
            border-radius: 8px;
            color: #ffd700;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95em;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .nav-arrow:hover {
            background: linear-gradient(135deg, #2a5298 0%, #3a72b8 100%);
            border-color: #ffd700;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(255,215,0,0.3);
        }

        .nav-arrow.disabled {
            opacity: 0.3;
            pointer-events: none;
            cursor: not-allowed;
        }

        .nav-arrow svg {
            width: 16px;
            height: 16px;
            fill: currentColor;
        }

        .stats-overview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            border: 2px solid rgba(255,255,255,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0,0,0,0.4);
        }

        .stat-value {
            font-size: 3em;
            font-weight: 900;
            color: #ffd700;
            margin-bottom: 10px;
            text-shadow: 0 0 20px rgba(255,215,0,0.4);
        }

        .stat-label {
            font-size: 1.1em;
            color: #b8b8d1;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 600;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }

        .tab-btn {
            flex: 1;
            min-width: 150px;
            padding: 15px 25px;
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            color: #e4e4e4;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .tab-btn:hover {
            background: rgba(255,255,255,0.15);
            border-color: #ffd700;
            transform: translateY(-2px);
        }

        .tab-btn.active {
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
            color: #1a1a2e;
            border-color: #ffd700;
        }

        .tab-content {
            display: none;
            animation: fadeIn 0.5s ease;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .leaderboard {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 30px;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255,255,255,0.1);
        }

        .section-title {
            font-size: 2em;
            margin-bottom: 25px;
            color: #ffd700;
            text-transform: uppercase;
            letter-spacing: 3px;
            text-align: center;
        }

        .leaderboard-item {
            display: grid;
            grid-template-columns: 80px 1fr 120px 120px 120px;
            gap: 20px;
            align-items: center;
            padding: 20px;
            margin-bottom: 15px;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            border-left: 5px solid transparent;
            transition: all 0.3s ease;
        }

        .leaderboard-item:hover {
            background: rgba(255,255,255,0.1);
            transform: translateX(10px);
        }

        .leaderboard-item.rank-1 { border-left-color: #ffd700; }
        .leaderboard-item.rank-2 { border-left-color: #c0c0c0; }
        .leaderboard-item.rank-3 { border-left-color: #cd7f32; }

        .rank-badge {
            font-size: 2em;
            font-weight: 900;
            text-align: center;
        }

        .rank-1 .rank-badge { color: #ffd700; text-shadow: 0 0 20px rgba(255,215,0,0.6); }
        .rank-2 .rank-badge { color: #c0c0c0; text-shadow: 0 0 20px rgba(192,192,192,0.6); }
        .rank-3 .rank-badge { color: #cd7f32; text-shadow: 0 0 20px rgba(205,127,50,0.6); }

        .player-name {
            font-size: 1.3em;
            font-weight: 600;
            color: #ffffff;
        }

        .stat-box {
            text-align: center;
        }

        .stat-box-value {
            font-size: 1.5em;
            font-weight: 700;
            color: #ffd700;
        }

        .stat-box-label {
            font-size: 0.85em;
            color: #b8b8d1;
            text-transform: uppercase;
            margin-top: 5px;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
        }

        .chart-container {
            background: rgba(255,255,255,0.05);
            padding: 25px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255,255,255,0.1);
        }

        .chart-title {
            text-align: center;
            margin-bottom: 20px;
            color: #ffd700;
            font-size: 1.3em;
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        .detailed-table {
            width: 100%;
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            overflow: hidden;
            border: 2px solid rgba(255,255,255,0.1);
        }

        .detailed-table table {
            width: 100%;
            border-collapse: collapse;
        }

        .detailed-table th {
            background: linear-gradient(135deg, #0f3460 0%, #533483 100%);
            padding: 18px;
            text-align: left;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: #ffd700;
            border-bottom: 3px solid #ffd700;
        }

        .detailed-table td {
            padding: 18px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            color: #e4e4e4;
        }

        .detailed-table tr:hover {
            background: rgba(255,255,255,0.08);
        }

        .chest-breakdown {
            font-size: 0.9em;
            color: #b8b8d1;
            line-height: 1.6;
        }

        .footer {
            text-align: center;
            padding: 30px;
            margin-top: 50px;
            color: rgba(255,255,255,0.5);
            border-top: 1px solid rgba(255,255,255,0.1);
        }

        @media (max-width: 768px) {
            .main-title { font-size: 2em; }
            .leaderboard-item {
                grid-template-columns: 1fr;
                text-align: center;
            }
            .charts-grid {
                grid-template-columns: 1fr;
            }
        }
        """
    
    def _generate_leaderboard(self, sorted_players):
        """Generate leaderboard HTML"""
        html = ""
        
        for i, (player_name, data) in enumerate(sorted_players, 1):  # Show ALL players
            rank_class = f"rank-{i}" if i <= 3 else ""
            
            html += f"""
            <div class="leaderboard-item {rank_class}">
                <div class="rank-badge">#{i}</div>
                <div class="player-name">{player_name}</div>
                <div class="stat-box">
                    <div class="stat-box-value">{data['total_chests']}</div>
                    <div class="stat-box-label">Chests</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-value">{data['total_points']:,}</div>
                    <div class="stat-box-label">Points</div>
                </div>
                <div class="stat-box">
                    <div class="stat-box-value">{len(data['chest_types'])}</div>
                    <div class="stat-box-label">Types</div>
                </div>
            </div>
            """
        
        return html
    
    def _generate_detailed_table(self, sorted_players):
        """Generate detailed statistics table"""
        html = '<div class="detailed-table"><table>'
        html += """
        <thead>
            <tr>
                <th>Rank</th>
                <th>Player Name</th>
                <th>Total Chests</th>
                <th>Total Points</th>
                <th>Chest Types</th>
            </tr>
        </thead>
        <tbody>
        """
        
        for i, (player_name, data) in enumerate(sorted_players, 1):
            chest_breakdown = "<br>".join(
                f"{chest_type}: {count}"
                for chest_type, count in sorted(
                    data['chest_types'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            )
            
            html += f"""
            <tr>
                <td><strong>#{i}</strong></td>
                <td><strong>{player_name}</strong></td>
                <td>{data['total_chests']}</td>
                <td>{data['total_points']:,}</td>
                <td class="chest-breakdown">{chest_breakdown if chest_breakdown else 'No chests'}</td>
            </tr>
            """
        
        html += "</tbody></table></div>"
        return html
    
    def _prepare_chart_data(self, sorted_players):
        """Prepare data for Chart.js"""
        # Top 10 players for charts
        top_players = sorted_players[:10]
        
        player_names = [p[0] for p in top_players]
        total_chests = [p[1]['total_chests'] for p in top_players]
        total_points = [p[1]['total_points'] for p in top_players]
        
        # Chest type distribution (all players)
        chest_type_totals = {}
        for _, data in sorted_players:
            for chest_type, count in data['chest_types'].items():
                chest_type_totals[chest_type] = chest_type_totals.get(chest_type, 0) + count
        
        return {
            'player_names': player_names,
            'total_chests': total_chests,
            'total_points': total_points,
            'chest_types': list(chest_type_totals.keys()),
            'chest_type_counts': list(chest_type_totals.values())
        }
    
    def _get_javascript(self, chart_data):
        """Generate JavaScript for charts and interactions"""
        return f"""
        // Tab switching
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}

        // Chart configuration
        Chart.defaults.color = '#e4e4e4';
        Chart.defaults.borderColor = 'rgba(255,255,255,0.1)';

        const chartColors = [
            '#ffd700', '#ff6b6b', '#4ecdc4', '#45b7d1', '#f7b731',
            '#5f27cd', '#00d2d3', '#1dd1a1', '#feca57', '#ee5a6f'
        ];

        // Points by Player Chart
        new Chart(document.getElementById('pointsChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(chart_data['player_names'])},
                datasets: [{{
                    label: 'Total Points',
                    data: {json.dumps(chart_data['total_points'])},
                    backgroundColor: chartColors[0],
                    borderColor: chartColors[0],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12,
                        titleFont: {{ size: 14, weight: 'bold' }},
                        bodyFont: {{ size: 13 }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    x: {{
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});

        // Chests by Player Chart
        new Chart(document.getElementById('chestsChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(chart_data['player_names'])},
                datasets: [{{
                    label: 'Total Chests',
                    data: {json.dumps(chart_data['total_chests'])},
                    backgroundColor: chartColors[1],
                    borderColor: chartColors[1],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12,
                        titleFont: {{ size: 14, weight: 'bold' }},
                        bodyFont: {{ size: 13 }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    x: {{
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});

        // Chest Type Distribution Chart
        new Chart(document.getElementById('typeChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(chart_data['chest_types'])},
                datasets: [{{
                    data: {json.dumps(chart_data['chest_type_counts'])},
                    backgroundColor: chartColors,
                    borderWidth: 3,
                    borderColor: '#1a1a2e'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'right',
                        labels: {{
                            padding: 15,
                            font: {{ size: 12 }}
                        }}
                    }},
                    tooltip: {{
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12,
                        titleFont: {{ size: 14, weight: 'bold' }},
                        bodyFont: {{ size: 13 }}
                    }}
                }}
            }}
        }});

        // Top Players Horizontal Bar Chart
        new Chart(document.getElementById('topPlayersChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(chart_data['player_names'])},
                datasets: [{{
                    label: 'Points',
                    data: {json.dumps(chart_data['total_points'])},
                    backgroundColor: chartColors.slice(0, 10),
                    borderWidth: 0
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12,
                        titleFont: {{ size: 14, weight: 'bold' }},
                        bodyFont: {{ size: 13 }}
                    }}
                }},
                scales: {{
                    x: {{
                        beginAtZero: true,
                        grid: {{ color: 'rgba(255,255,255,0.1)' }}
                    }},
                    y: {{
                        grid: {{ display: false }}
                    }}
                }}
            }}
        }});
        """
