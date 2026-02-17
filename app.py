import warnings
import logging
warnings.filterwarnings('ignore')
logging.getLogger('streamlit').setLevel(logging.ERROR)

import streamlit as st
import ee
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Import legal mining sites database
from legal_mining_sites import LEGAL_MINING_AREAS

# --- CONFIGURATION ---
MY_PROJECT_ID = "spectramining"
geolocator = Nominatim(user_agent="spectramining_ai_pro_v6")

# --- CACHED FUNCTIONS FOR PERFORMANCE ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_nearby_places_cached(lat, lon, radius_km=5):
    """
    Cached nearby places lookup - OPTIMIZED
    """
    try:
        query = f"{lat},{lon}"
        results = geolocator.reverse(query, exactly_one=False, language='en', addressdetails=True)
        
        nearby_places = []
        if results:
            for result in results[:3]:  # Only top 3 for speed
                if hasattr(result, 'raw') and 'address' in result.raw:
                    address = result.raw['address']
                    place_name = None
                    place_type = None
                    
                    if 'mall' in address or 'shopping' in address.get('amenity', '').lower():
                        place_name = address.get('mall', address.get('shop', address.get('amenity')))
                        place_type = "Shopping"
                    elif 'school' in address or 'college' in address or 'university' in address:
                        place_name = address.get('school', address.get('college', address.get('university')))
                        place_type = "Education"
                    elif 'hospital' in address or 'clinic' in address:
                        place_name = address.get('hospital', address.get('clinic'))
                        place_type = "Healthcare"
                    
                    if place_name and place_name not in [p['name'] for p in nearby_places]:
                        nearby_places.append({
                            'name': place_name,
                            'type': place_type,
                            'lat': result.latitude,
                            'lon': result.longitude
                        })
        
        return nearby_places[:2]  # Max 2 landmarks
    except:
        return []


def get_mineral_index_at_point(mineral_index_ee, lat, lon, mineral_name='iron'):
    """
    Get mineral index value at a specific point
    """
    try:
        point = ee.Geometry.Point([lon, lat])
        sample = mineral_index_ee.sample(region=point, scale=10, geometries=True).first()
        if sample:
            mineral_value = sample.get(f'{mineral_name}_index').getInfo()
            return mineral_value
        return None
    except:
        return None


def classify_location(lat, lon, mineral_coverage, mineral_name='iron'):
    """
    AI Classification based on proximity to legal mining areas and mineral detection
    """
    search_point = (lat, lon)
    nearby_mines = []
    min_distance = float('inf')
    nearest_mine = None
    
    mineral_type_map = {
        'iron': 'Iron Ore',
        'aluminum': 'Bauxite/Aluminum',
        'copper': 'Copper'
    }
    
    target_mine_type = mineral_type_map.get(mineral_name, 'Iron Ore')
    
    for mine_name, (mine_lat, mine_lon, country, mine_type) in LEGAL_MINING_AREAS.items():
        if mine_type != target_mine_type:
            continue
            
        mine_point = (mine_lat, mine_lon)
        distance = geodesic(search_point, mine_point).kilometers
        
        if distance <= 10:
            nearby_mines.append({
                'name': mine_name,
                'distance': distance,
                'country': country,
                'type': mine_type
            })
        
        if distance < min_distance:
            min_distance = distance
            nearest_mine = mine_name
    
    if nearby_mines:
        classification = "Legal Mining Area"
        classification_type = "mining"
    else:
        mineral_display = mineral_name.capitalize()
        if mineral_coverage > 10:
            classification = f"Natural - High Potential {mineral_display} Deposits"
            classification_type = "high_potential"
        elif mineral_coverage > 3:
            classification = f"Natural - Moderate Potential {mineral_display} Deposits"
            classification_type = "moderate_potential"
        else:
            classification = f"Natural - Low {mineral_display} Signature"
            classification_type = "low_potential"
    
    return classification, classification_type, nearby_mines, min_distance, nearest_mine


@st.cache_resource
def init_gee():
    try:
        ee.Initialize(project=MY_PROJECT_ID)
        return True
    except Exception as e:
        st.error(f"⚠️ Earth Engine Initialization Failed: {e}")
        return False


# Initialize session state
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'results' not in st.session_state:
    st.session_state.results = None
if 'trigger_scan' not in st.session_state:
    st.session_state.trigger_scan = False
if 'selected_mineral' not in st.session_state:
    st.session_state.selected_mineral = 'iron'
if 'previous_sensitivity' not in st.session_state:
    st.session_state.previous_sensitivity = "High"

# --- PAGE CONFIG - SIDEBAR ALWAYS EXPANDED ---
st.set_page_config(
    layout="wide",
    page_title="SpectraMining AI",
    page_icon="🛰️",
    initial_sidebar_state="expanded"  # ALWAYS EXPANDED
)

# --- OPTIMIZED CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #2d1b3d 100%);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar Toggle Button - Enhanced */
    [data-testid="collapsedControl"] {
        background: linear-gradient(135deg, #E63946 0%, #FF6B6B 100%) !important;
        border-radius: 0 12px 12px 0 !important;
        color: white !important;
        padding: 12px 8px !important;
        box-shadow: 0 4px 16px rgba(230, 57, 70, 0.5) !important;
        transition: all 0.3s ease !important;
    }
    
    [data-testid="collapsedControl"]:hover {
        box-shadow: 0 6px 20px rgba(230, 57, 70, 0.7) !important;
        transform: translateX(3px) !important;
    }
    
    [data-testid="collapsedControl"] svg {
        fill: white !important;
        width: 24px !important;
        height: 24px !important;
    }
    
    .main-header {
        text-align: center;
        padding: 1.5rem 0 1rem 0;
        background: linear-gradient(135deg, rgba(230, 57, 70, 0.1) 0%, rgba(69, 123, 157, 0.1) 100%);
        border-radius: 20px;
        margin-bottom: 1.5rem;
        border: 2px solid rgba(230, 57, 70, 0.3);
        box-shadow: 0 8px 32px rgba(230, 57, 70, 0.2);
    }
    
    .main-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(135deg, #E63946 0%, #FF6B6B 50%, #FFE66D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: 3px;
    }
    
    .subtitle {
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.2rem;
        color: #A8DADC;
        font-weight: 400;
        margin-top: 0.5rem;
        letter-spacing: 2px;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f3a 0%, #2d1b3d 100%);
        border-right: 2px solid rgba(230, 57, 70, 0.3);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #FFE66D !important;
        font-family: 'Orbitron', sans-serif;
    }
    
    .stTextInput input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid rgba(230, 57, 70, 0.3) !important;
        border-radius: 10px !important;
        color: #fff !important;
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.1rem;
        padding: 0.75rem !important;
    }
    
    .stButton button {
        background: linear-gradient(135deg, #E63946 0%, #FF6B6B 100%) !important;
        color: white !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: 700;
        font-size: 1.1rem;
        padding: 0.7rem 1.5rem !important;
        border-radius: 15px !important;
        border: none !important;
        box-shadow: 0 8px 32px rgba(230, 57, 70, 0.4);
        transition: all 0.3s ease;
        letter-spacing: 2px;
    }
    
    .stButton button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(230, 57, 70, 0.6);
    }
    
    /* Optimized Slider */
    .stSlider {
        padding: 0.3rem 0 !important;
    }
    
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #E63946 0%, #FF6B6B 50%, #FFE66D 100%) !important;
    }
    
    .stSlider [role="slider"] {
        background: linear-gradient(135deg, #E63946 0%, #FF6B6B 100%) !important;
        width: 18px !important;
        height: 18px !important;
        box-shadow: 0 4px 12px rgba(230, 57, 70, 0.5) !important;
    }
    
    [data-testid="stMetric"] {
        background: rgba(230, 57, 70, 0.1);
        padding: 0.8rem;
        border-radius: 15px;
        border: 2px solid rgba(230, 57, 70, 0.3);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
        margin-bottom: 0.4rem;
    }
    
    [data-testid="stMetric"] label {
        color: #A8DADC !important;
        font-family: 'Rajdhani', sans-serif;
        font-size: 0.85rem !important;
        font-weight: 600;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #FFE66D !important;
        font-family: 'Orbitron', sans-serif;
        font-size: 1.6rem !important;
        font-weight: 700;
    }
    
    .stProgress > div > div {
        background: linear-gradient(90deg, #E63946 0%, #FF6B6B 50%, #FFE66D 100%);
        border-radius: 10px;
    }
    
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        color: #FFE66D !important;
    }
    
    .stats-card {
        background: linear-gradient(135deg, rgba(230, 57, 70, 0.1) 0%, rgba(69, 123, 157, 0.1) 100%);
        padding: 1.2rem;
        border-radius: 15px;
        border: 2px solid rgba(230, 57, 70, 0.3);
        margin: 0.8rem 0;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
    }
    
    .stats-title {
        font-family: 'Orbitron', sans-serif;
        color: #FFE66D;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
    }
    
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
    
    iframe {
        display: block;
        margin: 0;
        padding: 0;
    }
    
    div[data-testid="stHorizontalBlock"] {
        gap: 0.8rem;
    }
    
    .element-container {
        margin-bottom: 0.3rem;
    }
    
    /* Performance: Reduce animations */
    * {
        animation-duration: 0.2s !important;
        transition-duration: 0.2s !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🛰️ SPECTRAMINING AI</h1>
    <p class="subtitle">Advanced Satellite-Based Multi-Mineral Detection & Geological Analysis Platform</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 0.6rem 0; background: linear-gradient(135deg, rgba(230, 57, 70, 0.15) 0%, rgba(69, 123, 157, 0.15) 100%); border-radius: 12px; margin-bottom: 0.8rem; border: 2px solid rgba(230, 57, 70, 0.3);">
        <div style="font-family: 'Orbitron', sans-serif; font-size: 1rem; font-weight: 900; background: linear-gradient(135deg, #E63946 0%, #FF6B6B 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🛰️ CONTROL PANEL
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Location Search
    st.markdown("#### 📍 Location")
    search_query = st.text_input(
        "Search Site or Region",
        value="Bailadila, India",
        placeholder="e.g., Chuquicamata, Chile",
        help="Enter mine name, city, or coordinates",
        label_visibility="visible"
    )
    
    if 'last_search_query' not in st.session_state:
        st.session_state.last_search_query = ""
    
    # New Analysis button
    if st.session_state.analysis_complete:
        if st.button("🔄 New Analysis", use_container_width=True, key="new_analysis"):
            if search_query != st.session_state.last_search_query:
                st.session_state.analysis_complete = False
                st.session_state.results = None
                st.session_state.trigger_scan = True
                st.rerun()
            else:
                st.warning("⚠️ Enter a new location first")
    
    st.markdown("---")
    
    # MINERAL SWAPPING BUTTONS
    st.markdown("#### 🧪 Active Mineral")
    
    col_fe, col_al, col_cu = st.columns(3)
    
    with col_fe:
        fe_active = st.session_state.selected_mineral == 'iron'
        if st.button("🔴\nFe", use_container_width=True, 
                     type="primary" if fe_active else "secondary",
                     key="btn_iron"):
            if not fe_active:
                st.session_state.selected_mineral = 'iron'
                if st.session_state.analysis_complete:
                    st.rerun()
    
    with col_al:
        al_active = st.session_state.selected_mineral == 'aluminum'
        if st.button("⚪\nAl", use_container_width=True,
                     type="primary" if al_active else "secondary",
                     key="btn_aluminum"):
            if not al_active:
                st.session_state.selected_mineral = 'aluminum'
                if st.session_state.analysis_complete:
                    st.rerun()
    
    with col_cu:
        cu_active = st.session_state.selected_mineral == 'copper'
        if st.button("🟠\nCu", use_container_width=True,
                     type="primary" if cu_active else "secondary",
                     key="btn_copper"):
            if not cu_active:
                st.session_state.selected_mineral = 'copper'
                if st.session_state.analysis_complete:
                    st.rerun()
    
    mineral_names = {
        'iron': '🔴 Iron (Fe)',
        'aluminum': '⚪ Aluminum (Al)',
        'copper': '🟠 Copper (Cu)'
    }
    st.info(f"**Active:** {mineral_names[st.session_state.selected_mineral]}")
    
    selected_mineral_key = st.session_state.selected_mineral
    
    # Detection Sensitivity
    st.markdown("#### ⚙️ Detection Settings")
    
    mineral_thresholds = {
        'iron': {"Low": 2.0, "Medium": 1.6, "High": 1.3, "Ultra": 1.0},
        'aluminum': {"Low": 1.5, "Medium": 1.3, "High": 1.2, "Ultra": 1.0},
        'copper': {"Low": 2.0, "Medium": 1.7, "High": 1.5, "Ultra": 1.2}
    }
    
    sensitivity = st.select_slider(
        "Sensitivity Level",
        options=["Low", "Medium", "High", "Ultra"],
        value=st.session_state.previous_sensitivity,
        help="Adjust detection threshold",
        key="sensitivity_slider",
        label_visibility="visible"
    )
    
    # Store current sensitivity
    st.session_state.previous_sensitivity = sensitivity
    
    mineral_threshold = mineral_thresholds[selected_mineral_key][sensitivity]
    
    st.caption(f"Threshold: **{mineral_threshold}** | Scan Radius: **10 km**")
    
    # Update threshold if changed
    if st.session_state.analysis_complete and st.session_state.results:
        old_threshold = st.session_state.results.get(f'{selected_mineral_key}_threshold', mineral_threshold)
        
        if abs(mineral_threshold - old_threshold) > 0.01:
            st.session_state.results[f'{selected_mineral_key}_threshold'] = mineral_threshold
            st.info(f"🔄 Updated: **{sensitivity}** ({mineral_threshold})")
    
    st.markdown("---")
    
    # Time Range Selection
    st.markdown("#### 📅 Imagery Period")
    date_range = st.selectbox(
        "Time Range",
        ["Last Year", "Last 2 Years", "Last 3 Years", "All Available (2020+)"],
        index=2,
        help="Longer periods = more cloud-free images",
        label_visibility="collapsed"
    )
    
    date_map = {
        "Last Year": "2025-02-15",
        "Last 2 Years": "2024-02-15",
        "Last 3 Years": "2023-02-15",
        "All Available (2020+)": "2020-01-01"
    }
    start_date = date_map[date_range]
    
    # Fixed cloud threshold
    cloud_threshold = 40
    st.caption("☁️ **Cloud Filter:** < 40% (Optimal)")
    
    st.markdown("---")
    
    if st.session_state.analysis_complete:
        st.success("✅ **Analysis Ready**")
        st.caption("Adjust settings for updates")
    
    st.markdown("---")
    
    mineral_display = mineral_names[selected_mineral_key]
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(230, 57, 70, 0.1) 0%, rgba(69, 123, 157, 0.1) 100%); padding: 0.8rem; border-radius: 12px; border: 2px solid rgba(230, 57, 70, 0.3);">
        <div style="font-family: 'Orbitron', sans-serif; color: #FFE66D; font-size: 0.85rem; font-weight: 700; margin-bottom: 0.4rem;">⚡ SYSTEM</div>
        <div style="color: #4CAF50; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.2rem;">● ONLINE</div>
        <div style="color: #A8DADC; font-size: 0.7rem; line-height: 1.3;">
            <b>Satellite:</b> Sentinel-2 SR<br>
            <b>Engine:</b> Google Earth<br>
            <b>Active:</b> {mineral_display}<br>
            <b>Project:</b> {MY_PROJECT_ID}
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN APPLICATION ---
scan_button = st.button("🚀 INITIATE SCAN", use_container_width=True, disabled=st.session_state.analysis_complete)

should_scan = (scan_button or st.session_state.trigger_scan) and not st.session_state.analysis_complete

if should_scan:
    
    st.session_state.trigger_scan = False
    
    if not init_gee():
        st.stop()
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.markdown("**📍 Geocoding location...**")
        progress_bar.progress(10)
        
        location = geolocator.geocode(search_query)
        if not location:
            st.error(f"❌ Location not found: '{search_query}'")
            st.stop()
        
        st.session_state.last_search_query = search_query
        
        st.success(f"✓ Location: **{location.address}**")
        progress_bar.progress(20)
        
        status_text.markdown("**🌍 Defining region...**")
        poi = ee.Geometry.Point([location.longitude, location.latitude])
        region = poi.buffer(10000).bounds()
        progress_bar.progress(30)
        
        status_text.markdown("**🛰️ Fetching imagery...**")
        
        s2_col = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                  .filterBounds(region)
                  .filterDate(start_date, '2026-02-15')
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_threshold))
                  .sort('CLOUDY_PIXEL_PERCENTAGE'))
        
        num_images = s2_col.size().getInfo()
        
        if num_images == 0:
            st.error(f"⚠️ No imagery found with <{cloud_threshold}% clouds.")
            st.warning("Try expanding time range")
            st.stop()
        
        st.info(f"📡 Retrieved **{num_images}** images")
        progress_bar.progress(50)
        
        s2_img = s2_col.median().divide(10000).clip(region)
        
        status_text.markdown("**🧪 Computing mineral indices...**")
        progress_bar.progress(60)
        
        # IRON
        red_band = s2_img.select('B4')
        blue_band = s2_img.select('B2')
        iron_index = red_band.divide(blue_band).rename('iron_index')
        
        # ALUMINUM
        swir1_band = s2_img.select('B11')
        swir2_band = s2_img.select('B12')
        aluminum_index = swir1_band.divide(swir2_band).rename('aluminum_index')
        
        # COPPER
        green_band = s2_img.select('B3')
        nir_band = s2_img.select('B8')
        copper_index = red_band.divide(green_band).multiply(
            nir_band.divide(red_band)
        ).rename('copper_index')
        
        # Get statistics - OPTIMIZED
        iron_stats = iron_index.reduceRegion(
            reducer=ee.Reducer.minMax().combine(
                ee.Reducer.mean(), '', True).combine(
                ee.Reducer.percentile([10, 90]), '', True),
            geometry=region,
            scale=50,  # Reduced from 30 for speed
            maxPixels=1e9,
            bestEffort=True
        ).getInfo()
        
        aluminum_stats = aluminum_index.reduceRegion(
            reducer=ee.Reducer.minMax().combine(
                ee.Reducer.mean(), '', True).combine(
                ee.Reducer.percentile([10, 90]), '', True),
            geometry=region,
            scale=50,
            maxPixels=1e9,
            bestEffort=True
        ).getInfo()
        
        copper_stats = copper_index.reduceRegion(
            reducer=ee.Reducer.minMax().combine(
                ee.Reducer.mean(), '', True).combine(
                ee.Reducer.percentile([10, 90]), '', True),
            geometry=region,
            scale=50,
            maxPixels=1e9,
            bestEffort=True
        ).getInfo()
        
        progress_bar.progress(70)
        
        # Calculate coverage
        iron_threshold_value = mineral_thresholds['iron'][sensitivity]
        aluminum_threshold_value = mineral_thresholds['aluminum'][sensitivity]
        copper_threshold_value = mineral_thresholds['copper'][sensitivity]
        
        iron_mask = iron_index.gt(iron_threshold_value)
        iron_coverage_stats = iron_mask.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=50,
            maxPixels=1e9,
            bestEffort=True
        ).getInfo()
        iron_coverage = (iron_coverage_stats.get('iron_index', 0)) * 100
        
        aluminum_mask = aluminum_index.gt(aluminum_threshold_value)
        aluminum_coverage_stats = aluminum_mask.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=50,
            maxPixels=1e9,
            bestEffort=True
        ).getInfo()
        aluminum_coverage = (aluminum_coverage_stats.get('aluminum_index', 0)) * 100
        
        copper_mask = copper_index.gt(copper_threshold_value)
        copper_coverage_stats = copper_mask.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=50,
            maxPixels=1e9,
            bestEffort=True
        ).getInfo()
        copper_coverage = (copper_coverage_stats.get('copper_index', 0)) * 100
        
        progress_bar.progress(80)
        status_text.markdown("**🗺️ Rendering maps...**")
        
        # Get tile URLs
        iron_min = max(iron_threshold_value, iron_stats.get('iron_index_p10', iron_threshold_value))
        iron_max = min(iron_stats.get('iron_index_p90', 3.0), 3.5)
        
        aluminum_min = max(aluminum_threshold_value, aluminum_stats.get('aluminum_index_p10', aluminum_threshold_value))
        aluminum_max = min(aluminum_stats.get('aluminum_index_p90', 2.0), 2.5)
        
        copper_min = max(copper_threshold_value, copper_stats.get('copper_index_p10', copper_threshold_value))
        copper_max = min(copper_stats.get('copper_index_p90', 2.5), 3.0)
        
        true_color_viz = {
            'bands': ['B4', 'B3', 'B2'],
            'min': 0.0,
            'max': 0.3,
            'gamma': 1.3
        }
        true_color_tile = s2_img.getMapId(true_color_viz)
        
        iron_masked = iron_index.updateMask(iron_index.gt(iron_threshold_value))
        iron_viz = {
            'min': iron_min,
            'max': iron_max,
            'palette': ['#FFA500', '#FF6347', '#FF4500', '#DC143C', '#8B0000', '#4A0000']
        }
        iron_tile = iron_masked.getMapId(iron_viz)
        
        aluminum_masked = aluminum_index.updateMask(aluminum_index.gt(aluminum_threshold_value))
        aluminum_viz = {
            'min': aluminum_min,
            'max': aluminum_max,
            'palette': ['#E0F7FA', '#4DD0E1', '#00BCD4', '#0097A7', '#00838F', '#006064']
        }
        aluminum_tile = aluminum_masked.getMapId(aluminum_viz)
        
        copper_masked = copper_index.updateMask(copper_index.gt(copper_threshold_value))
        copper_viz = {
            'min': copper_min,
            'max': copper_max,
            'palette': ['#FFEB3B', '#FFC107', '#FF9800', '#FF5722', '#8D6E63', '#5D4037']
        }
        copper_tile = copper_masked.getMapId(copper_viz)
        
        false_color_viz = {
            'bands': ['B8', 'B4', 'B3'],
            'min': 0.0,
            'max': 0.4,
            'gamma': 1.2
        }
        false_color_tile = s2_img.getMapId(false_color_viz)
        
        progress_bar.progress(90)
        
        # Store in session
        st.session_state.iron_index_ee = iron_index
        st.session_state.aluminum_index_ee = aluminum_index
        st.session_state.copper_index_ee = copper_index
        st.session_state.s2_img_ee = s2_img
        
        # AI Classification
        mineral_coverage_for_classification = {
            'iron': iron_coverage,
            'aluminum': aluminum_coverage,
            'copper': copper_coverage
        }[selected_mineral_key]
        
        classification, class_type, nearby_mines, nearest_distance, nearest_mine = classify_location(
            location.latitude, 
            location.longitude, 
            mineral_coverage_for_classification,
            selected_mineral_key
        )
        
        # Store results
        st.session_state.results = {
            'location': location,
            'num_images': num_images,
            'iron_coverage': iron_coverage,
            'aluminum_coverage': aluminum_coverage,
            'copper_coverage': copper_coverage,
            'iron_stats': iron_stats,
            'aluminum_stats': aluminum_stats,
            'copper_stats': copper_stats,
            'iron_threshold': iron_threshold_value,
            'aluminum_threshold': aluminum_threshold_value,
            'copper_threshold': copper_threshold_value,
            'true_color_tile': true_color_tile,
            'iron_tile': iron_tile,
            'aluminum_tile': aluminum_tile,
            'copper_tile': copper_tile,
            'false_color_tile': false_color_tile,
            'start_date': start_date,
            'cloud_threshold': cloud_threshold,
            'classification': classification,
            'classification_type': class_type,
            'nearby_mines': nearby_mines,
            'nearest_distance': nearest_distance,
            'nearest_mine': nearest_mine,
            'region': region,
            'iron_min': iron_min,
            'iron_max': iron_max,
            'aluminum_min': aluminum_min,
            'aluminum_max': aluminum_max,
            'copper_min': copper_min,
            'copper_max': copper_max
        }
        
        st.session_state.analysis_complete = True
        st.session_state.last_search_query = search_query
        
        progress_bar.progress(100)
        status_text.markdown("**✅ Complete!**")
        
        progress_bar.empty()
        status_text.empty()
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.exception(e)

# --- DISPLAY RESULTS ---
if st.session_state.analysis_complete and st.session_state.results:
    
    results = st.session_state.results
    location = results['location']
    
    current_mineral = st.session_state.selected_mineral
    
    mineral_config = {
        'iron': {
            'symbol': '🔴',
            'name': 'Iron',
            'abbr': 'Fe',
            'color': '#E63946',
            'emoji': '🔴'
        },
        'aluminum': {
            'symbol': '⚪',
            'name': 'Aluminum',
            'abbr': 'Al',
            'color': '#00BCD4',
            'emoji': '⚪'
        },
        'copper': {
            'symbol': '🟠',
            'name': 'Copper',
            'abbr': 'Cu',
            'color': '#FF9800',
            'emoji': '🟠'
        }
    }
    
    config = mineral_config[current_mineral]
    current_coverage = results[f'{current_mineral}_coverage']
    
    # Check if threshold changed - OPTIMIZED
    if f'{current_mineral}_index_ee' in st.session_state:
        current_threshold = mineral_thresholds[current_mineral][st.session_state.previous_sensitivity]
        stored_threshold = results.get(f'{current_mineral}_threshold', current_threshold)
        
        if abs(current_threshold - stored_threshold) > 0.01:
            with st.spinner(f"🔄 Updating..."):
                mineral_index = st.session_state[f'{current_mineral}_index_ee']
                region = results.get('region')
                
                mineral_mask = mineral_index.gt(current_threshold)
                coverage_stats = mineral_mask.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=region,
                    scale=50,
                    maxPixels=1e9,
                    bestEffort=True
                ).getInfo()
                
                new_mineral_coverage = (coverage_stats.get(f'{current_mineral}_index', 0)) * 100
                
                mineral_masked = mineral_index.updateMask(mineral_index.gt(current_threshold))
                
                palettes = {
                    'iron': ['#FFA500', '#FF6347', '#FF4500', '#DC143C', '#8B0000', '#4A0000'],
                    'aluminum': ['#E0F7FA', '#4DD0E1', '#00BCD4', '#0097A7', '#00838F', '#006064'],
                    'copper': ['#FFEB3B', '#FFC107', '#FF9800', '#FF5722', '#8D6E63', '#5D4037']
                }
                
                mineral_viz = {
                    'min': max(current_threshold, results.get(f'{current_mineral}_min', current_threshold)),
                    'max': results.get(f'{current_mineral}_max', 3.5),
                    'palette': palettes[current_mineral]
                }
                new_mineral_tile = mineral_masked.getMapId(mineral_viz)
                
                classification, class_type, nearby_mines, nearest_distance, nearest_mine = classify_location(
                    location.latitude,
                    location.longitude,
                    new_mineral_coverage,
                    current_mineral
                )
                
                st.session_state.results[f'{current_mineral}_coverage'] = new_mineral_coverage
                st.session_state.results[f'{current_mineral}_threshold'] = current_threshold
                st.session_state.results[f'{current_mineral}_tile'] = new_mineral_tile
                st.session_state.results['classification'] = classification
                st.session_state.results['classification_type'] = class_type
                
                results = st.session_state.results
                current_coverage = new_mineral_coverage
                
                st.rerun()
    
    with st.container():
        col1, col2 = st.columns([7, 3])
    
    with col2:
        st.markdown(f"### 📊 {config['symbol']} {config['name'].upper()}")
        
        class_type = results.get('classification_type', 'unknown')
        classification = results.get('classification', 'Unknown')
        
        if class_type == 'mining':
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(56, 142, 60, 0.2) 100%);
                padding: 1rem;
                border-radius: 12px;
                border: 3px solid #4CAF50;
                margin-bottom: 0.8rem;
                box-shadow: 0 6px 24px rgba(76, 175, 80, 0.4);
            ">
                <div style="font-family: 'Orbitron', sans-serif; color: #4CAF50; font-size: 0.8rem; font-weight: 700; margin-bottom: 0.2rem;">🤖 AI CLASSIFICATION</div>
                <div style="font-family: 'Orbitron', sans-serif; color: #66BB6A; font-size: 1rem; font-weight: 900;">⚖️ LEGAL MINING</div>
            </div>
            """, unsafe_allow_html=True)
            
            if results.get('nearby_mines'):
                st.success(f"✅ {len(results['nearby_mines'])} mine(s)")
                with st.expander("📍 Mines"):
                    for mine in results['nearby_mines'][:2]:  # Max 2
                        st.write(f"**{mine['name'][:25]}...**")
                        st.caption(f"{mine['distance']:.1f} km")
        else:
            if class_type == 'high_potential':
                color, icon = "#FF9800", "🌟"
            elif class_type == 'moderate_potential':
                color, icon = "#2196F3", "💎"
            else:
                color, icon = "#9E9E9E", "🌍"
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(33, 150, 243, 0.2) 0%, rgba(25, 118, 210, 0.2) 100%);
                padding: 1rem;
                border-radius: 12px;
                border: 3px solid {color};
                margin-bottom: 0.8rem;
                box-shadow: 0 6px 24px rgba(33, 150, 243, 0.4);
            ">
                <div style="font-family: 'Orbitron', sans-serif; color: {color}; font-size: 0.8rem; font-weight: 700; margin-bottom: 0.2rem;">🤖 CLASSIFICATION</div>
                <div style="font-family: 'Orbitron', sans-serif; color: {color}; font-size: 0.9rem; font-weight: 900;">{icon} {classification.replace('Natural - ', '')}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if results.get('nearest_mine'):
                st.info(f"📌 {results['nearest_mine'][:25]}... ({results['nearest_distance']:.0f}km)")
        
        st.markdown("---")
        
        # SPECIFIC MINERAL COVERAGE
        st.metric(
            label=f"{config['symbol']} {config['name']} Coverage",
            value=f"{current_coverage:.1f}%",
            delta="10km radius",
            help=f"{config['name']} mineral signature"
        )
        
        st.markdown(f"**Detection Confidence:**")
        confidence = min(current_coverage / 30, 1.0)
        st.progress(confidence)
        
        confidence_percent = confidence * 100
        if confidence_percent >= 75:
            st.success(f"🎯 **{confidence_percent:.0f}%** - Strong")
        elif confidence_percent >= 50:
            st.info(f"📊 **{confidence_percent:.0f}%** - Significant")
        elif confidence_percent >= 25:
            st.warning(f"⚠️ **{confidence_percent:.0f}%** - Weak")
        else:
            st.info(f"ℹ️ **{confidence_percent:.0f}%** - Limited")
        
        st.markdown("---")
        
        if current_coverage > 20:
            st.success(f"{config['emoji']} **HIGH GRADE**")
        elif current_coverage > 10:
            st.warning(f"{config['emoji']} **MODERATE**")
        elif current_coverage > 3:
            st.info(f"{config['emoji']} **LOW GRADE**")
        else:
            st.info(f"⚪ **TRACE**")
        
        st.markdown("---")
        
        st.markdown(f"""
        <div class="stats-card">
            <div class="stats-title">📈 {config['symbol']} SPECTRAL DATA</div>
        </div>
        """, unsafe_allow_html=True)
        
        mineral_stats = results[f'{current_mineral}_stats']
        spec_col1, spec_col2 = st.columns(2)
        with spec_col1:
            st.metric("Min", f"{mineral_stats.get(f'{current_mineral}_index_min', 0):.2f}")
            st.metric("Mean", f"{mineral_stats.get(f'{current_mineral}_index_mean', 0):.2f}")
        with spec_col2:
            st.metric("Max", f"{mineral_stats.get(f'{current_mineral}_index_max', 0):.2f}")
            st.metric("90th", f"{mineral_stats.get(f'{current_mineral}_index_p90', 0):.2f}")
        
        st.markdown("---")
    
    with col1:
        st.markdown(f"### 🗺️ {config['symbol']} {config['name'].upper()} - {location.address.split(',')[0]}")
        
        # HIGH PERFORMANCE MAP - only safe/tested parameters
        m = folium.Map(
            location=[location.latitude, location.longitude],
            zoom_start=13,
            tiles='OpenStreetMap',
            control_scale=True
        )
        
        # Google Satellite
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google',
            name='🛰️ Satellite',
            overlay=False,
            control=True
        ).add_to(m)

        # Landmarks - CACHED
        nearby_places = get_nearby_places_cached(location.latitude, location.longitude, radius_km=5)

        if nearby_places:
            for place in nearby_places:
                icon_color = {'Shopping': 'blue', 'Education': 'purple', 'Healthcare': 'red'}.get(place['type'], 'gray')
                folium.Marker(
                    [place['lat'], place['lon']],
                    popup=folium.Popup(str(place['name']), max_width=150),
                    tooltip=str(place['name']),
                    icon=folium.Icon(color=icon_color, icon='info-sign')
                ).add_to(m)

        # True Color - extract URL string explicitly
        true_color_url = str(results['true_color_tile']['tile_fetcher'].url_format)
        folium.TileLayer(
            tiles=true_color_url,
            attr='Sentinel-2',
            name='📷 True Color',
            overlay=True,
            control=True,
            opacity=1.0
        ).add_to(m)

        # Mineral Heatmap - extract URL string explicitly
        mineral_tile = results[f'{current_mineral}_tile']
        mineral_url = str(mineral_tile['tile_fetcher'].url_format)
        folium.TileLayer(
            tiles=mineral_url,
            attr=str(config['name']),
            name=f'{config["name"]} Heatmap',
            overlay=True,
            control=True,
            opacity=0.7
        ).add_to(m)

        # False Color - extract URL string explicitly
        false_color_url = str(results['false_color_tile']['tile_fetcher'].url_format)
        folium.TileLayer(
            tiles=false_color_url,
            attr='NIR',
            name='False Color (NIR)',
            overlay=True,
            control=True,
            opacity=1.0
        ).add_to(m)

        # Center marker
        folium.Marker(
            [location.latitude, location.longitude],
            popup=folium.Popup(f"{config['name']}: {current_coverage:.1f}%", max_width=200),
            tooltip="Analysis Center",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)

        # Analysis radius
        folium.Circle(
            location=[location.latitude, location.longitude],
            radius=10000,
            color=str(config['color']),
            fill=False,
            weight=2,
            opacity=0.5,
            popup=folium.Popup("10km Radius", max_width=100)
        ).add_to(m)

        # Mines
        if results.get('nearby_mines'):
            for mine in results['nearby_mines'][:2]:
                for mine_name, (lat, lon, country, mine_type) in LEGAL_MINING_AREAS.items():
                    if mine_name == mine['name']:
                        folium.Marker(
                            [lat, lon],
                            popup=folium.Popup(f"{mine['name'][:30]} | {mine['distance']:.1f}km", max_width=200),
                            tooltip=str(mine['name'][:30]),
                            icon=folium.Icon(color='green', icon='industry', prefix='fa')
                        ).add_to(m)
                        break

        folium.LayerControl(collapsed=False).add_to(m)

        # Render map - use integer width, not None
        map_data = st_folium(
            m,
            height=550,
            use_container_width=True,
            key=f"map_{current_mineral}_{st.session_state.previous_sensitivity}",
            returned_objects=["last_clicked"]
        )
        
        # Handle clicks - SIMPLIFIED
        if map_data and map_data.get("last_clicked"):
            clicked_lat = map_data["last_clicked"]["lat"]
            clicked_lng = map_data["last_clicked"]["lng"]
            
            distance = geodesic((location.latitude, location.longitude), (clicked_lat, clicked_lng)).kilometers
            
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                st.metric("Lat", f"{clicked_lat:.5f}°")
            with col_c2:
                st.metric("Lon", f"{clicked_lng:.5f}°")
            with col_c3:
                st.metric("Dist", f"{distance:.2f}km")
            
            if distance <= 10:
                if f'{current_mineral}_index_ee' in st.session_state:
                    mineral_value = get_mineral_index_at_point(
                        st.session_state[f'{current_mineral}_index_ee'],
                        clicked_lat, clicked_lng, current_mineral
                    )
                    
                    if mineral_value:
                        threshold = results.get(f'{current_mineral}_threshold', 1.3)
                        
                        if mineral_value > threshold:
                            st.success(f"{config['emoji']} **{mineral_value:.3f}** - Above threshold!")
                        else:
                            st.info(f"⚪ **{mineral_value:.3f}** - Below threshold")
            else:
                st.warning("⚠️ Outside 10km radius")
        
        # Legend - COMPACT
        legend_gradients = {
            'iron': 'linear-gradient(to right, #FFA500, #FF6347, #FF4500, #DC143C, #8B0000)',
            'aluminum': 'linear-gradient(to right, #E0F7FA, #4DD0E1, #00BCD4, #0097A7, #00838F)',
            'copper': 'linear-gradient(to right, #FFEB3B, #FFC107, #FF9800, #FF5722, #8D6E63)'
        }
        
        st.markdown(f"""
        <div style="background: rgba(230, 57, 70, 0.1); padding: 0.8rem; border-radius: 12px; border: 2px solid {config['color']}; margin-top: 0.8rem;">
            <div style="font-family: 'Orbitron', sans-serif; color: #FFE66D; font-size: 0.9rem; font-weight: 700; margin-bottom: 0.5rem;">🎨 LEGEND</div>
            <div style="width: 100%; height: 30px; background: {legend_gradients[current_mineral]}; border-radius: 5px; box-shadow: 0 3px 10px rgba(0,0,0,0.4);"></div>
            <div style="display: flex; justify-content: space-between; color: #A8DADC; font-size: 0.75rem; margin-top: 0.3rem;">
                <span>Low</span><span>Medium</span><span>High</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Technical Details - COMPACT
    st.markdown("### 📋 DETAILS")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.markdown(f"""
        **Satellite:**
        - Sentinel-2 SR
        - Images: {results['num_images']}
        - Clouds: <40%
        - Resolution: 10m
        """)
    
    with col_b:
        index_formulas = {
            'iron': 'Red/Blue',
            'aluminum': 'SWIR1/SWIR2',
            'copper': '(R/G)×(NIR/R)'
        }
        
        st.markdown(f"""
        **Analysis:**
        - {config['name']} ({config['abbr']})
        - Index: {index_formulas[current_mineral]}
        - Threshold: {results[f'{current_mineral}_threshold']:.2f}
        - Radius: 10km
        """)
    
    with col_c:
        st.markdown(f"""
        **Location:**
        - Lat: {location.latitude:.5f}°
        - Lon: {location.longitude:.5f}°
        - Area: ~314 km²
        """)

# --- FOOTER ---
st.markdown("""
<div style="text-align: center; color: #6c757d; font-family: 'Rajdhani', sans-serif; padding: 0.8rem 0; margin-top: 1.5rem;">
    <p>🛰️ <strong>SpectraMining AI</strong> | Sentinel-2 ESA & Google Earth Engine</p>
</div>

""", unsafe_allow_html=True)
