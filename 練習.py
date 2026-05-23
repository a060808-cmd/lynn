import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

# ── 步驟 1：頁面配置與標題 ──────────────────────────────────
st.set_page_config(page_title="共享單車站點地圖儀表板", layout="wide")

st.title("🚲 共享單車站點分佈儀表板")
st.caption("資料來源：parking_lots.csv（共享單車歷史與型態站點資料）")


# ── 步驟 2：載入與整理資料 ──────────────────────────────────
@st.cache_data
def load_data():

    # data 資料夾中的 csv
    csv_path = "./parking_lots.csv"

    # 讀取資料
    df = pd.read_csv(csv_path)

    # 資料型態整理
    df["parking_lot_id"] = df["parking_lot_id"].astype(str)

    df["min_rent_start_date"] = pd.to_datetime(
        df["min_rent_start_date"]
    )

    df["max_rent_start_date"] = pd.to_datetime(
        df["max_rent_start_date"]
    )

    return df


# 載入資料
df = load_data()


# ── 步驟 3：側邊欄動態篩選器 ────────────────────────────────
st.sidebar.header("🔍 站點資料篩選")

# 縣市篩選
all_cities = sorted(df["parking_lot_city"].dropna().unique())

selected_cities = st.sidebar.multiselect(
    "選擇縣市",
    options=all_cities,
    default=all_cities,
)

# 營運型態篩選
all_biz_types = sorted(
    df["parking_lot_biz_type_desc"].dropna().unique()
)

selected_biz_types = st.sidebar.multiselect(
    "選擇營運 / 商圈型態",
    options=all_biz_types,
    default=all_biz_types,
)

# 套用篩選
filtered_df = df[
    (df["parking_lot_city"].isin(selected_cities))
    &
    (df["parking_lot_biz_type_desc"].isin(selected_biz_types))
]


# ── 步驟 4：KPI 指標 ───────────────────────────────────────
m1, m2, m3 = st.columns(3)

with m1:
    st.metric(
        "當前篩選站點數",
        f"{len(filtered_df):,} 站"
    )

with m2:
    st.metric(
        "涵蓋縣市數",
        f"{filtered_df['parking_lot_city'].nunique()} 個縣市"
    )

with m3:
    st.metric(
        "營運型態類別",
        f"{filtered_df['parking_lot_biz_type_desc'].nunique()} 種"
    )

st.markdown("---")


# ── 步驟 5：地圖顏色控制 ──────────────────────────────────
color_by = st.radio(
    "🎨 地圖站點顏色依據：",
    [
        "縣市（parking_lot_city）",
        "營運型態（parking_lot_biz_type_desc）",
    ],
    horizontal=True,
)

color_col = (
    "parking_lot_city"
    if "縣市" in color_by
    else "parking_lot_biz_type_desc"
)


# ── 步驟 6：主版面 ────────────────────────────────────────
col1, col2 = st.columns([1, 2])


# 左側：表格
with col1:

    st.subheader("📋 站點詳細資訊")

    view_df = filtered_df[
        [
            "parking_lot_id",
            "parking_lot_name",
            "parking_lot_city",
            "parking_lot_area",
            "parking_lot_biz_type_desc",
        ]
    ].sort_values(
        ["parking_lot_city", "parking_lot_area"]
    )

    st.dataframe(
        view_df,
        use_container_width=True,
        hide_index=True,
        height=550,
    )


# 右側：地圖
with col2:

    st.subheader("🗺️ 站點空間地理分佈")

    if not filtered_df.empty:

        # 地圖中心點
        center_lat = filtered_df[
            "parking_lot_latitude"
        ].mean()

        center_lon = filtered_df[
            "parking_lot_longitude"
        ].mean()

        # 縮放大小
        zoom_level = 11 if len(selected_cities) == 1 else 7.5

        # 畫地圖
        fig = px.scatter_mapbox(
            filtered_df,

            lat="parking_lot_latitude",
            lon="parking_lot_longitude",

            color=color_col,

            hover_name="parking_lot_name",

            hover_data={
                "parking_lot_id": True,
                "parking_lot_city": True,
                "parking_lot_area": True,
                "parking_lot_biz_type_desc": True,
                "min_rent_start_date": True,
                "parking_lot_latitude": False,
                "parking_lot_longitude": False,
            },

            mapbox_style="open-street-map",

            zoom=zoom_level,

            center={
                "lat": center_lat,
                "lon": center_lon,
            },

            height=550,

            title="共享單車站點分佈圖",
        )

        # 邊距優化
        fig.update_layout(
            margin={
                "r": 0,
                "t": 40,
                "l": 0,
                "b": 0,
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.warning(
            "⚠️ 當前篩選條件下沒有資料，請調整左側篩選器。"
        )