import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta

# --- CONFIGURATION & STATE MANAGEMENT ---
st.set_page_config(page_title="MinichikoNovel - Analytics & Workspace", page_icon="📕", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'home'

# --- ROUTING FUNCTIONS ---
def go_to(view):
    st.session_state['current_view'] = view
    st.rerun()

def login_user(username):
    st.session_state['logged_in'] = True
    st.session_state['username'] = username
    st.success("เข้าสู่ระบบสำเร็จ!")
    time.sleep(1)
    go_to('dashboard')

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    go_to('home')

# --- DATA GENERATOR (สำหรับเรนเดอร์กราฟสถิติให้สวยงาม) ---
# ฟังก์ชันนี้จำลอง Dataframe ขึ้นมาเพื่อให้เห็นหน้าตา Dashboard จริงๆ (แทนการใช้ข้อมูลตายตัว)
@st.cache_data
def get_analytics_data():
    dates = pd.date_range(end=datetime.today(), periods=30)
    views = np.random.normal(15000, 2000, 30).astype(int)
    visitors = (views * np.random.uniform(0.6, 0.8, 30)).astype(int)
    df_traffic = pd.DataFrame({"Date": dates, "Views": views, "Unique Visitors": visitors})
    
    # ฐานข้อมูลผู้อ่าน (Demographics)
    countries = ["ไทย", "จีน (China)", "ญี่ปุ่น (Japan)", "เกาหลีใต้ (Korea)", "อื่นๆ (Inter)"]
    readers = [45, 25, 15, 10, 5]
    df_demo = pd.DataFrame({"Country": countries, "Percentage": readers})
    
    return df_traffic, df_demo

# --- PAGE VIEWS ---

def home_page_view():
    st.title("📕 MinichikoNovel Platform")
    st.markdown("---")
    # พื้นที่เตรียมแสดงผลเมื่อเชื่อมต่อฐานข้อมูลจริง
    st.info("ℹ️ ขณะนี้ยังไม่มีข้อมูลนิยายในระบบ (กรุณาเชื่อมต่อ Database เพื่อดึงข้อมูล)")
    
    # Placeholder UI
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.container(height=200, border=True)
        st.write("พื้นที่สำหรับปกนิยาย")

def login_page_view():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 เข้าสู่ระบบ")
        st.markdown("MinichikoNovel Writer & Admin Portal")
        
        with st.form("login_form"):
            # เอาคำใบ้ออกทั้งหมด
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)
            
            if submit:
                # เป็นเพียง Template พื้นฐาน รอการเขียนเชื่อม API/Database ตรวจสอบรหัสผ่านจริง
                if username and password:
                    login_user(username)
                else:
                    st.error("กรุณากรอก Username และ Password ให้ครบถ้วน")

def dashboard_view():
    st.title("📊 สถิติผู้เข้าชมแบบละเอียด (Advanced Analytics)")
    st.caption("อัปเดตข้อมูลล่าสุด: วันนี้")
    
    df_traffic, df_demo = get_analytics_data()
    
    # 1. TOP METRICS (KPIs)
    st.markdown("### 📈 ภาพรวม 30 วันย้อนหลัง")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="👁️ ยอดวิวรวม (Total Views)", value=f"{df_traffic['Views'].sum():,}", delta="12.5%")
    m2.metric(label="👤 ผู้เข้าชมแบบไม่ซ้ำ (Unique Visitors)", value=f"{df_traffic['Unique Visitors'].sum():,}", delta="8.2%")
    m3.metric(label="⏱️ เวลาอ่านเฉลี่ย (Avg. Reading Time)", value="18m 45s", delta="1m 20s")
    m4.metric(label="🔄 อัตราการกลับมาอ่านซ้ำ (Retention)", value="68.4%", delta="-1.2%")
    
    st.divider()

    # 2. TRAFFIC TREND CHART
    st.markdown("### 🚀 แนวโน้มการเข้าชมรายวัน")
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=df_traffic['Date'], y=df_traffic['Views'], mode='lines+markers', name='ยอดวิว (Views)', line=dict(color='#E63946', width=3)))
    fig_trend.add_trace(go.Scatter(x=df_traffic['Date'], y=df_traffic['Unique Visitors'], mode='lines', fill='tozeroy', name='ผู้เข้าชม (Visitors)', line=dict(color='#1D3557', width=2)))
    fig_trend.update_layout(template="plotly_white", hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_trend, use_container_width=True)

    # 3. DEMOGRAPHICS & ENGAGEMENT
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### 🌍 สัดส่วนนักอ่านตามพื้นที่ (Demographics)")
        fig_pie = px.pie(df_demo, values='Percentage', names='Country', hole=0.4, 
                         color_discrete_sequence=['#E63946', '#F4A261', '#E9C46A', '#2A9D8F', '#264653'])
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_chart2:
        st.markdown("### 📱 อุปกรณ์ที่ใช้เข้าอ่าน (Device Usage)")
        # สร้าง Bar chart แนวนอนแบบง่ายๆ
        device_data = pd.DataFrame({
            "Device": ["Mobile (iOS/Android)", "Desktop / Web", "Tablet"],
            "Users": [75, 20, 5]
        })
        fig_bar = px.bar(device_data, x="Users", y="Device", orientation='h', text="Users",
                         color_discrete_sequence=['#1D3557'])
        fig_bar.update_traces(texttemplate='%{text}%', textposition='outside')
        fig_bar.update_layout(xaxis_title="เปอร์เซ็นต์ (%)", yaxis_title="", margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_bar, use_container_width=True)

    # 4. BEST TIME TO PUBLISH (Heatmap)
    st.divider()
    st.markdown("### 🕒 ช่วงเวลาที่มีคนอ่านมากที่สุด (Best Time for Engagement)")
    # สร้างข้อมูลจำลองสำหรับ Heatmap
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    hours = [f"{i:02d}:00" for i in range(24)]
    z_data = np.random.poisson(lam=50, size=(7, 24)) 
    # ทำให้ช่วง 18:00 - 22:00 มีค่าสูงเป็นพิเศษ
    z_data[:, 18:23] += np.random.randint(50, 150, size=(7, 5))
    
    fig_heat = px.imshow(z_data, labels=dict(x="เวลา (Hour)", y="วัน (Day)", color="Engagement"),
                         x=hours, y=days, color_continuous_scale="Reds", aspect="auto")
    fig_heat.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig_heat, use_container_width=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📕 MinichikoNovel")
    
    if st.session_state['logged_in']:
        st.success(f"👤 ผู้ใช้: {st.session_state['username']}")
        if st.button("🏠 หน้าแรก (Home)", use_container_width=True):
             go_to('home')
        if st.button("📊 สถิติแบบละเอียด (Dashboard)", type="primary", use_container_width=True):
             go_to('dashboard')
        st.divider()
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            logout_user()
    else:
        st.info("สถานะ: ยังไม่ได้เข้าสู่ระบบ")
        if st.button("🏠 หน้าแรก (Home)", use_container_width=True):
             go_to('home')
        if st.button("🔐 เข้าสู่ระบบ (Login)", type="primary", use_container_width=True):
             go_to('login')

# --- MAIN CONTROLLER ---
if st.session_state['current_view'] == 'login':
    login_page_view()
elif st.session_state['current_view'] == 'dashboard' and st.session_state['logged_in']:
    dashboard_view()
elif st.session_state['current_view'] == 'home':
    home_page_view()
else:
    # Fallback
    if st.session_state['logged_in']:
        go_to('dashboard')
    else:
        go_to('home')