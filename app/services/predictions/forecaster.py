"""
Time Series Forecasting Service
Uses Prophet for predicting future trends
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    logger.warning("Prophet not installed. Forecasting features will be limited.")


class TimeSeriesForecaster:
    """
    Time series forecasting using Prophet
    """
    
    def __init__(self):
        self.model = None
        self.last_trained = None
        self.training_data_size = 0
        
    def prepare_data(self, data: List[Dict]) -> pd.DataFrame:
        """
        Prepare data for Prophet model
        Prophet requires columns: ds (date) and y (value)
        """
        df = pd.DataFrame(data)
        
        # Rename columns to Prophet format
        df = df.rename(columns={
            'date': 'ds',
            'count': 'y'
        })
        
        # Ensure ds is datetime
        df['ds'] = pd.to_datetime(df['ds'])
        
        # Sort by date
        df = df.sort_values('ds')
        
        return df
    
    def train_model(self, df: pd.DataFrame) -> None:
        """
        Train Prophet model on historical data
        """
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet is not installed. Run: pip install prophet")
        
        # Create and configure Prophet model
        self.model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False,  # Not enough data yet
            changepoint_prior_scale=0.05,  # Flexibility of trend changes
            interval_width=0.95  # 95% confidence interval
        )
        
        # Fit the model
        self.model.fit(df)
        
        self.last_trained = datetime.now()
        self.training_data_size = len(df)
        
        logger.info(f"Model trained on {self.training_data_size} data points")
    
    def forecast(self, periods: int = 7) -> pd.DataFrame:
        """
        Generate forecast for future periods
        
        Args:
            periods: Number of days to forecast
            
        Returns:
            DataFrame with predictions
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train_model() first.")
        
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=periods)
        
        # Generate predictions
        forecast = self.model.predict(future)
        
        return forecast
    
    def get_forecast_summary(self, forecast: pd.DataFrame, periods: int = 7) -> Dict:
        """
        Extract summary from forecast
        """
        # Get only future predictions
        future_forecast = forecast.tail(periods)
        
        predictions = []
        for _, row in future_forecast.iterrows():
            predictions.append({
                'date': row['ds'].strftime('%Y-%m-%d'),
                'predicted_value': max(0, round(row['yhat'])),  # No negative values
                'lower_bound': max(0, round(row['yhat_lower'])),
                'upper_bound': max(0, round(row['yhat_upper'])),
                'confidence': 0.95
            })
        
        return {
            'predictions': predictions,
            'model_info': {
                'type': 'Prophet',
                'trained_at': self.last_trained.isoformat() if self.last_trained else None,
                'training_data_size': self.training_data_size,
                'forecast_periods': periods,
                'confidence_interval': 0.95
            }
        }
    
    def calculate_accuracy_metrics(self, df: pd.DataFrame, test_size: int = 7) -> Dict:
        """
        Calculate model accuracy on historical data
        """
        if len(df) < test_size + 7:
            return {
                'mae': None,
                'mape': None,
                'message': 'Not enough data for accuracy calculation'
            }
        
        # Split data
        train_df = df[:-test_size]
        test_df = df[-test_size:]
        
        # Train on subset
        temp_model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=False,
            changepoint_prior_scale=0.05
        )
        temp_model.fit(train_df)
        
        # Predict on test set
        future = temp_model.make_future_dataframe(periods=test_size)
        forecast = temp_model.predict(future)
        
        # Get predictions for test period
        test_predictions = forecast.tail(test_size)['yhat'].values
        test_actuals = test_df['y'].values
        
        # Calculate metrics
        mae = np.mean(np.abs(test_predictions - test_actuals))
        mape = np.mean(np.abs((test_actuals - test_predictions) / (test_actuals + 1))) * 100
        
        return {
            'mae': round(mae, 2),
            'mape': round(mape, 2),
            'test_size': test_size
        }


class SimpleTrendAnalyzer:
    """
    Simple trend analysis without Prophet (fallback)
    """
    
    @staticmethod
    def moving_average_forecast(data: List[Dict], periods: int = 7, window: int = 7) -> Dict:
        """
        Simple moving average forecast
        """
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Calculate moving average
        df['ma'] = df['count'].rolling(window=window, min_periods=1).mean()
        
        # Get last MA value for forecast
        last_ma = df['ma'].iloc[-1]
        last_date = df['date'].iloc[-1]
        
        # Generate simple forecast
        predictions = []
        for i in range(1, periods + 1):
            future_date = last_date + timedelta(days=i)
            predictions.append({
                'date': future_date.strftime('%Y-%m-%d'),
                'predicted_value': round(last_ma),
                'lower_bound': round(last_ma * 0.8),
                'upper_bound': round(last_ma * 1.2),
                'confidence': 0.80
            })
        
        return {
            'predictions': predictions,
            'model_info': {
                'type': 'Moving Average',
                'window': window,
                'forecast_periods': periods,
                'note': 'Simple baseline model'
            }
        }
    
    @staticmethod
    def calculate_trend(data: List[Dict]) -> str:
        """
        Calculate overall trend direction
        """
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        if len(df) < 7:
            return 'insufficient_data'
        
        # Compare recent average to older average
        recent_avg = df['count'].tail(7).mean()
        older_avg = df['count'].head(7).mean()
        
        change_pct = ((recent_avg - older_avg) / (older_avg + 1)) * 100
        
        if change_pct > 10:
            return 'escalating'
        elif change_pct < -10:
            return 'de-escalating'
        else:
            return 'stable'
