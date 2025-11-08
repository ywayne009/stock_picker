"""
Strategy Charts and Visualization

Main visualization class for creating interactive charts for trading strategies.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any, Union
import webbrowser
from pathlib import Path
import subprocess
import platform
import os

from .chart_themes import (
    get_theme,
    get_candlestick_colors,
    get_signal_marker_style,
    get_ma_line_style,
    get_metric_color,
    get_chart_size,
    COLORS
)
from .performance_metrics import PerformanceMetrics, calculate_metrics


def is_wsl() -> bool:
    """Check if running in WSL (Windows Subsystem for Linux)."""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower()
    except:
        return False


def open_browser_wsl(filepath: str) -> bool:
    """
    Open a file in the default Windows browser from WSL.

    Args:
        filepath: Path to the HTML file (Linux path)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert WSL path to Windows path
        result = subprocess.run(
            ['wslpath', '-w', filepath],
            capture_output=True,
            text=True,
            check=True
        )
        windows_path = result.stdout.strip()

        # Open in Windows default browser
        # cmd.exe /c start "" "path" - the empty "" is for the window title
        subprocess.run(
            ['cmd.exe', '/c', 'start', '', windows_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except Exception as e:
        print(f"Warning: Could not auto-open browser in WSL: {e}")
        print(f"Please manually open: {filepath}")
        return False


def open_in_browser(filepath: str) -> None:
    """
    Open HTML file in browser, with WSL2 support.

    Args:
        filepath: Path to the HTML file
    """
    abs_path = str(Path(filepath).absolute())

    if is_wsl():
        # WSL environment - use Windows browser
        open_browser_wsl(abs_path)
    else:
        # Normal Linux/Mac/Windows
        webbrowser.open('file://' + abs_path)


class StrategyVisualizer:
    """
    Interactive chart visualizer for trading strategies.

    Provides methods to create various charts including:
    - Price charts with signals
    - Equity curves
    - Performance metrics dashboards
    - Strategy comparisons
    """

    def __init__(self, theme: str = 'dark', chart_size: str = 'medium'):
        """
        Initialize the visualizer.

        Args:
            theme: 'dark' or 'light' (default: 'dark')
            chart_size: 'small', 'medium', 'large', or 'dashboard'
        """
        self.theme = theme
        self.chart_size = chart_size
        self.theme_config = get_theme(theme)
        self.size_config = get_chart_size(chart_size)

    def plot_price_and_signals(
        self,
        data: pd.DataFrame,
        signals: pd.DataFrame,
        strategy_name: str = "Strategy",
        show_volume: bool = True
    ) -> go.Figure:
        """
        Create interactive price chart with moving averages and trade signals.

        Args:
            data: Original OHLCV DataFrame
            signals: DataFrame with signals, MA lines, and positions
            strategy_name: Name for chart title
            show_volume: Whether to show volume subplot

        Returns:
            Plotly Figure object
        """
        # Create subplots
        if show_volume:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.7, 0.3],
                subplot_titles=(f'{strategy_name} - Price & Signals', 'Volume')
            )
        else:
            fig = go.Figure()

        # Add candlestick chart
        candlestick_colors = get_candlestick_colors(self.theme)
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['open'],
                high=data['high'],
                low=data['low'],
                close=data['close'],
                name='Price',
                increasing=candlestick_colors['increasing'],
                decreasing=candlestick_colors['decreasing']
            ),
            row=1, col=1
        )

        # Add moving averages if present
        if 'fast_ma' in signals.columns:
            fast_ma_style = get_ma_line_style('fast')
            fig.add_trace(
                go.Scatter(
                    x=signals.index,
                    y=signals['fast_ma'],
                    mode='lines',
                    name='Fast MA',
                    line=fast_ma_style
                ),
                row=1, col=1
            )

        if 'slow_ma' in signals.columns:
            slow_ma_style = get_ma_line_style('slow')
            fig.add_trace(
                go.Scatter(
                    x=signals.index,
                    y=signals['slow_ma'],
                    mode='lines',
                    name='Slow MA',
                    line=slow_ma_style
                ),
                row=1, col=1
            )

        # Add buy signals
        buy_signals = signals[signals['signal'] == 1]
        if len(buy_signals) > 0:
            buy_marker = get_signal_marker_style('buy')
            fig.add_trace(
                go.Scatter(
                    x=buy_signals.index,
                    y=buy_signals['close'],
                    mode='markers',
                    name='Buy Signal',
                    marker=buy_marker,
                    hovertemplate='<b>BUY</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )

        # Add sell signals
        sell_signals = signals[signals['signal'] == -1]
        if len(sell_signals) > 0:
            sell_marker = get_signal_marker_style('sell')
            fig.add_trace(
                go.Scatter(
                    x=sell_signals.index,
                    y=sell_signals['close'],
                    mode='markers',
                    name='Sell Signal',
                    marker=sell_marker,
                    hovertemplate='<b>SELL</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )

        # Add volume if requested
        if show_volume:
            colors = [COLORS['bullish'] if close >= open_price else COLORS['bearish']
                     for close, open_price in zip(data['close'], data['open'])]

            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.5
                ),
                row=2, col=1
            )

        # Update layout
        layout_config = self.theme_config.copy()
        layout_config['title']['text'] = f'{strategy_name} - Price & Signals'

        fig.update_layout(
            **layout_config,
            xaxis_title='Date',
            yaxis_title='Price ($)',
            height=self.size_config['height'],
            width=self.size_config['width'],
            xaxis_rangeslider_visible=False
        )

        # Add range selector
        fig.update_xaxes(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1M", step="month", stepmode="backward"),
                    dict(count=3, label="3M", step="month", stepmode="backward"),
                    dict(count=6, label="6M", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ]),
                bgcolor=COLORS['grid_dark'] if self.theme == 'dark' else COLORS['grid_light']
            )
        )

        return fig

    def plot_equity_curve(
        self,
        signals: pd.DataFrame,
        initial_capital: float = 100000.0,
        benchmark: Optional[pd.DataFrame] = None,
        strategy_name: str = "Strategy"
    ) -> go.Figure:
        """
        Create equity curve chart showing portfolio value over time.

        Args:
            signals: DataFrame with signals and positions
            initial_capital: Starting capital
            benchmark: Optional benchmark data for comparison
            strategy_name: Name for chart title

        Returns:
            Plotly Figure object
        """
        # Calculate portfolio value
        portfolio_df = self._calculate_portfolio_history(signals, initial_capital)

        # Create figure
        fig = go.Figure()

        # Add equity curve
        fig.add_trace(
            go.Scatter(
                x=portfolio_df.index,
                y=portfolio_df['portfolio_value'],
                mode='lines',
                name=strategy_name,
                line=dict(color=COLORS['ma_fast'], width=2),
                fill='tonexty',
                fillcolor=f"rgba(33, 150, 243, 0.1)",
                hovertemplate='Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>'
            )
        )

        # Add benchmark if provided
        if benchmark is not None:
            fig.add_trace(
                go.Scatter(
                    x=benchmark.index,
                    y=benchmark['close'] / benchmark['close'].iloc[0] * initial_capital,
                    mode='lines',
                    name='Buy & Hold',
                    line=dict(color=COLORS['neutral'], width=2, dash='dash'),
                    hovertemplate='Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>'
                )
            )

        # Calculate and add drawdown
        drawdown = self._calculate_drawdown_series(portfolio_df['portfolio_value'])

        # Add drawdown as shaded area
        fig.add_trace(
            go.Scatter(
                x=portfolio_df.index,
                y=portfolio_df['portfolio_value'] * (1 + drawdown),
                mode='lines',
                name='Drawdown',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            )
        )

        # Shade drawdown periods
        fig.add_trace(
            go.Scatter(
                x=portfolio_df.index,
                y=portfolio_df['portfolio_value'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(239, 83, 80, 0.2)',
                name='Drawdown',
                hovertemplate='Drawdown: %{customdata:.1f}%<extra></extra>',
                customdata=drawdown * 100
            )
        )

        # Update layout
        layout_config = self.theme_config.copy()
        layout_config['title']['text'] = f'{strategy_name} - Equity Curve'

        fig.update_layout(
            **layout_config,
            xaxis_title='Date',
            yaxis_title='Portfolio Value ($)',
            height=self.size_config['height'],
            width=self.size_config['width']
        )

        return fig

    def plot_performance_metrics(
        self,
        metrics: Union[PerformanceMetrics, Dict[str, Any]],
        strategy_name: str = "Strategy"
    ) -> go.Figure:
        """
        Create performance metrics dashboard.

        Args:
            metrics: PerformanceMetrics object or metrics dictionary
            strategy_name: Name for chart title

        Returns:
            Plotly Figure object
        """
        # Convert to dict if needed
        if isinstance(metrics, PerformanceMetrics):
            metrics_dict = metrics.to_dict()
        else:
            metrics_dict = metrics

        # Create subplots
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=(
                'Total Return', 'Win Rate', 'Profit Factor',
                'Sharpe Ratio', 'Max Drawdown', 'Total Trades',
                'Average Trade', 'Volatility', 'CAGR'
            ),
            specs=[
                [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}],
                [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}],
                [{'type': 'indicator'}, {'type': 'indicator'}, {'type': 'indicator'}]
            ],
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )

        # Define metrics to display
        metric_configs = [
            ('total_return_pct', '%', 1, 1, True),
            ('win_rate_pct', '%', 1, 2, True),
            ('profit_factor', '', 1, 3, True),
            ('sharpe_ratio', '', 2, 1, True),
            ('max_drawdown_pct', '%', 2, 2, False),
            ('total_trades', '', 2, 3, True),
            ('average_trade', '$', 3, 1, True),
            ('volatility_pct', '%', 3, 2, False),
            ('cagr_pct', '%', 3, 3, True)
        ]

        # Add indicators
        for metric_key, suffix, row, col, higher_is_better in metric_configs:
            value = metrics_dict.get(metric_key, 0)
            color = get_metric_color(value, higher_is_better)

            fig.add_trace(
                go.Indicator(
                    mode='number',
                    value=value,
                    number={'suffix': suffix, 'font': {'size': 28}},
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'font': {'size': 14}},
                    number_font_color=color
                ),
                row=row, col=col
            )

        # Update layout
        layout_config = self.theme_config.copy()
        layout_config['title']['text'] = f'{strategy_name} - Performance Metrics'

        fig.update_layout(
            **layout_config,
            height=self.size_config['height'],
            width=self.size_config['width'],
            showlegend=False
        )

        return fig

    def plot_strategy_comparison(
        self,
        strategies: List[Dict[str, Any]],
        initial_capital: float = 100000.0
    ) -> go.Figure:
        """
        Create comparison chart for multiple strategies.

        Args:
            strategies: List of dicts with 'name', 'results', and optionally 'metrics'
            initial_capital: Starting capital

        Returns:
            Plotly Figure object
        """
        # Create subplots
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.15,
            row_heights=[0.6, 0.4],
            subplot_titles=('Equity Curves Comparison', 'Metrics Comparison')
        )

        colors = [COLORS['ma_fast'], COLORS['ma_slow'], COLORS['purple'], COLORS['cyan']]

        # Add equity curves
        for idx, strategy in enumerate(strategies):
            portfolio_df = self._calculate_portfolio_history(
                strategy['results'],
                initial_capital
            )

            color = colors[idx % len(colors)]

            fig.add_trace(
                go.Scatter(
                    x=portfolio_df.index,
                    y=portfolio_df['portfolio_value'],
                    mode='lines',
                    name=strategy['name'],
                    line=dict(color=color, width=2),
                    hovertemplate=f"{strategy['name']}<br>Value: $%{{y:,.2f}}<extra></extra>"
                ),
                row=1, col=1
            )

        # Add metrics comparison if provided
        if all('metrics' in s for s in strategies):
            metrics_to_compare = ['total_return_pct', 'sharpe_ratio', 'max_drawdown_pct', 'win_rate_pct']
            x_labels = [s['name'] for s in strategies]

            for metric_key in metrics_to_compare:
                values = []
                for strategy in strategies:
                    metrics = strategy['metrics']
                    if isinstance(metrics, PerformanceMetrics):
                        metrics = metrics.to_dict()
                    values.append(metrics.get(metric_key, 0))

                fig.add_trace(
                    go.Bar(
                        x=x_labels,
                        y=values,
                        name=metric_key.replace('_', ' ').title(),
                        hovertemplate='%{x}<br>%{y:.2f}<extra></extra>'
                    ),
                    row=2, col=1
                )

        # Update layout
        layout_config = self.theme_config.copy()
        layout_config['title']['text'] = 'Strategy Comparison'

        fig.update_layout(
            **layout_config,
            height=self.size_config['height'],
            width=self.size_config['width'],
            barmode='group'
        )

        fig.update_yaxes(title_text="Portfolio Value ($)", row=1, col=1)
        fig.update_yaxes(title_text="Metric Value", row=2, col=1)
        fig.update_xaxes(title_text="Strategy", row=2, col=1)

        return fig

    def create_dashboard(
        self,
        data: pd.DataFrame,
        signals: pd.DataFrame,
        metrics: Union[PerformanceMetrics, Dict[str, Any]],
        strategy_name: str = "Strategy",
        output_path: Optional[str] = None,
        auto_open: bool = True
    ) -> str:
        """
        Create a complete dashboard with all charts combined.

        Args:
            data: Original OHLCV DataFrame
            signals: DataFrame with signals and positions
            metrics: Performance metrics
            strategy_name: Name for dashboard
            output_path: Path to save HTML file (optional)
            auto_open: Whether to open in browser automatically

        Returns:
            HTML string or path to saved file
        """
        # Create individual charts
        price_fig = self.plot_price_and_signals(data, signals, strategy_name)
        equity_fig = self.plot_equity_curve(signals, strategy_name=strategy_name)
        metrics_fig = self.plot_performance_metrics(metrics, strategy_name)

        # Combine into single HTML with tabs (simplified version)
        # For now, we'll create separate charts and save them

        if output_path:
            # Save price chart
            price_path = output_path.replace('.html', '_price.html')
            equity_path = output_path.replace('.html', '_equity.html')
            metrics_path = output_path.replace('.html', '_metrics.html')

            price_fig.write_html(price_path)
            equity_fig.write_html(equity_path)
            metrics_fig.write_html(metrics_path)

            # Create main dashboard HTML
            dashboard_html = self._create_dashboard_html(
                strategy_name,
                price_path,
                equity_path,
                metrics_path,
                metrics
            )

            with open(output_path, 'w') as f:
                f.write(dashboard_html)

            if auto_open:
                open_in_browser(output_path)

            return output_path

        return ""

    def export_chart(
        self,
        figure: go.Figure,
        filename: str,
        format: str = 'html'
    ) -> None:
        """
        Export chart to file.

        Args:
            figure: Plotly Figure object
            filename: Output filename
            format: 'html', 'png', or 'pdf'
        """
        # Ensure output directory exists
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == 'html':
            figure.write_html(filename)
        elif format == 'png':
            figure.write_image(filename, format='png', scale=2)
        elif format == 'pdf':
            figure.write_image(filename, format='pdf')
        else:
            raise ValueError(f"Unsupported format: {format}")

    # Helper methods

    def _calculate_portfolio_history(
        self,
        signals: pd.DataFrame,
        initial_capital: float
    ) -> pd.DataFrame:
        """Calculate portfolio value over time."""
        from .performance_metrics import _simulate_portfolio
        return _simulate_portfolio(signals, initial_capital, commission=0.001)

    def _calculate_drawdown_series(self, portfolio_values: pd.Series) -> pd.Series:
        """Calculate drawdown series."""
        running_max = portfolio_values.expanding().max()
        drawdown = (portfolio_values - running_max) / running_max
        return drawdown

    def _create_dashboard_html(
        self,
        strategy_name: str,
        price_path: str,
        equity_path: str,
        metrics_path: str,
        metrics: Union[PerformanceMetrics, Dict[str, Any]]
    ) -> str:
        """Create main dashboard HTML with tabs."""
        if isinstance(metrics, PerformanceMetrics):
            metrics_dict = metrics.to_dict()
        else:
            metrics_dict = metrics

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>{strategy_name} Dashboard</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #0E1117;
            color: #FAFAFA;
        }}
        .header {{
            text-align: center;
            padding: 20px;
            background-color: #1E2530;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .tabs {{
            overflow: hidden;
            background-color: #1E2530;
            border-radius: 10px 10px 0 0;
        }}
        .tab {{
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            background-color: #1E2530;
            color: #FAFAFA;
            font-size: 17px;
        }}
        .tab:hover {{
            background-color: #2A3441;
        }}
        .tab.active {{
            background-color: #0E1117;
        }}
        .tabcontent {{
            display: none;
            padding: 20px;
            border: 1px solid #1E2530;
            border-top: none;
            border-radius: 0 0 10px 10px;
        }}
        iframe {{
            width: 100%;
            height: 800px;
            border: none;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        .metric-card {{
            background-color: #1E2530;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 14px;
            color: #888;
        }}
        .positive {{ color: #26A69A; }}
        .negative {{ color: #EF5350; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{strategy_name} - Performance Dashboard</h1>
    </div>

    <div class="summary">
        <div class="metric-card">
            <div class="metric-label">Total Return</div>
            <div class="metric-value {'positive' if metrics_dict.get('total_return_pct', 0) > 0 else 'negative'}">
                {metrics_dict.get('total_return_pct', 0):.2f}%
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Win Rate</div>
            <div class="metric-value">{metrics_dict.get('win_rate_pct', 0):.1f}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Sharpe Ratio</div>
            <div class="metric-value">{metrics_dict.get('sharpe_ratio', 0):.2f}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Max Drawdown</div>
            <div class="metric-value negative">{metrics_dict.get('max_drawdown_pct', 0):.2f}%</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Total Trades</div>
            <div class="metric-value">{metrics_dict.get('total_trades', 0)}</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Profit Factor</div>
            <div class="metric-value">{metrics_dict.get('profit_factor', 0):.2f}</div>
        </div>
    </div>

    <div class="tabs">
        <button class="tab active" onclick="openTab(event, 'price')">Price & Signals</button>
        <button class="tab" onclick="openTab(event, 'equity')">Equity Curve</button>
        <button class="tab" onclick="openTab(event, 'metrics')">Detailed Metrics</button>
    </div>

    <div id="price" class="tabcontent" style="display: block;">
        <iframe src="{Path(price_path).name}"></iframe>
    </div>

    <div id="equity" class="tabcontent">
        <iframe src="{Path(equity_path).name}"></iframe>
    </div>

    <div id="metrics" class="tabcontent">
        <iframe src="{Path(metrics_path).name}"></iframe>
    </div>

    <script>
        function openTab(evt, tabName) {{
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {{
                tabcontent[i].style.display = "none";
            }}
            tablinks = document.getElementsByClassName("tab");
            for (i = 0; i < tablinks.length; i++) {{
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }}
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }}
    </script>
</body>
</html>
        """
