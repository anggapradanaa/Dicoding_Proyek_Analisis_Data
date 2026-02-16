import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Beijing Air Quality Dashboard",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)

# ==================== DATA LOADING FUNCTION ====================

@st.cache_data
def load_data():
    """Load and preprocess air quality data"""
    try:
        folder_path = 'PRSA_Data_20130301-20170228'
        files = glob.glob(os.path.join(folder_path, '*.csv'))
        
        if not files:
            st.error(f"No CSV files found in '{folder_path}' directory!")
            st.info("Please ensure the data folder is in the same directory as this script.")
            st.stop()
        
        # Read and concatenate all files
        df_list = []
        for file in files:
            df_temp = pd.read_csv(file)
            df_list.append(df_temp)
        
        df = pd.concat(df_list, ignore_index=True)
        
        # Create datetime column
        df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
        
        # Sort and reset index
        df = df.sort_values(by=['datetime', 'station'])
        df = df.reset_index(drop=True)
        
        # Drop unnecessary columns
        if 'No' in df.columns:
            df = df.drop('No', axis=1)
        
        # Remove rows with missing PM2.5
        df = df.dropna(subset=['PM2.5'])
        
        # Add time features
        df['date'] = df['datetime'].dt.date
        df['year'] = df['datetime'].dt.year
        df['month'] = df['datetime'].dt.month
        df['month_name'] = df['datetime'].dt.strftime('%b')
        
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

# ==================== HELPER FUNCTIONS ====================

def categorize_air_quality(pm25):
    """Categorize air quality based on WHO/AQI standards"""
    if pm25 <= 12:
        return 'Good'
    elif pm25 <= 35:
        return 'Moderate'
    elif pm25 <= 55:
        return 'Unhealthy for Sensitive'
    elif pm25 <= 150:
        return 'Unhealthy'
    elif pm25 <= 250:
        return 'Very Unhealthy'
    else:
        return 'Hazardous'

def filter_data(df, station, date_range):
    """Filter data based on station and date range"""
    filtered_df = df.copy()
    
    # Filter by station
    if station != "All Stations":
        filtered_df = filtered_df[filtered_df['station'] == station]
    
    # Filter by date range
    filtered_df = filtered_df[
        (filtered_df['datetime'].dt.date >= date_range[0]) & 
        (filtered_df['datetime'].dt.date <= date_range[1])
    ]
    
    return filtered_df

# ==================== MAIN APPLICATION ====================

def main():
    # Load data
    df = load_data()
    
    # ==================== HEADER ====================
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 3.5rem; font-weight: bold; color: #1f77b4; margin-bottom: 0.5rem;'>
                🌁 Beijing Air Quality Dashboard
            </h1>
            <p style='font-size: 1.2rem; color: #666; margin-top: 0;'>
                Multi-Station PM2.5 Monitoring & Analysis (2013-2017)
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # ==================== SIDEBAR ====================
    st.sidebar.header("🎛️ Filter Options")
    
    # Station filter
    stations = ["All Stations"] + sorted(df['station'].unique().tolist())
    selected_station = st.sidebar.selectbox(
        "Select Station:",
        options=stations,
        index=0
    )
    
    # Date range filter
    min_date = df['datetime'].min().date()
    max_date = df['datetime'].max().date()

    st.sidebar.subheader("Date Range")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date_input = st.date_input(
            "Start Date:",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            key='start'
        )
    with col2:
        end_date_input = st.date_input(
            "End Date:",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            key='end'
        )

    date_range = (start_date_input, end_date_input)
    
    # Handle single date selection
    start_date, end_date = date_range
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.info(
        f"""
        **Dataset Information:**
        - Period: {min_date} to {max_date}
        - Total Stations: {df['station'].nunique()}
        - Total Records: {len(df):,}
        """
    )
    
    # Filter data
    filtered_df = filter_data(df, selected_station, (start_date, end_date))
    
    # Check if filtered data is empty
    if len(filtered_df) == 0:
        st.warning("⚠️ No data available for the selected filters. Please adjust your selection.")
        st.stop()
    
    # ==================== METRICS SECTION ====================
    st.header("📊 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_pm25 = filtered_df['PM2.5'].mean()
        st.metric(
            label="Average PM2.5",
            value=f"{avg_pm25:.1f} µg/m³",
            delta=f"{avg_pm25 - df['PM2.5'].mean():.1f} vs overall"
        )
    
    with col2:
        max_pm25 = filtered_df['PM2.5'].max()
        st.metric(
            label="Maximum PM2.5",
            value=f"{max_pm25:.1f} µg/m³"
        )
    
    with col3:
        min_pm25 = filtered_df['PM2.5'].min()
        st.metric(
            label="Minimum PM2.5",
            value=f"{min_pm25:.1f} µg/m³"
        )
    
    with col4:
        # Calculate percentage of unhealthy days (PM2.5 > 35)
        unhealthy_pct = (filtered_df['PM2.5'] > 35).sum() / len(filtered_df) * 100
        st.metric(
            label="Unhealthy Days",
            value=f"{unhealthy_pct:.1f}%",
            delta=f"PM2.5 > 35 µg/m³",
            delta_color="inverse"
        )
    
    with col5:
        # Total data points
        total_records = len(filtered_df)
        st.metric(
            label="Total Records",
            value=f"{total_records:,}",
            delta=f"{filtered_df['station'].nunique()} stations"
        )
    
    st.markdown("---")
    
    # ==================== OVERVIEW TREND ====================
    st.header("📈 PM2.5 Trend Over Time")
    
    if selected_station == "All Stations":
        # Daily average across all stations
        daily_avg = filtered_df.groupby(filtered_df['datetime'].dt.date)['PM2.5'].mean().reset_index()
        daily_avg.columns = ['Date', 'PM2.5']
        
        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(daily_avg['Date'], daily_avg['PM2.5'], color='#1f77b4', linewidth=2, alpha=0.8)
        ax.fill_between(daily_avg['Date'], daily_avg['PM2.5'], alpha=0.3, color='#1f77b4')
        
        # Add WHO guidelines
        ax.axhline(y=35, color='orange', linestyle='--', linewidth=1.5, label='WHO Unhealthy (35)', alpha=0.7)
        ax.axhline(y=55, color='red', linestyle='--', linewidth=1.5, label='WHO Very Unhealthy (55)', alpha=0.7)
        
        ax.set_xlabel('Date', fontsize=11, fontweight='bold')
        ax.set_ylabel('PM2.5 (µg/m³)', fontsize=11, fontweight='bold')
        ax.set_title('Daily Average PM2.5 - All Stations', fontsize=13, fontweight='bold', pad=15)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    else:
        # Trend for specific station
        station_data = filtered_df[filtered_df['station'] == selected_station].copy()
        daily_avg = station_data.groupby(station_data['datetime'].dt.date)['PM2.5'].mean().reset_index()
        daily_avg.columns = ['Date', 'PM2.5']
        
        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(daily_avg['Date'], daily_avg['PM2.5'], color='#d62728', linewidth=2, alpha=0.8, label=selected_station)
        ax.fill_between(daily_avg['Date'], daily_avg['PM2.5'], alpha=0.3, color='#d62728')
        
        # Add WHO guidelines
        ax.axhline(y=35, color='orange', linestyle='--', linewidth=1.5, label='WHO Unhealthy (35)', alpha=0.7)
        ax.axhline(y=55, color='red', linestyle='--', linewidth=1.5, label='WHO Very Unhealthy (55)', alpha=0.7)
        
        ax.set_xlabel('Date', fontsize=11, fontweight='bold')
        ax.set_ylabel('PM2.5 (µg/m³)', fontsize=11, fontweight='bold')
        ax.set_title(f'Daily Average PM2.5 - {selected_station}', fontsize=13, fontweight='bold', pad=15)
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    st.markdown("---")
    
    # ==================== VISUALISASI 1: STATION TERTINGGI ====================
    st.header("Stasiun Paling Terdampak Polusi PM2.5")
    
    # Calculate average PM2.5 by station (using filtered data)
    station_avg = filtered_df.groupby('station')['PM2.5'].mean().sort_values(ascending=False).reset_index()
    station_avg.columns = ['Station', 'Average_PM2.5']
    
    # Visualization
    fig, ax = plt.subplots(figsize=(14, 6))
    colors = ['#d62728' if i < 3 else '#1f77b4' for i in range(len(station_avg))]
    bars = ax.bar(station_avg['Station'], station_avg['Average_PM2.5'], color=colors, edgecolor='black', alpha=0.8)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.1f}',
               ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.axhline(y=35, color='orange', linestyle='--', linewidth=2, label='WHO Unhealthy (35 µg/m³)', alpha=0.7)
    ax.axhline(y=55, color='red', linestyle='--', linewidth=2, label='WHO Very Unhealthy (55 µg/m³)', alpha=0.7)
    
    ax.set_xlabel('Station', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average PM2.5 (µg/m³)', fontsize=12, fontweight='bold')
    ax.set_title('Average PM2.5 Levels by Station', fontsize=14, fontweight='bold', pad=15)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # Insight
    if len(station_avg) >= 3:
        st.info(f"""
        
        Stasiun dengan rata-rata PM2.5 tertinggi adalah **{station_avg.iloc[0]['Station']}** 
        dengan nilai **{station_avg.iloc[0]['Average_PM2.5']:.2f} µg/m³**.
        
        Top 3 stasiun dengan polusi tertinggi:
        1. {station_avg.iloc[0]['Station']}: {station_avg.iloc[0]['Average_PM2.5']:.2f} µg/m³
        2. {station_avg.iloc[1]['Station']}: {station_avg.iloc[1]['Average_PM2.5']:.2f} µg/m³
        3. {station_avg.iloc[2]['Station']}: {station_avg.iloc[2]['Average_PM2.5']:.2f} µg/m³
  
        """)
    else:
        st.info(f"""
                        
        Stasiun dengan rata-rata PM2.5 tertinggi adalah **{station_avg.iloc[0]['Station']}** 
        dengan nilai **{station_avg.iloc[0]['Average_PM2.5']:.2f} µg/m³**.
        """)
    
    st.markdown("---")
    
    # ==================== VISUALISASI 2: POLA MUSIMAN ====================
    st.header("Pola Musiman PM2.5")
    
    # Monthly pattern (using filtered data)
    filtered_df['year'] = filtered_df['datetime'].dt.year
    filtered_df['month'] = filtered_df['datetime'].dt.month
    
    monthly_pm = filtered_df.groupby(['year', 'month'])['PM2.5'].mean().reset_index()
    monthly_avg = filtered_df.groupby('month')['PM2.5'].mean().reset_index()
    
    # Create visualization
    fig, axes = plt.subplots(2, 1, figsize=(15, 10))
    
    # 1. Yearly trend with monthly breakdown
    years_in_filtered = sorted(filtered_df['year'].unique())
    for year in years_in_filtered:
        year_data = monthly_pm[monthly_pm['year'] == year]
        axes[0].plot(year_data['month'], year_data['PM2.5'], marker='o', linewidth=2, label=f'Year {year}', alpha=0.8)
    
    axes[0].set_xlabel('Month', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Average PM2.5 (µg/m³)', fontsize=12, fontweight='bold')
    axes[0].set_title('Monthly PM2.5 Trends Across Years', fontsize=14, fontweight='bold')
    axes[0].legend(loc='upper right', ncol=2)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_xticks(range(1, 13))
    axes[0].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    
    # 2. Average seasonal pattern
    colors_season = ['#d62728' if m in [12, 1, 2] else '#ff7f0e' if m in [3, 4, 5] else '#2ca02c' if m in [6, 7, 8] else '#1f77b4' 
                     for m in monthly_avg['month']]
    
    bars = axes[1].bar(monthly_avg['month'], monthly_avg['PM2.5'], color=colors_season, edgecolor='black', alpha=0.8)
    
    # Add value labels
    for i, bar in enumerate(bars):
        height = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width()/2., height,
                     f'{height:.1f}',
                     ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    axes[1].axhline(y=monthly_avg['PM2.5'].mean(), color='red', linestyle='--', linewidth=2, 
                    label=f'Overall Average: {monthly_avg["PM2.5"].mean():.1f}', alpha=0.7)
    
    axes[1].set_xlabel('Month', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Average PM2.5 (µg/m³)', fontsize=12, fontweight='bold')
    axes[1].set_title('Average Seasonal Pattern of PM2.5', fontsize=14, fontweight='bold')
    axes[1].set_xticks(range(1, 13))
    axes[1].set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    axes[1].legend(loc='upper right')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Add season labels
    season_labels = [
        (1.5, 'Winter', '#d62728'),
        (4, 'Spring', '#ff7f0e'),
        (7, 'Summer', '#2ca02c'),
        (10, 'Fall', '#1f77b4')
    ]
    
    for pos, label, color in season_labels:
        axes[1].text(pos, axes[1].get_ylim()[1] * 0.95, label, 
                    ha='center', fontsize=11, fontweight='bold', color=color,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor=color, alpha=0.7))
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # Calculate seasonal statistics
    season_map = {12: 'Winter', 1: 'Winter', 2: 'Winter',
                  3: 'Spring', 4: 'Spring', 5: 'Spring',
                  6: 'Summer', 7: 'Summer', 8: 'Summer',
                  9: 'Fall', 10: 'Fall', 11: 'Fall'}
    
    filtered_df['season'] = filtered_df['month'].map(season_map)
    season_stats = filtered_df.groupby('season')['PM2.5'].mean()
    
    # Build insight dynamically based on available seasons
    available_seasons = season_stats.index.tolist()
    season_order = ['Winter', 'Spring', 'Summer', 'Fall']
    available_ordered = [s for s in season_order if s in available_seasons]
    
    insight_text = "Pola musiman PM2.5 berdasarkan periode yang dipilih:\n\n"
    
    for season in available_ordered:
        if season == 'Winter':
            insight_text += f"- **Musim Dingin (Des-Feb)**: PM2.5 {season_stats[season]:.1f} µg/m³\n"
        elif season == 'Spring':
            insight_text += f"- **Musim Semi (Mar-Mei)**: PM2.5 {season_stats[season]:.1f} µg/m³\n"
        elif season == 'Summer':
            insight_text += f"- **Musim Panas (Jun-Agu)**: PM2.5 {season_stats[season]:.1f} µg/m³\n"
        elif season == 'Fall':
            insight_text += f"- **Musim Gugur (Sep-Nov)**: PM2.5 {season_stats[season]:.1f} µg/m³\n"
    
    if len(available_ordered) >= 4:
        highest_season = season_stats.idxmax()
        lowest_season = season_stats.idxmin()
        insight_text += f"\n**{highest_season}** memiliki PM2.5 tertinggi, sementara **{lowest_season}** terendah."
    
    st.info(insight_text)
    
    st.markdown("---")
    
    # ==================== VISUALISASI 3: CLUSTERING ====================
    st.header("Clustering Station Berdasarkan Karakteristik Polusi")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Heatmap: Pollutant Levels Across Stations")
        
        # Create station profile with multiple pollutants (using filtered data)
        station_profile = filtered_df.groupby('station').agg({
            'PM2.5': 'mean',
            'PM10': 'mean',
            'SO2': 'mean',
            'NO2': 'mean',
            'CO': 'mean',
            'O3': 'mean'
        }).round(2)
        
        pollutants_normalized = station_profile[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']]
        
        # Normalize for better visualization
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        pollutants_scaled = pd.DataFrame(
            scaler.fit_transform(pollutants_normalized),
            index=pollutants_normalized.index,
            columns=pollutants_normalized.columns
        )
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(pollutants_scaled.T, annot=False, cmap='RdYlGn_r', center=0, 
                    cbar_kws={'label': 'Normalized Level'}, ax=ax, linewidths=0.5)
        ax.set_title('Pollutant Levels Across Stations (Normalized)', fontsize=13, fontweight='bold', pad=10)
        ax.set_xlabel('Station', fontsize=11, fontweight='bold')
        ax.set_ylabel('Pollutant', fontsize=11, fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.subheader("Clustering by Pollution Level")
        
        # Manual clustering based on PM2.5 quartiles (using filtered data)
        q1 = station_profile['PM2.5'].quantile(0.25)
        q2 = station_profile['PM2.5'].quantile(0.50)
        q3 = station_profile['PM2.5'].quantile(0.75)
        
        def classify_pollution(pm25):
            if pm25 < q1:
                return 'Low Pollution'
            elif pm25 < q2:
                return 'Moderate Pollution'
            elif pm25 < q3:
                return 'High Pollution'
            else:
                return 'Very High Pollution'
        
        station_profile['Cluster'] = station_profile['PM2.5'].apply(classify_pollution)
        station_profile_sorted = station_profile.sort_values('PM2.5', ascending=True)
        
        # Color mapping
        cluster_colors = {
            'Low Pollution': '#2ca02c',
            'Moderate Pollution': '#ff7f0e',
            'High Pollution': '#d62728',
            'Very High Pollution': '#8B0000'
        }
        
        colors = [cluster_colors[cluster] for cluster in station_profile_sorted['Cluster']]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        bars = ax.barh(range(len(station_profile_sorted)), station_profile_sorted['PM2.5'], 
                       color=colors, edgecolor='black', alpha=0.8)
        ax.set_yticks(range(len(station_profile_sorted)))
        ax.set_yticklabels(station_profile_sorted.index)
        ax.set_xlabel('Average PM2.5 (µg/m³)', fontsize=11, fontweight='bold')
        ax.set_title('Station Clustering by Pollution Level', fontsize=13, fontweight='bold', pad=10)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (idx, row) in enumerate(station_profile_sorted.iterrows()):
            ax.text(row['PM2.5'] + 1, i, f"{row['PM2.5']:.1f}", 
                   va='center', fontsize=9, fontweight='bold')
        
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=color, edgecolor='black', label=label) 
                          for label, color in cluster_colors.items()]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    # Correlation heatmap (using filtered data)
    st.subheader("Correlation Matrix: Pollutants and Meteorological Factors")
    
    correlation_matrix = filtered_df[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES']].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=1, cbar_kws={'label': 'Correlation Coefficient'}, ax=ax)
    ax.set_title('Correlation Matrix: Pollutants and Meteorological Factors', fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # Count stations per cluster
    cluster_counts = station_profile['Cluster'].value_counts().reindex([
        'Low Pollution', 'Moderate Pollution', 'High Pollution', 'Very High Pollution'
    ], fill_value=0)
    
    # Insight
    st.info(f"""
    
    Terdapat 4 kelompok stasiun dengan karakteristik polusi yang mirip:
    
    - **Very High Pollution** ({cluster_counts['Very High Pollution']} stasiun): PM2.5 > {q3:.1f} µg/m³
      → Memerlukan prioritas intervensi tinggi
    
    - **High Pollution** ({cluster_counts['High Pollution']} stasiun): PM2.5 antara {q2:.1f}-{q3:.1f} µg/m³
      → Area dengan polusi substansial
    
    - **Moderate Pollution** ({cluster_counts['Moderate Pollution']} stasiun): PM2.5 antara {q1:.1f}-{q2:.1f} µg/m³
      → Perlu monitoring berkelanjutan
    
    - **Low Pollution** ({cluster_counts['Low Pollution']} stasiun): PM2.5 < {q1:.1f} µg/m³
      → Kondisi relatif lebih baik dalam periode yang dipilih
    
    **Korelasi Penting:**
    - PM2.5 berkorelasi dengan PM10 (r={correlation_matrix.loc['PM2.5', 'PM10']:.2f}) dan CO (r={correlation_matrix.loc['PM2.5', 'CO']:.2f})
    - Korelasi dengan TEMP (r={correlation_matrix.loc['PM2.5', 'TEMP']:.2f}) menunjukkan pengaruh suhu terhadap polusi
    """)
    
    st.markdown("---")
    
    # ==================== VISUALISASI 4: DISTRIBUSI KUALITAS UDARA ====================
    st.header("Distribusi Kualitas Udara Berdasarkan Lokasi")
    
    # Add category to filtered data
    filtered_df['AQI_Category'] = filtered_df['PM2.5'].apply(categorize_air_quality)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Air Quality Category Distribution")
        
        # Count by category
        category_order = ['Good', 'Moderate', 'Unhealthy for Sensitive', 
                         'Unhealthy', 'Very Unhealthy', 'Hazardous']
        aqi_counts = filtered_df['AQI_Category'].value_counts()
        aqi_pct = (aqi_counts / len(filtered_df) * 100).round(2)
        
        # Pie chart
        colors_aqi = {
            'Good': '#00e400',
            'Moderate': '#ffff00',
            'Unhealthy for Sensitive': '#ff7e00',
            'Unhealthy': '#ff0000',
            'Very Unhealthy': '#8f3f97',
            'Hazardous': '#7e0023'
        }
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Get colors for existing categories
        plot_colors = [colors_aqi.get(cat, 'gray') for cat in aqi_counts.index]
        
        wedges, texts, autotexts = ax.pie(
            aqi_counts.values,
            labels=aqi_counts.index,
            colors=plot_colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10}
        )
        
        # Enhance text
        for i, (autotext, wedge) in enumerate(zip(autotexts, wedges)):
            # Get background color
            bg_color = wedge.get_facecolor()
            category = aqi_counts.index[i]
            
            # Determine text color based on category
            if category in ['Good', 'Moderate']:  # Light colors
                autotext.set_color('black')
            else:  # Dark colors
                autotext.set_color('white')
            
            autotext.set_fontweight('bold')
        
        ax.set_title('Overall Air Quality Distribution', fontsize=13, fontweight='bold', pad=15)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.subheader("Air Quality by Station")
        
        # Stacked bar chart by station (using filtered data)
        station_quality_dist = pd.crosstab(filtered_df['station'], filtered_df['AQI_Category'], normalize='index') * 100
        station_quality_dist = station_quality_dist.round(2)
        
        # Reorder columns by severity
        station_quality_dist = station_quality_dist[[col for col in category_order if col in station_quality_dist.columns]]
        
        # Sort stations by average PM2.5
        station_avg_all = filtered_df.groupby('station')['PM2.5'].mean().sort_values(ascending=False)
        station_quality_dist = station_quality_dist.reindex(station_avg_all.index)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        station_quality_dist.plot(kind='barh', stacked=True, ax=ax, 
                                  color=[colors_aqi.get(cat, 'gray') for cat in station_quality_dist.columns],
                                  edgecolor='black', linewidth=0.5)
        
        # Add percentage labels on bars
        for i, station in enumerate(station_quality_dist.index):
            cumsum = 0
            for col in station_quality_dist.columns:
                value = station_quality_dist.loc[station, col]
                
                # Determine text color based on background (use black for light colors, white for dark)
                bg_color = colors_aqi.get(col, 'gray')
                if bg_color in ['#00e400', '#ffff00']:  # Green and Yellow (light colors)
                    text_color = 'black'
                else:  # Orange, Red, Purple, Dark Red (dark colors)
                    text_color = 'white'
                
                if value >= 5:  # Show normal size for >= 5%
                    ax.text(cumsum + value/2, i, f'{value:.1f}%', 
                        ha='center', va='center', fontsize=8, fontweight='bold', color=text_color)
                elif value >= 2:  # Show smaller font for 2-5%
                    ax.text(cumsum + value/2, i, f'{value:.1f}%', 
                        ha='center', va='center', fontsize=6, fontweight='bold', color=text_color)
                cumsum += value

        ax.set_xlabel('Percentage (%)', fontsize=11, fontweight='bold')
        ax.set_ylabel('Station', fontsize=11, fontweight='bold')
        ax.set_title('Air Quality Distribution by Station', fontsize=13, fontweight='bold', pad=15)
        ax.legend(title='Air Quality Category', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    # Calculate good air days percentage
    if 'Good' in station_quality_dist.columns and 'Moderate' in station_quality_dist.columns:
        station_quality_dist['Good_Air_Days'] = station_quality_dist['Good'] + station_quality_dist['Moderate']
    elif 'Good' in station_quality_dist.columns:
        station_quality_dist['Good_Air_Days'] = station_quality_dist['Good']
    elif 'Moderate' in station_quality_dist.columns:
        station_quality_dist['Good_Air_Days'] = station_quality_dist['Moderate']
    else:
        station_quality_dist['Good_Air_Days'] = 0
    
    if len(station_quality_dist) > 0:
        best_station = station_quality_dist['Good_Air_Days'].idxmax()
        worst_station = station_quality_dist['Good_Air_Days'].idxmin()
        
        # Insight
        overall_dist = filtered_df['AQI_Category'].value_counts(normalize=True) * 100
        unhealthy_categories = ['Unhealthy', 'Very Unhealthy', 'Hazardous']
        unhealthy_pct = overall_dist[overall_dist.index.isin(unhealthy_categories)].sum()
        
        st.info(f"""
        
        Distribusi kualitas udara menunjukkan variasi signifikan antar lokasi:
        
        - **Kondisi Kritis**: {unhealthy_pct:.1f}% waktu berada di kategori "Unhealthy" atau lebih buruk
        - **Stasiun Terbaik**: {best_station} dengan {station_quality_dist.loc[best_station, 'Good_Air_Days']:.1f}% waktu berkualitas baik/moderat
        - **Stasiun Terburuk**: {worst_station} dengan {station_quality_dist.loc[worst_station, 'Good_Air_Days']:.1f}% waktu berkualitas baik/moderat
        
        """)
    
    st.markdown("---")
    
    # ==================== FOOTER ====================
    st.markdown("""
    <div style='text-align: center; padding: 20px; color: #666;'>
        <p><strong>Beijing Air Quality Dashboard</strong></p>
        <p>Data Source: PRSA Multi-Station Dataset (2013-2017)</p>
        <p>© 2026 Data Analytics Team | Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    main()
