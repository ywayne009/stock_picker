"""
Chart Themes and Styling

Provides professional color schemes and layout configurations for charts.
"""
from typing import Dict, Any


# Color palettes
COLORS = {
    # Trading colors
    'bullish': '#26A69A',  # Teal green
    'bearish': '#EF5350',  # Red
    'buy_signal': '#00E676',  # Bright green
    'sell_signal': '#FF1744',  # Bright red
    'ma_fast': '#2196F3',  # Blue
    'ma_slow': '#FF9800',  # Orange

    # Chart colors
    'background_dark': '#0E1117',
    'background_light': '#FFFFFF',
    'grid_dark': '#1E2530',
    'grid_light': '#E5E5E5',
    'text_dark': '#FAFAFA',
    'text_light': '#31333F',

    # Metrics colors
    'positive': '#26A69A',
    'negative': '#EF5350',
    'neutral': '#757575',
    'highlight': '#FFD700',

    # Additional colors
    'purple': '#9C27B0',
    'cyan': '#00BCD4',
    'yellow': '#FFEB3B',
    'pink': '#E91E63',
}


def get_dark_theme() -> Dict[str, Any]:
    """
    Get dark theme layout configuration.

    Returns:
        Dictionary with Plotly layout settings
    """
    return {
        'template': 'plotly_dark',
        'plot_bgcolor': COLORS['background_dark'],
        'paper_bgcolor': COLORS['background_dark'],
        'font': {
            'color': COLORS['text_dark'],
            'family': 'Arial, sans-serif',
            'size': 12
        },
        'title': {
            'font': {
                'size': 20,
                'color': COLORS['text_dark'],
                'family': 'Arial, sans-serif'
            },
            'x': 0.5,
            'xanchor': 'center'
        },
        'xaxis': {
            'gridcolor': COLORS['grid_dark'],
            'showgrid': True,
            'zeroline': False
        },
        'yaxis': {
            'gridcolor': COLORS['grid_dark'],
            'showgrid': True,
            'zeroline': False
        },
        'hovermode': 'x unified',
        'hoverlabel': {
            'bgcolor': '#1E2530',
            'font_size': 12,
            'font_family': 'Arial, sans-serif'
        },
        'margin': {
            'l': 60,
            'r': 30,
            't': 80,
            'b': 60
        },
        'legend': {
            'bgcolor': 'rgba(30, 37, 48, 0.8)',
            'bordercolor': COLORS['grid_dark'],
            'borderwidth': 1,
            'font': {
                'color': COLORS['text_dark']
            }
        }
    }


def get_light_theme() -> Dict[str, Any]:
    """
    Get light theme layout configuration.

    Returns:
        Dictionary with Plotly layout settings
    """
    return {
        'template': 'plotly_white',
        'plot_bgcolor': COLORS['background_light'],
        'paper_bgcolor': COLORS['background_light'],
        'font': {
            'color': COLORS['text_light'],
            'family': 'Arial, sans-serif',
            'size': 12
        },
        'title': {
            'font': {
                'size': 20,
                'color': COLORS['text_light'],
                'family': 'Arial, sans-serif'
            },
            'x': 0.5,
            'xanchor': 'center'
        },
        'xaxis': {
            'gridcolor': COLORS['grid_light'],
            'showgrid': True,
            'zeroline': False
        },
        'yaxis': {
            'gridcolor': COLORS['grid_light'],
            'showgrid': True,
            'zeroline': False
        },
        'hovermode': 'x unified',
        'hoverlabel': {
            'bgcolor': 'white',
            'font_size': 12,
            'font_family': 'Arial, sans-serif'
        },
        'margin': {
            'l': 60,
            'r': 30,
            't': 80,
            'b': 60
        },
        'legend': {
            'bgcolor': 'rgba(255, 255, 255, 0.8)',
            'bordercolor': COLORS['grid_light'],
            'borderwidth': 1,
            'font': {
                'color': COLORS['text_light']
            }
        }
    }


def get_theme(theme_name: str = 'dark') -> Dict[str, Any]:
    """
    Get theme configuration by name.

    Args:
        theme_name: 'dark' or 'light' (default: 'dark')

    Returns:
        Theme configuration dictionary
    """
    if theme_name.lower() == 'light':
        return get_light_theme()
    return get_dark_theme()


def get_candlestick_colors(theme: str = 'dark') -> Dict[str, str]:
    """
    Get candlestick color configuration.

    Args:
        theme: 'dark' or 'light'

    Returns:
        Dictionary with increasing/decreasing colors
    """
    return {
        'increasing': {
            'line': {'color': COLORS['bullish']},
            'fillcolor': COLORS['bullish']
        },
        'decreasing': {
            'line': {'color': COLORS['bearish']},
            'fillcolor': COLORS['bearish']
        }
    }


def get_signal_marker_style(signal_type: str) -> Dict[str, Any]:
    """
    Get marker style for buy/sell signals.

    Args:
        signal_type: 'buy' or 'sell'

    Returns:
        Plotly marker configuration
    """
    if signal_type == 'buy':
        return {
            'symbol': 'triangle-up',
            'size': 12,
            'color': COLORS['buy_signal'],
            'line': {
                'color': 'white',
                'width': 1
            }
        }
    else:  # sell
        return {
            'symbol': 'triangle-down',
            'size': 12,
            'color': COLORS['sell_signal'],
            'line': {
                'color': 'white',
                'width': 1
            }
        }


def get_ma_line_style(ma_type: str) -> Dict[str, Any]:
    """
    Get line style for moving averages.

    Args:
        ma_type: 'fast' or 'slow'

    Returns:
        Plotly line configuration
    """
    if ma_type == 'fast':
        return {
            'color': COLORS['ma_fast'],
            'width': 2
        }
    else:  # slow
        return {
            'color': COLORS['ma_slow'],
            'width': 2
        }


def get_metric_color(value: float, higher_is_better: bool = True) -> str:
    """
    Get color for metric value.

    Args:
        value: Metric value
        higher_is_better: If True, positive values are good

    Returns:
        Color hex code
    """
    if value == 0:
        return COLORS['neutral']

    if higher_is_better:
        return COLORS['positive'] if value > 0 else COLORS['negative']
    else:
        return COLORS['negative'] if value > 0 else COLORS['positive']


# Default chart sizes
CHART_SIZES = {
    'small': {'width': 800, 'height': 400},
    'medium': {'width': 1200, 'height': 600},
    'large': {'width': 1600, 'height': 800},
    'dashboard': {'width': 1400, 'height': 900}
}


def get_chart_size(size: str = 'medium') -> Dict[str, int]:
    """
    Get chart dimensions.

    Args:
        size: 'small', 'medium', 'large', or 'dashboard'

    Returns:
        Dictionary with width and height
    """
    return CHART_SIZES.get(size, CHART_SIZES['medium'])
