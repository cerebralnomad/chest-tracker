"""
HTML Dashboard Generator for Total Battle Chest Tracker
Creates self-contained, uploadable HTML reports with charts and rankings
"""

from pathlib import Path
from datetime import datetime, timedelta
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
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"daily_report_{date_str}.html"
        
        point_values = self.config.get('points', {})
        stats = self.db.get_detailed_stats(self.db.daily_db, point_values)
        
        html = self._create_html(
            title=f"Daily Report - {date_str}",
            stats=stats,
            period_type="daily"
        )
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def generate_weekly_report(self):
        """Generate weekly HTML report"""
        week_str = datetime.now().strftime("%Y-W%U")
        filename = f"weekly_report_{week_str}.html"
        
        point_values = self.config.get('points', {})
        stats = self.db.get_detailed_stats(self.db.weekly_db, point_values)
        
        html = self._create_html(
            title=f"Weekly Report - Week {week_str}",
            stats=stats,
            period_type="weekly"
        )
        
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def generate_monthly_report(self):
        """Generate monthly HTML report"""
        month_str = datetime.now().strftime("%Y-%m")
        filename = f"monthly_report_{month_str}.html"
        
        point_values = self.config.get('points', {})
        stats = self.db.get_detailed_stats(self.db.monthly_db, point_values)
        
        html = self._create_html(
            title=f"Monthly Report - {month_str}",
            stats=stats,
            period_type="monthly"
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
    
    def cleanup_old_reports(self):
        """Delete HTML reports older than 30 days"""
        cutoff_date = datetime.now() - timedelta(days=30)
        
        deleted_count = 0
        for html_file in self.output_dir.glob("*.html"):
            # Don't delete index.html
            if html_file.name == "index.html":
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
    
    def _create_html(self, title, stats, period_type):
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
            <div class="period-badge">{title}</div>
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
