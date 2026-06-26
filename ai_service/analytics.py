"""
Analytics Module using Pandas, Scikit-learn, Matplotlib.
Provides: Peak hour analysis, violation frequency, revenue prediction,
and violation probability ML model.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


class TrafficAnalytics:
    """Advanced analytics module for traffic data."""

    def __init__(self, output_dir: str = "./analytics_output"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def peak_hour_analysis(self, density_data: List[Dict]) -> Dict:
        """
        Analyze peak traffic hours.
        
        Args:
            density_data: List of {timestamp, vehicle_count, camera_id}
        
        Returns:
            Peak hours analysis with top congested hours
        """
        if not density_data:
            return {"peak_hours": [], "avg_by_hour": {}}

        df = pd.DataFrame(density_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.day_name()

        hourly = df.groupby('hour')['vehicle_count'].mean().sort_values(ascending=False)

        peak_hours = []
        for hour, avg_count in hourly.head(5).items():
            peak_hours.append({
                "hour": int(hour),
                "hour_label": f"{int(hour):02d}:00 - {int(hour)+1:02d}:00",
                "avg_vehicle_count": round(float(avg_count), 1),
            })

        # Day-of-week pattern
        daily = df.groupby('day_of_week')['vehicle_count'].mean().to_dict()

        return {
            "peak_hours": peak_hours,
            "avg_by_hour": {int(k): round(float(v), 1) for k, v in hourly.items()},
            "avg_by_day": {k: round(float(v), 1) for k, v in daily.items()},
        }

    def violation_frequency_analysis(self, violations: List[Dict]) -> Dict:
        """
        Analyze violation frequency by zone, type, and time.
        """
        if not violations:
            return {}

        df = pd.DataFrame(violations)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # By type
        type_freq = df['violation_type'].value_counts().to_dict()

        # By hour
        df['hour'] = df['timestamp'].dt.hour
        hourly_violations = df.groupby('hour').size().to_dict()

        # By day of week
        df['day'] = df['timestamp'].dt.day_name()
        daily_violations = df.groupby('day').size().to_dict()

        # By location/zone
        zone_freq = df['location'].value_counts().head(10).to_dict() if 'location' in df.columns else {}

        return {
            "by_type": type_freq,
            "by_hour": {int(k): int(v) for k, v in hourly_violations.items()},
            "by_day": daily_violations,
            "by_zone": zone_freq,
            "total": len(df),
        }

    def revenue_trend_prediction(
        self,
        payment_data: List[Dict],
        months_ahead: int = 3,
    ) -> Dict:
        """
        Predict revenue trends using simple linear regression.
        """
        if not payment_data or len(payment_data) < 3:
            return {"prediction": [], "trend": "insufficient_data"}

        df = pd.DataFrame(payment_data)
        df['payment_date'] = pd.to_datetime(df['payment_date'])
        df['month'] = df['payment_date'].dt.to_period('M')

        monthly = df.groupby('month')['amount'].sum().reset_index()
        monthly['month_num'] = range(len(monthly))

        if len(monthly) < 3:
            return {"prediction": [], "trend": "insufficient_data"}

        # Simple linear regression
        from sklearn.linear_model import LinearRegression

        X = monthly['month_num'].values.reshape(-1, 1)
        y = monthly['amount'].values.astype(float)

        model = LinearRegression()
        model.fit(X, y)

        # Predict future months
        future_X = np.arange(len(monthly), len(monthly) + months_ahead).reshape(-1, 1)
        predictions = model.predict(future_X)

        trend = "increasing" if model.coef_[0] > 0 else "decreasing"

        return {
            "historical": [
                {"month": str(row['month']), "revenue": float(row['amount'])}
                for _, row in monthly.iterrows()
            ],
            "prediction": [
                {"month_ahead": i + 1, "predicted_revenue": round(float(p), 2)}
                for i, p in enumerate(predictions)
            ],
            "trend": trend,
            "slope": round(float(model.coef_[0]), 2),
            "r_squared": round(float(model.score(X, y)), 3),
        }

    def violation_probability_model(
        self,
        feature_data: List[Dict],
    ) -> Dict:
        """
        Train a simple ML model for violation probability prediction.
        
        Features: hour, day_of_week, vehicle_count, congestion_index
        Target: violation_occurred (binary)
        """
        if not feature_data or len(feature_data) < 20:
            return {"status": "insufficient_data"}

        df = pd.DataFrame(feature_data)

        # Ensure required columns
        required_cols = ['hour', 'day_of_week', 'vehicle_count', 'congestion_index', 'violation_occurred']
        for col in required_cols:
            if col not in df.columns:
                return {"status": f"missing_column: {col}"}

        # Encode day_of_week
        day_mapping = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2,
            'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6,
        }
        df['day_num'] = df['day_of_week'].map(day_mapping).fillna(0)

        X = df[['hour', 'day_num', 'vehicle_count', 'congestion_index']].values
        y = df['violation_occurred'].values.astype(int)

        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score, classification_report

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        feature_importance = dict(zip(
            ['hour', 'day_of_week', 'vehicle_count', 'congestion_index'],
            [round(float(f), 4) for f in model.feature_importances_],
        ))

        return {
            "status": "trained",
            "accuracy": round(float(accuracy), 3),
            "feature_importance": feature_importance,
            "training_samples": len(X_train),
            "test_samples": len(X_test),
        }

    def generate_density_chart(
        self,
        density_data: List[Dict],
        title: str = "Traffic Density Over Time",
    ) -> str:
        """Generate a traffic density line chart."""
        if not density_data:
            return ""

        df = pd.DataFrame(density_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(df['timestamp'], df['vehicle_count'], color='#2d5f8a', linewidth=2)
        ax.fill_between(df['timestamp'], df['vehicle_count'], alpha=0.2, color='#2d5f8a')
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Time')
        ax.set_ylabel('Vehicle Count')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()

        path = os.path.join(self.output_dir, "density_chart.png")
        fig.savefig(path, dpi=150)
        plt.close(fig)

        return path

    def generate_violation_chart(
        self,
        violations: List[Dict],
        title: str = "Violations by Type",
    ) -> str:
        """Generate a violation pie chart."""
        if not violations:
            return ""

        df = pd.DataFrame(violations)
        type_counts = df['violation_type'].value_counts()

        colors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71', '#9b59b6']
        labels = {
            'red_light': 'Red Light',
            'no_helmet': 'No Helmet',
            'no_seatbelt': 'No Seatbelt',
            'overspeed': 'Overspeeding',
            'wrong_lane': 'Wrong Lane',
        }

        fig, ax = plt.subplots(figsize=(8, 8))
        wedges, texts, autotexts = ax.pie(
            type_counts.values,
            labels=[labels.get(t, t) for t in type_counts.index],
            colors=colors[:len(type_counts)],
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85,
        )

        # Style
        for autotext in autotexts:
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')

        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()

        path = os.path.join(self.output_dir, "violation_pie.png")
        fig.savefig(path, dpi=150)
        plt.close(fig)

        return path
