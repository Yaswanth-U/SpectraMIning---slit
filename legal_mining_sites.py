"""
Legal Mining Areas Database
Contains coordinates of 149 verified legal mining sites worldwide

Usage:
    from legal_mining_database import LEGAL_MINING_AREAS, get_mines_by_type, get_mine_count
"""

# --- LEGAL MINING AREAS DATASET ---
LEGAL_MINING_AREAS = {
    # ==================== IRON ORE MINES ====================
    # INDIA
    "Bailadila Iron Ore Complex": (18.6297, 81.3025, "India", "Iron Ore"),
    "NMDC Bailadila Mine 14": (18.6500, 81.2800, "India", "Iron Ore"),
    "Donimalai Iron Ore Mine": (15.1833, 76.9167, "India", "Iron Ore"),
    "Kudremukh Iron Ore Mine": (13.3167, 75.2500, "India", "Iron Ore"),
    "Barbil Iron Ore Mines": (22.1167, 85.3833, "India", "Iron Ore"),
    "Kiriburu Iron Ore Mine": (22.1333, 85.3000, "India", "Iron Ore"),
    "Meghahatuburu Iron Ore Mine": (22.1500, 85.2833, "India", "Iron Ore"),
    "Gua Iron Ore Mines": (22.2167, 85.3833, "India", "Iron Ore"),
    "Noamundi Iron Ore Mine": (22.1667, 85.5000, "India", "Iron Ore"),
    "Chiria Iron Ore Mines": (22.3000, 85.2167, "India", "Iron Ore"),
    
    # BRAZIL
    "Carajás Mine": (-6.0667, -50.2667, "Brazil", "Iron Ore"),
    "Itabira Mine Complex": (-19.6167, -43.2333, "Brazil", "Iron Ore"),
    "Minas Centrais Complex": (-20.3167, -43.7833, "Brazil", "Iron Ore"),
    "Brucutu Mine": (-19.9167, -43.6167, "Brazil", "Iron Ore"),
    "Conceição Mine": (-19.4667, -43.4167, "Brazil", "Iron Ore"),
    "Fábrica Nova Mine": (-20.0833, -43.8500, "Brazil", "Iron Ore"),
    "Alegria Mine": (-19.8333, -43.4833, "Brazil", "Iron Ore"),
    "Capão Xavier Mine": (-19.9500, -43.8667, "Brazil", "Iron Ore"),
    
    # AUSTRALIA
    "Mount Whaleback Mine": (-23.3667, 119.6667, "Australia", "Iron Ore"),
    "Tom Price Mine": (-22.6833, 117.7833, "Australia", "Iron Ore"),
    "Paraburdoo Mine": (-23.1667, 117.6667, "Australia", "Iron Ore"),
    "Yandicoogina Mine": (-22.7000, 119.0833, "Australia", "Iron Ore"),
    "Marandoo Mine": (-22.6167, 118.1000, "Australia", "Iron Ore"),
    "Nammuldi Mine": (-22.6667, 117.9167, "Australia", "Iron Ore"),
    "Cloudbreak Mine": (-22.3000, 119.4500, "Australia", "Iron Ore"),
    "Christmas Creek Mine": (-22.1167, 119.5333, "Australia", "Iron Ore"),
    "West Angelas Mine": (-23.1167, 118.6833, "Australia", "Iron Ore"),
    "Jimblebar Mine": (-23.3333, 119.6167, "Australia", "Iron Ore"),
    "Koodaideri Mine": (-22.4500, 119.5000, "Australia", "Iron Ore"),
    
    # SOUTH AFRICA
    "Sishen Mine": (-27.6500, 23.0167, "South Africa", "Iron Ore"),
    "Kolomela Mine": (-28.3833, 22.8833, "South Africa", "Iron Ore"),
    "Thabazimbi Mine": (-24.5833, 27.4167, "South Africa", "Iron Ore"),
    
    # SWEDEN
    "Kiruna Mine": (67.8556, 20.2253, "Sweden", "Iron Ore"),
    "Malmberget Mine": (67.1833, 20.6667, "Sweden", "Iron Ore"),
    
    # RUSSIA
    "Lebedinsky Mine": (50.9667, 37.6167, "Russia", "Iron Ore"),
    "Stoilensky Mine": (50.8000, 37.9000, "Russia", "Iron Ore"),
    "Mikhailovsky Mine": (51.6833, 35.2667, "Russia", "Iron Ore"),
    "Kachkanarsky Mine": (58.7000, 59.4833, "Russia", "Iron Ore"),
    
    # CHINA
    "Anshan Mine Complex": (41.1083, 122.9900, "China", "Iron Ore"),
    "Qidashan Mine": (41.0833, 123.0833, "China", "Iron Ore"),
    "Dagushan Mine": (41.0167, 122.8833, "China", "Iron Ore"),
    "Gongchangling Mine": (40.9833, 123.2000, "China", "Iron Ore"),
    
    # UKRAINE
    "Kryvyi Rih Mining District": (47.9108, 33.3917, "Ukraine", "Iron Ore"),
    
    # CANADA
    "Mary River Mine": (71.2833, -78.9833, "Canada", "Iron Ore"),
    "IOC Mine": (52.9500, -66.8667, "Canada", "Iron Ore"),
    
    # USA
    "Hibbing Taconite Mine": (47.4271, -92.9377, "USA", "Iron Ore"),
    "Minntac Mine": (47.5333, -92.7000, "USA", "Iron Ore"),
    "United Taconite Mine": (47.5167, -92.3500, "USA", "Iron Ore"),
    "Keetac Mine": (47.4000, -92.8833, "USA", "Iron Ore"),
    
    # MAURITANIA
    "Guelbs Mine": (22.7167, -12.5833, "Mauritania", "Iron Ore"),
    "M'Haoudat Mine": (22.6833, -12.7000, "Mauritania", "Iron Ore"),
    
    # LIBERIA
    "Bong Mine": (6.8833, -10.0500, "Liberia", "Iron Ore"),
    "Nimba Mine": (7.5833, -8.5167, "Liberia", "Iron Ore"),
    
    # IRAN
    "Gol-e-Gohar Mine": (29.1667, 57.3833, "Iran", "Iron Ore"),
    "Chadormalu Mine": (32.4833, 55.6500, "Iran", "Iron Ore"),
    
    # KAZAKHSTAN
    "Sokolov-Sarbai Mine": (52.8833, 62.9500, "Kazakhstan", "Iron Ore"),
    "Lisakovsk Mine": (52.5333, 62.5000, "Kazakhstan", "Iron Ore"),
    
    # ==================== ALUMINUM/BAUXITE MINES ====================
    # AUSTRALIA
    "Weipa Bauxite Mine": (-12.6667, 141.8667, "Australia", "Bauxite/Aluminum"),
    "Gove Bauxite Mine": (-12.2667, 136.8167, "Australia", "Bauxite/Aluminum"),
    "Huntly Bauxite Mine": (-32.5833, 116.0167, "Australia", "Bauxite/Aluminum"),
    "Willowdale Bauxite Mine": (-32.7167, 116.0500, "Australia", "Bauxite/Aluminum"),
    "Boddington Bauxite Mine": (-32.8000, 116.4667, "Australia", "Bauxite/Aluminum"),
    
    # GUINEA
    "Sangaredi Bauxite Mine": (11.1333, -13.7333, "Guinea", "Bauxite/Aluminum"),
    "Boké Bauxite Mine": (10.9500, -14.2833, "Guinea", "Bauxite/Aluminum"),
    "Kamsar Bauxite Mine": (10.6500, -14.6167, "Guinea", "Bauxite/Aluminum"),
    "Dian-Dian Bauxite Mine": (11.2000, -13.6500, "Guinea", "Bauxite/Aluminum"),
    
    # BRAZIL
    "Paragominas Bauxite Mine": (-3.0000, -47.5000, "Brazil", "Bauxite/Aluminum"),
    "Porto Trombetas Bauxite Mine": (-1.4667, -56.3833, "Brazil", "Bauxite/Aluminum"),
    "Juruti Bauxite Mine": (-2.1500, -56.0833, "Brazil", "Bauxite/Aluminum"),
    "Miraí Bauxite Mine": (-20.8667, -42.6167, "Brazil", "Bauxite/Aluminum"),
    "Poços de Caldas Bauxite Mine": (-21.7833, -46.5667, "Brazil", "Bauxite/Aluminum"),
    
    # CHINA
    "Guangxi Bauxite District": (23.7333, 106.6167, "China", "Bauxite/Aluminum"),
    "Shanxi Bauxite District": (37.8667, 112.5500, "China", "Bauxite/Aluminum"),
    "Henan Bauxite District": (34.7667, 113.6500, "China", "Bauxite/Aluminum"),
    "Guizhou Bauxite Mine": (26.5833, 106.7167, "China", "Bauxite/Aluminum"),
    
    # INDIA
    "Odisha Bauxite Mines": (20.2667, 85.8333, "India", "Bauxite/Aluminum"),
    "Gujarat Bauxite Mines": (21.5167, 73.2167, "India", "Bauxite/Aluminum"),
    "Jharkhand Bauxite Mines": (23.3500, 85.3333, "India", "Bauxite/Aluminum"),
    "Chhattisgarh Bauxite Mines": (21.2500, 81.6333, "India", "Bauxite/Aluminum"),
    "Amarkantak Bauxite Mine": (22.6667, 81.7500, "India", "Bauxite/Aluminum"),
    
    # JAMAICA
    "Clarendon Bauxite Mine": (17.9667, -77.2500, "Jamaica", "Bauxite/Aluminum"),
    "St. Ann Bauxite Mine": (18.4333, -77.2000, "Jamaica", "Bauxite/Aluminum"),
    "Manchester Bauxite Mine": (18.0500, -77.5167, "Jamaica", "Bauxite/Aluminum"),
    
    # RUSSIA
    "North Urals Bauxite Mine": (59.5000, 60.2000, "Russia", "Bauxite/Aluminum"),
    "Srednetimanskoe Bauxite Mine": (65.3000, 57.2500, "Russia", "Bauxite/Aluminum"),
    "Ural Bauxite Deposit": (58.0000, 59.5000, "Russia", "Bauxite/Aluminum"),
    
    # VIETNAM
    "Central Highlands Bauxite": (12.6667, 108.0333, "Vietnam", "Bauxite/Aluminum"),
    "Dak Nong Bauxite Mine": (12.2500, 107.7000, "Vietnam", "Bauxite/Aluminum"),
    
    # INDONESIA
    "Bintan Bauxite Mine": (1.0500, 104.4500, "Indonesia", "Bauxite/Aluminum"),
    "Riau Islands Bauxite": (0.9000, 104.4500, "Indonesia", "Bauxite/Aluminum"),
    
    # MALAYSIA
    "Pahang Bauxite District": (3.8000, 103.3200, "Malaysia", "Bauxite/Aluminum"),
    
    # SURINAME
    "Lelydorp Bauxite Mine": (5.7000, -55.2333, "Suriname", "Bauxite/Aluminum"),
    "Paranam Bauxite Mine": (5.6167, -55.0667, "Suriname", "Bauxite/Aluminum"),
    
    # GREECE
    "Parnassos-Giona Bauxite": (38.5333, 22.6167, "Greece", "Bauxite/Aluminum"),
    
    # ==================== COPPER MINES ====================
    # CHILE
    "Escondida Copper Mine": (-24.2667, -69.0833, "Chile", "Copper"),
    "Collahuasi Copper Mine": (-20.9667, -68.7167, "Chile", "Copper"),
    "El Teniente Copper Mine": (-34.0833, -70.3667, "Chile", "Copper"),
    "Los Bronces Copper Mine": (-33.1500, -70.3000, "Chile", "Copper"),
    "Chuquicamata Copper Mine": (-22.3000, -68.9000, "Chile", "Copper"),
    "Radomiro Tomic Copper Mine": (-22.4500, -68.8333, "Chile", "Copper"),
    "Ministro Hales Copper Mine": (-22.3500, -68.9500, "Chile", "Copper"),
    "Los Pelambres Copper Mine": (-31.7833, -70.5500, "Chile", "Copper"),
    "Andina Copper Mine": (-32.8500, -70.2500, "Chile", "Copper"),
    "Centinela Copper Mine": (-23.9667, -69.4500, "Chile", "Copper"),
    
    # PERU
    "Antamina Copper Mine": (-9.3500, -77.1000, "Peru", "Copper"),
    "Cerro Verde Copper Mine": (-16.5167, -71.5833, "Peru", "Copper"),
    "Las Bambas Copper Mine": (-14.1833, -72.2333, "Peru", "Copper"),
    "Toromocho Copper Mine": (-11.5167, -76.1167, "Peru", "Copper"),
    "Antapaccay Copper Mine": (-14.3667, -71.2833, "Peru", "Copper"),
    "Toquepala Copper Mine": (-17.2667, -70.6167, "Peru", "Copper"),
    "Cuajone Copper Mine": (-17.0333, -70.7167, "Peru", "Copper"),
    
    # USA
    "Bingham Canyon Copper Mine": (40.5250, -112.1500, "USA", "Copper"),
    "Morenci Copper Mine": (33.0500, -109.3667, "USA", "Copper"),
    "Bagdad Copper Mine": (34.5833, -113.1833, "USA", "Copper"),
    "Sierrita Copper Mine": (31.8167, -111.0500, "USA", "Copper"),
    "Ray Copper Mine": (33.1833, -110.9833, "USA", "Copper"),
    "Miami Copper Mine": (33.3833, -110.8667, "USA", "Copper"),
    "Safford Copper Mine": (32.8167, -109.7167, "USA", "Copper"),
    
    # INDONESIA
    "Grasberg Copper Mine": (-4.0500, 137.1167, "Indonesia", "Copper"),
    "Batu Hijau Copper Mine": (-8.9833, 116.8833, "Indonesia", "Copper"),
    
    # AUSTRALIA
    "Olympic Dam Copper Mine": (-30.4333, 136.8833, "Australia", "Copper"),
    "Mount Isa Copper Mine": (-20.7333, 139.4833, "Australia", "Copper"),
    "Ernest Henry Copper Mine": (-20.4500, 140.7167, "Australia", "Copper"),
    "Cadia-Ridgeway Copper Mine": (-33.4500, 148.9667, "Australia", "Copper"),
    "Prominent Hill Copper Mine": (-29.7167, 135.5333, "Australia", "Copper"),
    
    # ZAMBIA
    "Kansanshi Copper Mine": (-12.0833, 26.4333, "Zambia", "Copper"),
    "Lumwana Copper Mine": (-12.3167, 25.8167, "Zambia", "Copper"),
    "Konkola Copper Mine": (-12.4000, 27.8833, "Zambia", "Copper"),
    "Mopani Copper Mine": (-12.8000, 28.2000, "Zambia", "Copper"),
    
    # DEMOCRATIC REPUBLIC OF CONGO
    "Tenke Fungurume Copper Mine": (-10.6000, 26.1000, "DR Congo", "Copper"),
    "Kamoa-Kakula Copper Mine": (-10.7667, 25.8000, "DR Congo", "Copper"),
    "Mutanda Copper Mine": (-10.9333, 27.5667, "DR Congo", "Copper"),
    "Kamoto Copper Mine": (-10.7167, 26.4000, "DR Congo", "Copper"),
    
    # MONGOLIA
    "Oyu Tolgoi Copper Mine": (43.0000, 106.8500, "Mongolia", "Copper"),
    "Erdenet Copper Mine": (49.0333, 104.0667, "Mongolia", "Copper"),
    
    # RUSSIA
    "Norilsk Copper District": (69.3500, 88.2000, "Russia", "Copper"),
    "Udokan Copper Deposit": (56.5333, 118.2500, "Russia", "Copper"),
    
    # KAZAKHSTAN
    "Kounrad Copper Mine": (47.6333, 74.9833, "Kazakhstan", "Copper"),
    
    # MEXICO
    "Buenavista Copper Mine": (30.3167, -109.7333, "Mexico", "Copper"),
    "La Caridad Copper Mine": (30.1167, -109.4833, "Mexico", "Copper"),
    
    # POLAND
    "Lubin Copper Mine": (51.4000, 16.2000, "Poland", "Copper"),
    "Rudna Copper Mine": (51.5167, 16.2667, "Poland", "Copper"),
    
    # CANADA
    "Highland Valley Copper Mine": (50.4833, -121.0333, "Canada", "Copper"),
    "Mount Polley Copper Mine": (52.5500, -121.6167, "Canada", "Copper"),
    
    # PANAMA
    "Cobre Panama Mine": (8.6500, -80.6167, "Panama", "Copper"),
    
    # IRAN
    "Sarcheshmeh Copper Mine": (29.5500, 55.7667, "Iran", "Copper"),
    
    # SPAIN
    "Las Cruces Copper Mine": (37.5500, -6.2333, "Spain", "Copper"),
    
    # PHILIPPINES
    "Tampakan Copper Deposit": (6.3833, 125.0667, "Philippines", "Copper"),
    
    # TURKEY
    "Çayeli Copper Mine": (41.0833, 40.7333, "Turkey", "Copper"),
}


def get_mines_by_type(mineral_type):
    """
    Filter mines by mineral type
    
    Args:
        mineral_type: One of 'Iron Ore', 'Bauxite/Aluminum', 'Copper'
    
    Returns:
        Dictionary of mines matching the type
    """
    return {name: coords for name, coords in LEGAL_MINING_AREAS.items() 
            if coords[3] == mineral_type}


def get_mine_count():
    """
    Return count of mines by type
    
    Returns:
        Dictionary with counts: {'Iron Ore': 57, 'Bauxite/Aluminum': 37, 'Copper': 55}
    """
    counts = {}
    for mine_data in LEGAL_MINING_AREAS.values():
        mine_type = mine_data[3]
        counts[mine_type] = counts.get(mine_type, 0) + 1
    return counts


def get_mines_by_country(country):
    """
    Filter mines by country
    
    Args:
        country: Country name (e.g., 'Australia', 'Chile', 'India')
    
    Returns:
        Dictionary of mines in that country
    """
    return {name: coords for name, coords in LEGAL_MINING_AREAS.items() 
            if coords[2] == country}


def get_all_countries():
    """
    Get list of all countries with mines
    
    Returns:
        Sorted list of country names
    """
    countries = set(coords[2] for coords in LEGAL_MINING_AREAS.values())
    return sorted(countries)


def get_total_count():
    """
    Get total number of mines in database
    
    Returns:
        Integer count of all mines
    """
    return len(LEGAL_MINING_AREAS)


if __name__ == "__main__":
    # Print statistics when run directly
    print("=" * 60)
    print("LEGAL MINING AREAS DATABASE")
    print("=" * 60)
    
    counts = get_mine_count()
    print("\n📊 Mines by Type:")
    for mine_type, count in counts.items():
        print(f"   {mine_type}: {count} mines")
    
    print(f"\n🌍 Total Mines: {get_total_count()}")
    print(f"🗺️  Countries: {len(get_all_countries())}")
    
    print("\n🌎 Countries with mines:")
    for country in get_all_countries():
        country_mines = get_mines_by_country(country)
        print(f"   {country}: {len(country_mines)} mine(s)")
    
    print("\n" + "=" * 60)