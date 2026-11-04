import streamlit as st
from PIL import Image
import os
import json

# --- 頁面基本設定 ---
st.set_page_config(page_title="AI 專屬雲端數位衣櫃", page_icon="👗", layout="wide")

# 初始化 Session State (本地資料暫存)
if "wardrobe" not in st.session_state:
    st.session_state.wardrobe = []

if "profile" not in st.session_state:
    # 預設載入你剛才提供的身材黃金數據
    st.session_state.profile = {
        "bust": 90,
        "underbust": 75,
        "cup": "75C",
        "waist": 82,
        "hips": 103,
        "thigh": 65,
        "shoulder": 46,
        "leg_length": 82,
        "arm_length": 47,
        "arm_circumference": 30,
        "body_shape": "結構型微沙漏梨形 (Structured Curvy Pear)"
    }

# --- 側邊欄：個人身型檔案 ---
with st.sidebar:
    st.header("👤 專屬數位替身檔案")
    st.success(f"身型定位：{st.session_state.profile['body_shape']}")
    
    st.markdown("### 實測身體維度")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**胸圍：** {st.session_state.profile['bust']} cm ({st.session_state.profile['cup']})")
        st.write(f"**腰圍：** {st.session_state.profile['waist']} cm")
        st.write(f"**臀圍：** {st.session_state.profile['hips']} cm")
        st.write(f"**大腿圍：** {st.session_state.profile['thigh']} cm")
    with col2:
        st.write(f"**肩寬：** {st.session_state.profile['shoulder']} cm")
        st.write(f"**腿長：** {st.session_state.profile['leg_length']} cm")
        st.write(f"**臂長：** {st.session_state.profile['arm_length']} cm")
        st.write(f"**臂圍：** {st.session_state.profile['arm_circumference']} cm")
        
    st.divider()
    avatar_file = st.file_uploader("更新你的基準全身照 (Image 1)", type=["jpg", "png", "jpeg"])
    if avatar_file:
        img = Image.open(avatar_file)
        st.image(img, caption="當前虛擬模特基準", use_container_width=True)

# --- 主頁面 Tab 導航 ---
tab1, tab2, tab3 = st.tabs(["👗 衣櫃管理與上傳", "✨ 穿搭試衣間", "🤖 試穿 Prompt 生成器"])

# ----------------- TAB 1: 上傳與管理衣物 -----------------
with tab1:
    st.subheader("📤 上傳新單品到雲端衣櫃")
    
    col_upload, col_meta = st.columns([1, 1])
    
    with col_upload:
        uploaded_garment = st.file_uploader("上傳衣物照片 (Image 2)", type=["jpg", "png", "jpeg"], key="garment_uploader")
        if uploaded_garment:
            g_img = Image.open(uploaded_garment)
            st.image(g_img, caption="預覽單品", width=250)
            
    with col_meta:
        item_name = st.text_input("單品名稱", placeholder="例如：天藍色輕透防曬襯衫")
        category = st.selectbox("品類分類", ["上裝 (Tops)", "下裝 (Bottoms)", "外套 (Outerwear)", "連身 (One-Piece)", "鞋履 (Shoes)", "配件 (Accessories)"])
        color = st.text_input("主色調", placeholder="例如：淺水洗藍 / 純白 / 燕麥色")
        style_vibe = st.multiselect("風格標籤", ["韓系簡約 (Clean fit)", "日系文藝", "通勤智性", "休閒寬鬆", "甜酷風格", "復古老錢風"])
        notes = st.text_area("備註細節 / 材質", placeholder="例如：微透光雪紡、天絲、落肩版型")
        
        if st.button("➕ 儲存到雲端衣櫃", use_container_width=True):
            if uploaded_garment and item_name:
                item_data = {
                    "id": len(st.session_state.wardrobe) + 1,
                    "name": item_name,
                    "category": category,
                    "color": color,
                    "style": style_vibe,
                    "notes": notes,
                    "image": g_img
                }
                st.session_state.wardrobe.append(item_data)
                st.success(f"已成功收錄：{item_name}！")
            else:
                st.error("請至少上傳照片並填寫單品名稱！")
                
    st.divider()
    st.subheader("🗄️ 我的衣櫃清單")
    
    if len(st.session_state.wardrobe) == 0:
        st.info("衣櫃目前是空的，快從上方上傳第一件衣服吧！")
    else:
        # 分類展示
        cats = ["上裝 (Tops)", "下裝 (Bottoms)", "外套 (Outerwear)", "連身 (One-Piece)", "鞋履 (Shoes)"]
        for cat in cats:
            items_in_cat = [i for i in st.session_state.wardrobe if i["category"] == cat]
            if items_in_cat:
                st.markdown(f"#### 📌 {cat}")
                cols = st.columns(4)
                for idx, itm in enumerate(items_in_cat):
                    with cols[idx % 4]:
                        st.image(itm["image"], caption=itm["name"], use_container_width=True)
                        st.caption(f"顏色：{itm['color']} | 標籤：{', '.join(itm['style'])}")

# ----------------- TAB 2: 穿搭試衣間 -----------------
with tab2:
    st.subheader("💡 今日穿搭挑選")
    
    tops = [i for i in st.session_state.wardrobe if i["category"] == "上裝 (Tops)"]
    bottoms = [i for i in st.session_state.wardrobe if i["category"] == "下裝 (Bottoms)"]
    outers = [i for i in st.session_state.wardrobe if i["category"] == "外套 (Outerwear)"]
    
    col_t, col_b, col_o = st.columns(3)
    
    with col_t:
        st.markdown("##### 選擇上衣")
        top_selected = st.selectbox("上裝庫", ["無"] + [t["name"] for t in tops])
    with col_b:
        st.markdown("##### 選擇下裝")
        bot_selected = st.selectbox("下裝庫", ["無"] + [b["name"] for b in bottoms])
    with col_o:
        st.markdown("##### 選擇外套")
        out_selected = st.selectbox("外套庫", ["無"] + [o["name"] for o in outers])
        
    st.divider()
    st.markdown("### 搭配細節調校 (Styling Details)")
    scol1, scol2, scol3 = st.columns(3)
    with scol1:
        tuck_style = st.selectbox("衣角穿法", [
            "French Tuck (法式半塞 - 最修飾腰腹與假胯)",
            "Full Tuck (高腰全塞 - 最大化長腿比例)",
            "Untucked (自然垂墜 - 隨性慵懶放鬆)"
        ])
    with scol2:
        sleeve_style = st.selectbox("袖口處理", [
            "Rolled up to elbows (捲至手肘 - 露出纖細小臂顯俐落)",
            "Normal (自然放鬆長袖)"
        ])
    with scol3:
        occasion = st.selectbox("穿搭場景", ["日常咖啡廳/休閒", "辦公室智性通勤", "週末戶外約會", "極簡高級看展"])

# ----------------- TAB 3: 專屬 Prompt 生成 -----------------
with tab3:
    st.subheader("🎨 生成 Imagen 3 / 虛擬試穿專用 Prompt")
    st.write("這段 Prompt 已經融入了你的**精確身材數據**與**單品版型結構**，直接複製貼入 AI 即可出圖：")
    
    # 動態拼接 Prompt
    base_user_prompt = (
        "Full-body high-end commercial fashion lookbook photograph of the East Asian woman from Image 1, "
        "faithfully capturing her exact facial identity, glasses, soft straight hair with bangs, and natural skin tone. "
        f"Authentic body proportions strictly matching the reference profile: structured 46cm shoulders, a 75C bust, "
        f"an 82cm waist, fuller 103cm hips, 65cm thighs, and an 82cm inseam leg length, standing in a natural relaxed posture. "
    )
    
    garment_desc = f"The subject is wearing {top_selected if top_selected != '無' else 'a tailored top'} "
    if out_selected != "無":
        garment_desc += f"layered with {out_selected}, "
    garment_desc += f"paired with {bot_selected if bot_selected != '無' else 'high-waisted tailored bottoms'}. "
    
    styling_desc = (
        f"Styled with a {tuck_style.split(' ')[0]}, with sleeves {sleeve_style.split(' ')[0]}. "
        "The garments drape naturally over her real curves with realistic fabric creasing and authentic seam tension. "
        f"Setting is a minimalist modern dressing room suited for a {occasion} aesthetic, with soft diffused daylight studio lighting. "
        "85mm portrait lens, f/4 aperture, photorealistic 8k catalog composition."
    )
    
    final_prompt = base_user_prompt + garment_desc + styling_desc
    
    st.text_area("📋 專屬 Virtual Try-On Prompt (English)", value=final_prompt, height=180)
    st.info("💡 複製上方這段 Prompt，搭配你的基準全身照與衣服照片，即可在任何繪圖/試穿工具（如 Imagen 3、Midjourney、IDM-VTON）生成完美貼合身型的試穿圖！")
