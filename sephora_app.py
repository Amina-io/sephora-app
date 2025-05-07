import streamlit as st
import pandas as pd
import joblib
import os
from PIL import Image
import numpy as np

# Helper function for file paths
def get_file_path(relative_path):
    """Get absolute file path relative to the script location"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)

# Set page title and layout
st.set_page_config(page_title="Skincare Product Recommendation System", layout="wide")

# Load your data and model
try:
    skincare_df = pd.read_csv(get_file_path('skincare_df.csv'), low_memory=False)
    model = joblib.load(get_file_path('sephora_model_1.pkl'))
except Exception as e:
    st.error(f"Error loading data or model: {e}")
    st.stop()

# Define background color and general styling
def set_styling():
    st.markdown(
        """
        <style>
        /* Main background */
        .stApp {
            background-color: #fce4ec;
        }
        
        /* General text color - for headings and paragraphs */
        p, h1, h2, h3, h4, h5, h6 {
            color: #333333 !important;
        }
        
        /* Specifically target label text for the questions */
        .stSelectbox label {
            color: #333333 !important;
        }
        
        /* Dropdown styling - background dark */
        .stSelectbox div[data-baseweb="select"] {
            background-color: #333333 !important;
        }
        
        /* Dropdown text - white */
        .stSelectbox div[data-baseweb="select"] span {
            color: white !important;
        }
        
        /* Button styling - specifically targeting text too */
        .stButton button {
            background-color: #333333 !important;
            color: white !important;
            border: none !important;
            padding: 10px 20px !important;
            border-radius: 5px !important;
            width: 100% !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton button:hover {
            background-color: #555555 !important;
            transform: translateY(-2px) !important;
        }
        
        /* Force any text inside the button to be white */
        .stButton button * {
            color: white !important;
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            font-size: 14px !important;
            color: #666666 !important;
        }
        
        /* Divider styling */
        hr {
            margin-top: 20px !important;
            margin-bottom: 20px !important;
            border-color: #f8bbd0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Function to display a skin tone option with image
def display_skin_tone_option(col, tone_name, display_name):
    with col:
        try:
            # Check if image exists and display it
            image_path = get_file_path(f"assets/skin_tones/{tone_name}.jpg")
            if os.path.exists(image_path):
                img = Image.open(image_path)
                st.image(img, width=100, caption=display_name)
            else:
                # Fallback to emoji
                emoji_map = {"porcelain": "⚪️", "fairLight": "⚪️", "light": "⚪️", 
                            "lightMedium": "🟡", "medium": "🟡", "mediumTan": "🟡",
                            "olive": "🟠", "tan": "🟠", "deep": "🟤", "dark": "🟤", 
                            "ebony": "🟤", "rich": "🟤", "notSureST": "❓"}
                st.markdown(f"{emoji_map.get(tone_name, '⚪️')} **{display_name}**")
            
            # Create a clearly named button
            button_label = f"Select {display_name}"
            if st.button(button_label, key=f"select_{tone_name}_btn"):
                st.session_state.skin_tone = tone_name
                # Add this line to make the selection more obvious to the user
                st.success(f"Selected: {display_name}")
                
        except Exception as e:
            # Handle exceptions
            st.warning(f"Could not load image for {display_name}: {e}")
            if st.button(f"Select {display_name}", key=f"fallback_{tone_name}_btn"):
                st.session_state.skin_tone = tone_name

# Apply styling
set_styling()

# Create layout
left_col, center_col = st.columns([1, 2])

# Initialize session state
if 'get_recommendations_clicked' not in st.session_state:
    st.session_state.get_recommendations_clicked = False

# Left panel with questions
with left_col:
    st.markdown("### Your Skincare Profile")
    
    # Improved skin type selection with explanations
    st.markdown("#### Select your skin type")
    
    # Add explanatory information
    with st.expander("Not sure about your skin type?"):
        st.markdown("""
        **Combination**: Mixed skin with oily areas (typically T-zone) and normal or dry areas elsewhere.
        
        **Dry**: Skin that feels tight, may flake, and lacks natural moisture. Often feels rough or itchy.
        
        **Oily**: Skin that produces excess sebum, appears shiny, and may be prone to enlarged pores and acne.
        """)
    
    # Create a more visual selection instead of a simple dropdown
    skin_type_cols = st.columns(3)
    
    # Initialize session state for selections if not exists
    if 'skin_type' not in st.session_state:
        st.session_state.skin_type = "Combination"  # Default
    
    # Visual buttons for skin type selection
    with skin_type_cols[0]:
        combo_btn = st.button("Combination", key="combo_btn", 
                        help="Mixed skin with both oily and dry areas")
        if combo_btn:
            st.session_state.skin_type = "Combination"
            
    with skin_type_cols[1]:
        dry_btn = st.button("Dry", key="dry_btn",
                       help="Skin that feels tight or has flaky patches")
        if dry_btn:
            st.session_state.skin_type = "Dry"
            
    with skin_type_cols[2]:
        oily_btn = st.button("Oily", key="oily_btn",
                        help="Skin that produces excess oil, appears shiny")
        if oily_btn:
            st.session_state.skin_type = "Oily"
    
    # Show the current selection
    st.markdown(f"**Selected skin type:** {st.session_state.skin_type}")
    
    # Set the user_skin_type variable for the model
    user_skin_type = st.session_state.skin_type
    
    # Add separator
    st.markdown("---")
    
    # Improved skin tone selection
    st.markdown("#### Select your skin tone")
    
    # Add explanatory information about skin tone categories
    with st.expander("About skin tone categories"):
        st.markdown("""
        We offer a detailed range of skin tones to provide more personalized recommendations:
        
        **Light Tones**: Porcelain, Fair-Light, Light
        **Medium Tones**: Light-Medium, Medium, Medium-Tan, Olive, Tan
        **Deep Tones**: Deep, Dark, Ebony, Rich
        
        Select the tone that best matches your skin for the most accurate product recommendations.
        """)
    
    # Initialize session state for skin tone
    if 'skin_tone' not in st.session_state:
        st.session_state.skin_tone = "medium"  # Default

    # Create a layout with 3 rows
    row1_cols = st.columns(3)
    row2_cols = st.columns(3)
    row3_cols = st.columns(3)
    row4_cols = st.columns(1)

    # Display skin tone options by row
    # First row - lighter tones
    display_skin_tone_option(row1_cols[0], "porcelain", "Porcelain")
    display_skin_tone_option(row1_cols[1], "fairLight", "Fair-Light")
    display_skin_tone_option(row1_cols[2], "light", "Light")

    # Second row - medium tones
    display_skin_tone_option(row2_cols[0], "lightMedium", "Light-Medium")
    display_skin_tone_option(row2_cols[1], "medium", "Medium")
    display_skin_tone_option(row2_cols[2], "mediumTan", "Medium-Tan")

    # Third row - more medium to deeper tones
    display_skin_tone_option(row3_cols[0], "olive", "Olive")
    display_skin_tone_option(row3_cols[1], "tan", "Tan")
    display_skin_tone_option(row3_cols[2], "deep", "Deep")

    # Fourth row - Not sure option
    display_skin_tone_option(row4_cols[0], "notSureST", "Not Sure")

    # Show current selection
    st.markdown(f"**Selected skin tone:** {st.session_state.skin_tone}")

    # Set the user_skin_tone variable for the model
    user_skin_tone = st.session_state.skin_tone
    
    # Add separator
    st.markdown("---")
    
    # Budget Category selection (keeping the dropdown for now)
    st.markdown("#### Select your budget category")
    user_budget_category = st.selectbox(
        'Choose your budget range', 
        ['Low', 'Medium', 'High']
    )
    
    # Get Recommendations button
    if st.button('Get Recommendations'):
        st.session_state.get_recommendations_clicked = True

# Define the recommendation function
def get_recommendations(user_skin_type, user_skin_tone, user_budget_category):
    # Create a skin tone column name from the selection
    skin_tone_col = f"skin_tone_{user_skin_tone}"
    
    # Initial filtering by skin type and budget
    filtered_data = skincare_df[
        (skincare_df['price_category'] == user_budget_category) &
        (skincare_df['skin_type'] == user_skin_type)
    ].copy()
    
    # If we find no data, return empty result
    if filtered_data.empty:
        return pd.DataFrame({'message': ['No recommendations found for the given criteria.']})

    # Define all possible feature columns
    feature_columns = ['skin_type_combination', 'skin_type_dry', 'skin_type_oily',
                       'price_category_low', 'price_category_medium', 'price_category_high',
                       'skin_tone_dark', 'skin_tone_deep', 'skin_tone_ebony', 'skin_tone_fair',
                       'skin_tone_fairLight', 'skin_tone_light', 'skin_tone_lightMedium',
                       'skin_tone_medium', 'skin_tone_mediumTan', 'skin_tone_notSureST',
                       'skin_tone_olive', 'skin_tone_porcelain', 'skin_tone_rich', 'skin_tone_tan']
    
    # Ensure all needed columns exist
    for col in feature_columns:
        if col not in filtered_data.columns:
            filtered_data[col] = 0
    
    # Set the user's selected skin tone to True in the dataframe
    # First, set all skin tone columns to 0
    for col in [c for c in feature_columns if c.startswith('skin_tone_')]:
        filtered_data[col] = 0
    
    # Then, set the selected skin tone to 1, if it exists in our feature columns
    if skin_tone_col in feature_columns:
        filtered_data[skin_tone_col] = 1
    
    # Get predictions and sort
    filtered_data['predicted_rating'] = model.predict(filtered_data[feature_columns])
    recommendations = filtered_data.sort_values(by='predicted_rating', ascending=False).head(3)
    
    return recommendations[['product_name', 'predicted_rating']]

# Center content
# In the center_col section
with center_col:
    if not st.session_state.get_recommendations_clicked:
        st.image(get_file_path("skinsync.gif"), use_column_width=True)
    else:
        # Recommendation logic
        st.markdown("## Your Top Recommendations")
        
        try:
            recommendations = get_recommendations(user_skin_type, user_skin_tone, user_budget_category)
            
            if 'message' in recommendations.columns:
                st.write(recommendations['message'][0])
            elif recommendations.empty:
                st.warning("No recommendations found for your criteria. Try adjusting your selections.")
            else:
                st.write('Top 3 Recommendations:')
                # Enhanced display of recommendations
                for i, (index, row) in enumerate(recommendations.iterrows()):
                    st.markdown(f"### {i+1}. {row['product_name']}")
                    st.markdown(f"Predicted Rating: {row['predicted_rating']:.2f}/5")
                    st.markdown("---")
        except Exception as e:
            st.error(f"Error generating recommendations: {e}")