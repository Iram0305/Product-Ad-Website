import streamlit as st
import json
import os
import base64

# ==================== CONFIG ====================
st.set_page_config(page_title="Product Ads Board", layout="centered")

FILE_NAME = "ads.json"

# ==================== FUNCTIONS ====================
def load_ads():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_ads(ads_list):
    with open(FILE_NAME, "w") as f:
        json.dump(ads_list, f)

# Load ads at startup
ads = load_ads()

# ==================== SIDEBAR - POST NEW AD ====================
st.sidebar.header("📢 Post a New Ad")

with st.sidebar.form("post_ad_form", clear_on_submit=True):
    title = st.text_input("Ad Title *", placeholder="iPhone 13 Pro - Like New")
    seller = st.text_input("Your Name (optional)", placeholder="John Doe")
    category = st.selectbox("Category *", [
        "Electronics", "Fashion & Beauty", "Home & Garden", 
        "Vehicles", "Books", "Sports", "Other"
    ])
    description = st.text_area("Description *", placeholder="Write details about your product...")
    price = st.number_input("Price ($)", min_value=0.0, step=0.01, format="%.2f")
    contact = st.text_input("Contact (email/phone) *", placeholder="example@gmail.com or +1 234 567 890")
    image = st.file_uploader("Product Image (optional)", type=["png", "jpg", "jpeg"])

    submitted = st.form_submit_button("🚀 Post Ad")

    if submitted:
        if not title.strip() or not description.strip() or not contact.strip():
            st.error("Title, description, and contact are required!")
        else:
            new_ad = {
                "title": title.strip(),
                "seller": seller.strip() or "Anonymous",
                "category": category,
                "description": description.strip(),
                "price": float(price) if price > 0 else None,
                "contact": contact.strip(),
            }

            if image is not None:
                new_ad["image_base64"] = base64.b64encode(image.getvalue()).decode("utf-8")

            ads.append(new_ad)
            save_ads(ads)
            st.success("Ad posted successfully!")
            st.rerun()

# ==================== MAIN PAGE ====================
st.title("🛍️ Product Ads Board")
st.caption("A simple classifieds-style site for buying and selling products")

# Filters
col1, col2 = st.columns([2, 2])
with col1:
    selected_category = st.selectbox("Filter by Category", ["All"] + ["Electronics", "Fashion & Beauty", "Home & Garden", "Vehicles", "Books", "Sports", "Other"])
with col2:
    search_term = st.text_input("🔍 Search in title/description", "")

# Apply filters
filtered_ads = ads

if selected_category != "All":
    filtered_ads = [ad for ad in filtered_ads if ad["category"] == selected_category]

if search_term:
    search_lower = search_term.lower()
    filtered_ads = [
        ad for ad in filtered_ads
        if search_lower in ad["title"].lower() or search_lower in ad["description"].lower()
    ]

# Display ads
if not filtered_ads:
    st.info("No ads found. Be the first to post one using the sidebar! ➡️")
else:
    st.write(f"**Showing {len(filtered_ads)} ad(s)**")
    for ad in reversed(filtered_ads):  # Newest first
        with st.container():
            st.markdown("---")
            cols = st.columns([1.8, 4])
            
            with cols[0]:
                if "image_base64" in ad:
                    img_bytes = base64.b64decode(ad["image_base64"])
                    st.image(img_bytes, use_column_width=True)
                else:
                    st.write("📷 No image")
            
            with cols[1]:
                st.subheader(ad["title"])
                st.caption(f"📂 {ad['category']}  •  👤 {ad['seller']}")
                
                st.write(ad["description"])
                
                price_text = f"${ad['price']:.2f}" if ad['price'] is not None else "Contact for price"
                st.markdown(f"**Price:** {price_text}")
                
                st.markdown(f"**Contact:** `{ad['contact']}`")
                
                # Optional: copy contact to clipboard
                if st.button("📋 Copy contact", key=f"copy_{id(ad)}"):
                    st.code(ad["contact"])
                    st.toast("Contact copied!")

st.markdown("---")
st.caption("💡 Data is saved to `ads.json` (persistent when running locally). On Streamlit Community Cloud, data resets when the app sleeps — for production use Google Sheets, Supabase, or Firebase.")
