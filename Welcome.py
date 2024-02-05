import folium
import streamlit as st
import json
import pandas as pd
import numpy as np
import pydeck as pdk
import base64

css = """
<style>
/* Targeting the main content area for the green background */
.main .block-container, .stApp {
    background-color: #f9f0df;
}
/* Sidebar */
.st-emotion-cache-16txtl3.eczjsme4 {
    background-color: #f9f0df;
}

.st-emotion-cache-6qob1r.eczjsme3 {
    background-color: #f9f0df;
}

.st-emotion-cache-ue6h4q.e1y5xkzn3 {
    color:#34571a
} 

.st-emotion-cache-18ni7ap.ezrtsby2 {
    background-color: #f9f0df;
}

h1 {
    color: #34571a;
    font-family: "Source Sans Pro", sans-serif;
}
div.stText {
    color: #34571a;
    font-size: 24px;
}
h3 {
    color: #34571a;
    font-family: "Source Sans Pro", sans-serif;
    
}
div.stText {
    color: #34571a;
    font-size: 10px;
}

/* Style for "Your profile" */
.profile-title {
    font-family: "Source Sans Pro", sans-serif;
    font-weight: 700;
    color: #34571a;
    font-size: 24px;
}
/* Style pour la carte PyDeck */
.stDeckGlJsonChart {
    border: 2px solid black;
    border-radius: 5px;
}
.st-emotion-cache-1788y8l.e1f1d6gn2 {
    border: 2px solid black !important;
    border-radius: 5px;  # pour des coins arrondis
    padding: 10px;      # espace entre le texte et le bord
}
.st-emotion-cache-1wivap2.e1i5pmia3  {
    text-align: center; /* Centrer horizontalement le texte */
    display: flex;
    flex-direction: column;
    justify-content: center; /* Centrer verticalement le contenu */
}
.st-emotion-cache-16idsys p {
    word-break: break-word;
    margin-bottom: 0px;
    font-size: 18px;
    font-weight: 550;
}    
.st-emotion-cache-5rimss.e1nzilvr5 {
    color: black;
}
    
</style>
"""

st.markdown(css, unsafe_allow_html=True)
# Chemin du fichier CSV corrigé
CSV_FILE_PATH = r"/Users/ratchoul/Desktop/PLEASE CODE ESSAI V9.csv"

# Utilisation de @st.cache_resource pour charger les données GeoJSON
@st.cache_resource
def load_geojson(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def load_and_process_data():
    data = pd.read_csv(CSV_FILE_PATH, delimiter=';', decimal=',')
    data['Mean Score'] = data[['Productivity', 'Tolerance', 'Water requirement']].mean(axis=1)
    return data

def get_top_cereals_by_region_soil_and_type(data, region, soil_type, organic_status, top_n=3):
    filtered_data = data[(data['Regions of France'] == region) &
                         (data['Type of soil'] == soil_type) &
                         (data['Organic or not'] == organic_status)]
    top_cereals = filtered_data.sort_values(by='Mean Score', ascending=False).head(top_n)
    return top_cereals

def display_metrics(cereal):
    col1, col2, col3 = st.columns(3)
    precocity_comment = "Precoce" if cereal['Precocity'] >= 3 else "Late"
    precocity_color = "green" if cereal['Precocity'] >= 3 else "red"
    col1.metric("Precocity", cereal['Precocity'])
    col1.markdown(f"<span style='color: {precocity_color};'>{precocity_comment}</span>", unsafe_allow_html=True)

    cold_resistance_comment = "Resistant to cold" if cereal['Cold resistance'] >= 3 else "Not resistant to cold"
    cold_resistance_color = "green" if cereal['Cold resistance'] >= 3 else "red"
    col2.metric("Cold resistance", cereal['Cold resistance'])
    col2.markdown(f"<span style='color: {cold_resistance_color};'>{cold_resistance_comment}</span>", unsafe_allow_html=True)

    water_requirement_comment = "Requires little water" if cereal['Water requirement'] < 5 else "Requires lots of water"
    water_requirement_color = "green" if cereal['Water requirement'] < 5 else "red"
    col3.metric("Water requirement", cereal['Water requirement'])
    col3.markdown(f"<span style='color: {water_requirement_color};'>{water_requirement_comment}</span>", unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    price_comment = "Cheap grain" if cereal['Price per ton'] < 950 else "Expensive grain"
    price_color = "green" if cereal['Price per ton'] < 950 else "red"
    col4.metric("Purchase price", f"{cereal['Price per ton']}€/t")
    col4.markdown(f"<span style='color: {price_color};'>{price_comment}</span>", unsafe_allow_html=True)

    weight_comment = "Light grain" if cereal['Weight'] < 5 else "Heavy grain"
    weight_color = "green" if cereal['Weight'] < 5 else "red"
    col5.metric("Weight", cereal['Weight'])
    col5.markdown(f"<span style='color: {weight_color};'>{weight_comment}</span>", unsafe_allow_html=True)

    protein_content_comment = "High quality grain" if cereal['Protein share'] >= 75 else "Poor quality grain"
    protein_content_color = "green" if cereal['Protein share'] >= 75 else "red"
    col6.metric("Protein share", cereal['Protein share'])
    col6.markdown(f"<span style='color: {protein_content_color};'>{protein_content_comment}</span>", unsafe_allow_html=True)

def display_podium(top_cereals):
    # Add custom styles for the podium and space above
    podium_style = """
    <style>
    .podium-intro {
        font-size: 20px; /* Set the font size for the introduction */
        font-family: 'Source Sans Pro', sans-serif;
        color: #34571a;
        margin-bottom: 1.5em; /* Equivalent to three lines space */
        margin-top: 1.5em; /* Space from the map above */
        text-align: center;
    }
    .podium-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 0;  /* No space between the steps */
        margin-top: 1.5em; /* Space between text and podium */
        margin-bottom: 1.5em; /* Space between podium and metrics */
    }
    .podium-place {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border-radius: 10px;  /* Rounded corners */
        padding: 10px;
        color: black;
        font-weight: bold;
        overflow: hidden;  /* Prevents text from overflowing */
        text-overflow: ellipsis;  /* Adds an ellipsis if the text overflows */
        white-space: nowrap;  /* Prevents text from wrapping to the next line */
    }
    .first-place {
        width: 120px;  /* Maintain the width for first place */
        height: 150px;
        background: gold;
    }
    .second-place {
        width: 100px;  /* Maintain the width for second place */
        height: 100px;
        background: silver;
    }
    .third-place {
        width: 80px;  /* Maintain the width for third place */
        height: 75px;
        background: #cd7f32;
    }
    .placement-label {
        font-size: 14px;  /* Adjusted font size for placement label */
        font-weight: normal;  /* Less emphasis on the label */
    }
    </style>
    """
    st.markdown(podium_style, unsafe_allow_html=True)

    # Introduction sentence for the podium
    st.markdown('<div class="podium-intro">The 3 best wheat varieties for your farm are:</div>', unsafe_allow_html=True)

    # Check if we have at least 3 top cereals to display the podium
    if len(top_cereals) >= 3:
        podium_html = f"""
        <div class='podium-container'>
            <div class='podium-place second-place'>
                <div class='placement-label'>2nd</div>
                {top_cereals.iloc[1]['Wheat variety']}
            </div>
            <div class='podium-place first-place'>
                <div class='placement-label'>1st</div>
                {top_cereals.iloc[0]['Wheat variety']}
            </div>
            <div class='podium-place third-place'>
                <div class='placement-label'>3rd</div>
                {top_cereals.iloc[2]['Wheat variety']}
            </div>
        </div>
        """
        st.markdown(podium_html, unsafe_allow_html=True)
        # Add space after the podium
        st.markdown('<div style="margin-top: 1.5em;"></div>', unsafe_allow_html=True)
    elif len(top_cereals) > 0:
        st.write("Not enough varieties for a full podium")

def display_wheat_requirement(farm_size, price_per_ton):
    required_wheat = round(0.150 * farm_size)
    harvested_wheat = round(7 * farm_size)
    total_price = price_per_ton * required_wheat
    formatted_price = f"{total_price:,.0f}"
    formatted_harvest = f"{harvested_wheat:,.0f}"


    # Custom CSS for the wheat requirement text
    wheat_requirement_css = """
    <style>
    .wheat-requirement-text {
        font-family: 'Source Sans Pro', sans-serif; /* Assuming this is the font for your headings */
        color: #34571a; /* Same color as your headings */
        font-size: 18px; /* A bit larger size than your current text, adjust as needed */
        margin-bottom: 1em; /* Add some space below each sentence */
    }
    </style>
    """
    # Include the custom CSS in the app
    st.markdown(wheat_requirement_css, unsafe_allow_html=True)

    # Display the wheat requirement information using markdown for HTML styling
    st.write("")
    st.write("")
    st.markdown(f"<div class='wheat-requirement-text'>For a farming size of {farm_size} hectares, you will need to sow {required_wheat}t of common wheat.</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='wheat-requirement-text'>If conditions are all perfect, you will harvest {formatted_harvest}t of common wheat.</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='wheat-requirement-text'>You will pay €{formatted_price} for the seeds.</div>", unsafe_allow_html=True)
    st.write("")
    st.write("")
        
def main():

    # Include custom CSS to position the image
    st.markdown("""
    <style>
    .top-right {
        position: fixed; /* Fixed position */
        top: 68px;
        right: 20px;
        z-index: 999; /* Ensure it's above other content */
    }
    </style>
    """, unsafe_allow_html=True)

    # Convert image to base64
    def get_image_base64(path):
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return encoded_string
    
    # Path to your image - this should be the path where the image is stored
    image_path ="/Users/ratchoul/Desktop/w5.png"
    image_base64 = get_image_base64(image_path)

    # Use the image base64 string in the markdown to display the image
    st.markdown(f'<div class="top-right"><img src="data:image/png;base64,{image_base64}" width="100"></div>', unsafe_allow_html=True)    
    st.title("Map of France")
    st.subheader("Let's see which variety of common wheat is the best match for your farm!")
  # Définir le style CSS pour le cadre
    st.markdown("""
        <style>
        .map-container {
            border: 2px solid black;
            border-radius: 5px;
            overflow: hidden;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Chargement des données
    cereal_data = load_and_process_data()
    
    # Barre latérale pour les critères de sélection
    with st.sidebar:
        st.sidebar.markdown('<p class="profile-title">Your profile</p>', unsafe_allow_html=True)
        regions = cereal_data['Regions of France'].unique()
        selected_region = st.selectbox("Region", regions)

        soil_types = cereal_data['Type of soil'].unique()
        selected_soil_type = st.selectbox("Soil type", soil_types)

        organic_options = cereal_data['Organic or not'].unique()
        selected_organic_status = st.selectbox("Farming type", organic_options)

        farm_size = st.number_input('Farm size (in hectares)', min_value=0, max_value=100000, step=1)

        variety_choice = st.radio("Choose variety to display metrics", ("1st Variety", "2nd Variety", "3rd Variety"))

    # Régions de France avec les chemins des fichiers GeoJSON
    regions = {
        "Auvergne": "/Users/ratchoul/Desktop/App FIEP/entrypoint/region-auvergne-rhone-alpes.geojson",
        "Burgundy": "/Users/ratchoul/Desktop/App FIEP/entrypoint/region-bourgogne-franche-comte.geojson",
        "Brittany": "/Users/ratchoul/Desktop/App FIEP/entrypoint/region-bretagne.geojson",
        "Centre Val de Loire": "/Users/ratchoul/Desktop/App FIEP/entrypoint/region-centre-val-de-loire.geojson",
        "Corsica": "/Users/ratchoul/Desktop/App FIEP/entrypoint/region-corse.geojson",
        "Grand Est": "/Users/ratchoul/Desktop/App FIEP/entrypoint/region-grand-est.geojson",
        "Hauts de France": "/Users/ratchoul/Desktop/App FIEP/entrypoint/region-hauts-de-france.geojson",
        "Île de France": "/Users/ratchoul/Desktop/App FIEP/entrypoint/region-ile-de-france.geojson",
        "Normandy": "/Users/ratchoul/Desktop/App FIEP/entrypoint/region-normandie.geojson",
        "Nouvelle-Aquitaine": "/Users/ratchoul/Desktop/App FIEP/entrypoint/region-nouvelle-aquitaine.geojson",
        "Occitanie": "/Users/ratchoul/Desktop/App FIEP/entrypoint/region-occitanie.geojson",
        "Pays de la Loire": "/Users/ratchoul/Desktop/App FIEP/entrypoint/region-pays-de-la-loire.geojson",
        "Provence-Alpes-Côte d'Azur": "/Users/ratchoul/Desktop/App FIEP/entrypoint/region-provence-alpes-cote-d-azur.geojson"
    }

    # Création d'une carte centrée sur la France
    m = folium.Map(location=[46.603354, 1.888334], zoom_start=6)

    # Coloration de la région sélectionnée en utilisant la fonction mise en cache
    if selected_region in regions:
        region_geojson = load_geojson(regions[selected_region])
        folium.GeoJson(region_geojson, name=selected_region, style_function=lambda x: {'fillColor': 'purple'}).add_to(m)
    
    # Création du HTML pour la carte Folium et Injection du HTML avec un cadre CSS
    map_html = m._repr_html_()
    html_with_frame = f"""
    <div style="border: 2px solid black; border-radius: 5px; width: 900px; height: 540px;">
        {map_html}
    </div>
    """
    st.components.v1.html(html_with_frame, width=1000, height=580) 
     # Créer un espace pour la carte PyDeck
    pydeck_container = st.empty()

   # Affichage du podium et des métriques
    if selected_region and selected_soil_type and selected_organic_status:
        top_cereals = get_top_cereals_by_region_soil_and_type(cereal_data, selected_region, selected_soil_type, selected_organic_status)
        display_podium(top_cereals)

        if not top_cereals.empty:
            variety_index = {"1st Variety": 0, "2nd Variety": 1, "3rd Variety": 2}.get(variety_choice, 0)
            if len(top_cereals) > variety_index:
                selected_cereal = top_cereals.iloc[variety_index]
                display_metrics(selected_cereal)
                price_per_ton = selected_cereal['Price per ton']
                display_wheat_requirement(farm_size, price_per_ton)

    
    # Dictionnaire des villes par région
    villes_par_region = {
        "Auvergne": {
            "Clermont-Ferrand": (45.7772, 3.0870),
            "Saint-Etienne": (45.4397, 4.3872),
            "Lyon": (45.7640, 4.8357),
            "Annecy": (45.8992, 6.1294),
            "Grenoble": (45.1885, 5.7245),
            "Valence": (44.9333, 4.8924),
            "Brioude": (45.2892, 3.3873)
        },
        "Burgundy": {
            "Besançon": (47.2378, 6.0245),
            "Clamecy": (47.4606, 3.5183),
            "Le Creusot": (46.8063, 4.4360),
            "Poligny": (46.8333, 5.7000),
        },
        "Brittany": {
            "Rennes": (48.1173, -1.6778),
            "Loudéac": (48.1784, -2.7536),
            "Carhaix-Plouguer": (48.2735, -3.5731),
            "Ploërmel": (47.9311, -2.3963)
        },
       "Centre Val de Loire": {
            "Tours": (47.3941, 0.6848),
            "Châteauroux": (46.8091, 1.6915),
            "Bourges": (47.0833, 2.3983),
            "Blois": (47.5926, 1.3349),
            "Orléans": (47.9039, 1.9090),
            "Châteaudun": (48.0704, 1.3383)
        },
        
        "Grand Est": {
            "Metz": (49.1197, 6.1761),
            "Sarrebourg": (48.7411, 7.0578),
            "Guebwiller": (47.9167, 7.2167),
            "Charmes": (48.3572, 6.3089),
            "Saint-Dizier": (48.6367, 4.9497),
            "Châlons-en-Champagne": (48.9562, 4.3634),
            "Vouzier": (48.1506, 4.1658),
            "Bar-le-Duc": (48.7726, 5.1622)
        },
        "Hauts de France": {
            "Amiens": (49.8951, 2.3022),
            "Hesdin": (50.3719, 2.0370),
            "Longuenesse": (50.7240, 2.2841),
            "Arras": (50.2922, 2.7805),
            "Caudry": (50.1242, 3.4140),
            "Saint-Quentin": (49.8486, 3.2886),
            "Compiègne": (49.4175, 2.8262),
            "Doullens": (50.1626, 2.3291)
        },
        "Île de France": {
            "Fontainebleau": (48.4047, 2.7016),
            "Provins": (48.5612, 3.2999)
        },
        "Normandy": {
                       "Mathonville": (49.6741, 1.3066),
            "Rouen": (49.4432, 1.0999),
            "Morgny": (49.6300, 1.5720),
            "Louviers": (49.2156, 1.1697),
            "Evreux": (49.0248, 1.1505),
            "Bernay": (49.0841, 0.5993),
            "Argentan": (48.7443, -0.0234),
            "Vire": (48.8375, -0.8885),
            "Saint-Lô": (49.1161, -1.0900),
            "Falaise": (48.8934, -0.1986)
        },
        "Nouvelle-Aquitaine": {
            "Limoges": (45.8333, 1.2611),
            "Poitiers": (46.5802, 0.3404),
            "Ruffec": (46.0281, 0.2040),
            "Saint-Jean-d'Angély": (45.9463, -0.5143),
            "Angoulême": (45.6486, 0.1562),
            "Bordeaux": (44.8378, -0.5792),
            "Orthez": (43.4882, -0.7694),
            "Marmande": (44.5042, 0.1623),
            "Périgueux": (45.1847, 0.7214),
            "Tulle": (45.2679, 1.7717),
            "Guéret": (46.1682, 1.8717),
            "Bressuire": (46.8416, -0.4892)
        },
        "Occitanie": {
            "Auch": (43.6460, 0.5860),
            "Toulouse": (43.6045, 1.4442),
            "Montanban": (43.8857, 1.1804),
            "Cahors": (44.4479, 1.4407),
            "Figeac": (44.6083, 2.0357),
            "Rodez": (44.3494, 2.5725),
            "Mende": (44.5181, 3.4990),
        },
        "Provence-Alpes-Côte d'Azur": {
            "Gap": (44.5594, 6.0790),
            "Manosque": (43.8281, 5.7821)
        },
            "Pays de la Loire": {
            "Le Mans": (48.0061, 0.1996),
            "Mayenne": (48.3041, -0.7139),
            "Angers": (47.4784, -0.5632),
            "Ancenis": (47.3707, -1.1766),
            "Blain": (47.3606, -1.7068),
            "Montaigu": (46.9867, -1.3077),
            "La Flèche": (47.6985, -0.0758),  
            "Sablé-sur-Sarthe": (47.8397, -0.3342) 
        }

}

    # Générer et afficher la carte PyDeck avec des barres en 3D
    if selected_region in villes_par_region:
        villes = villes_par_region[selected_region]
        echelle_dispersion = 0.4
        nombre_points_par_ville = 60
        df_list = []

        for ville, (lat, lon) in villes.items():
            df_ville = pd.DataFrame(
                np.random.randn(nombre_points_par_ville, 2) * echelle_dispersion + [lat, lon],
                columns=['lat', 'lon'])
            df_list.append(df_ville)

        df = pd.concat(df_list)

        # Assigner aléatoirement une couleur à chaque point
        couleurs = [(255, 255, 0, 130), (128, 128, 128), (178, 34, 34)]  # Jaune, Gris foncé, Rouge clair avec transparence
        df['couleur'] = [couleurs[np.random.randint(0, 3)] for _ in range(len(df))]

        # Générer des hauteurs aléatoires pour les barres en 3D
        df['hauteur'] = np.random.randint(100, 1000, size=len(df))

       # Créer une vue PyDeck avec inclinaison et orientation
        vue = pdk.ViewState(
            latitude=46.603354,
            longitude=1.888334,
            zoom=5,  # Zoom sur la France
            pitch=45,  # Inclinaison de 45 degrés
            bearing=0  # Orientation à 0 degrés (vers le nord)
        )

        couche = pdk.Layer(
            'ColumnLayer',  # Utilisation de ColumnLayer pour des barres en 3D
            data=df,
            get_position='[lon, lat]',
            get_elevation='hauteur',
            elevation_scale=50,  # Ajustement de l'échelle de hauteur
            radius=1500,  # Rayon à la base des barres
            get_fill_color='couleur',  # Couleur des barres
            pickable=True,
            auto_highlight=True,
        )

        # Afficher la carte avec PyDeck avec un style de carte coloré
        st.pydeck_chart(pdk.Deck(
            layers=[couche],
            initial_view_state=vue,
            map_style='mapbox://styles/mapbox/light-v10'  # Utiliser un style de carte coloré
        ))
    
        
if __name__ == "__main__":
    main()
