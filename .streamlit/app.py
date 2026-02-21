import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta

# --- CONFIGURATION & STATE MANAGEMENT ---
st.set_page_config(page_title="MinichikoNovel - Writer Portal", page_icon="📕", layout="wide")

# สร้างตัวแปร State เพื่อเก็บข้อมูลชั่วคราว
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'home'
if 'show_create_form' not in st.session_state:
    st.session_state['show_create_form'] = False
if 'editing_novel_name' not in st.session_state:
    st.session_state['editing_novel_name'] = ""
if 'my_novels' not in st.session_state:
    st.session_state['my_novels'] = []

# --- ROUTING FUNCTIONS ---
def go_to(view, novel_name=""):
    st.session_state['current_view'] = view
    if novel_name:
        st.session_state['editing_novel_name'] = novel_name
    st.rerun()

def login_user(username):
    st.session_state['logged_in'] = True
    st.session_state['username'] = username
    st.success("เข้าสู่ระบบสำเร็จ!")
    time.sleep(1)
    go_to('workspace')

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['show_create_form'] = False
    st.session_state['editing_novel_name'] = ""
    go_to('home')

# --- DATA GENERATOR (แบบไม่มี Mock Data / โครงสร้างรอรับฐานข้อมูลจริง) ---
@st.cache_data
def get_empty_analytics_data():
    # สร้าง Dataframe ที่มีค่าเป็น 0 ทั้งหมดสำหรับ 30 วันย้อนหลัง
    dates = pd.date_range(end=datetime.today(), periods=30)
    df_traffic = pd.DataFrame({"Date": dates, "Views": [0]*30, "Unique Visitors": [0]*30})
    
    # ฐานข้อมูลผู้อ่าน (รอข้อมูลจริง)
    df_demo = pd.DataFrame({"Country": ["รอการเชื่อมต่อข้อมูล"], "Percentage": [100]})
    
    # Heatmap แบบว่างเปล่า (ค่า 0 ทั้งหมด)
    z_data = [[0]*24 for _ in range(7)]
    
    return df_traffic, df_demo, z_data

# --- PAGE VIEWS (ระบบหน้าจอต่างๆ) ---

def home_page_view():
    st.title("📕 MinichikoNovel Platform")
    st.markdown("---")
    st.info("ℹ️ ขณะนี้ยังไม่มีข้อมูลนิยายในระบบ (รอการเชื่อมต่อฐานข้อมูล)")

def login_page_view():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 เข้าสู่ระบบ")
        st.markdown("MinichikoNovel Writer & Admin Portal")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", type="primary", use_container_width=True)
            
            if submit:
                if username and password:
                    login_user(username)
                else:
                    st.error("กรุณากรอก Username และ Password ให้ครบถ้วน")

# ==========================================
# 1. หน้าพื้นที่นักเขียน (WRITER WORKSPACE)
# ==========================================
def writer_workspace_view():
    st.title(f"✒️ พื้นที่นักเขียน (Workspace)")
    st.caption(f"ยินดีต้อนรับคุณ: {st.session_state['username']}")
    st.divider()

    if st.button("➕ เพิ่มงานเขียนใหม่", type="primary"):
        st.session_state['show_create_form'] = not st.session_state['show_create_form']

    if st.session_state['show_create_form']:
        with st.container(border=True):
            st.markdown("### ✨ สร้างนิยายเรื่องใหม่")
            novel_title = st.text_input("ชื่อเรื่อง", placeholder="ใส่ชื่อนิยายของคุณที่นี่...")
            c_form1, c_form2 = st.columns(2)
            with c_form1:
                pen_name = st.text_input("นามปากกา")
                category = st.selectbox("หมวดหมู่", ["นิยายวาย (BL)", "นิยายจีนโบราณ", "โรมานซ์", "แฟนตาซี"])
                novel_desc = st.text_area("คำโปรย (Synopsis)", height=150)
            with c_form2:
                cover_image = st.file_uploader("🖼️ อัปโหลดไฟล์รูปภาพหน้าปก", type=['png', 'jpg', 'jpeg'])
            
            if st.button("💾 บันทึกและสร้างเรื่อง", type="primary"):
                if novel_title:
                    st.session_state['my_novels'].append({
                        "title": novel_title,
                        "pen_name": pen_name if pen_name else st.session_state['username'],
                        "category": category,
                        "status": "ฉบับร่าง",
                        "views": 0,
                        "comments": 0
                    })
                    st.success(f"สร้างโปรเจกต์ '{novel_title}' สำเร็จ!")
                    st.session_state['show_create_form'] = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("กรุณาตั้งชื่อเรื่องก่อนบันทึก")

    st.markdown("### 📚 งานเขียนของฉัน")
    if len(st.session_state['my_novels']) == 0:
        st.info("คุณยังไม่มีผลงานในระบบ กดปุ่ม 'เพิ่มงานเขียนใหม่' เพื่อเริ่มต้นเรื่องแรกเลย!")
    else:
        for idx, novel in enumerate(st.session_state['my_novels']):
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.subheader(f"📕 {novel['title']}")
                c1.caption(f"นามปากกา: {novel['pen_name']} | หมวด: {novel['category']} | สถานะ: {novel['status']}")
                c2.write(f"👁‍🗨 {novel['views']} วิว")
                c2.write(f"💬 {novel['comments']} คอมเมนต์")
                
                if c3.button("✏️ จัดการตอน", key=f"edit_{idx}", type="secondary", use_container_width=True):
                    go_to('manage_chapters', novel['title'])
                if c3.button("📊 ดูสถิติ", key=f"stat_{idx}", use_container_width=True):
                    go_to('analytics')

# ==========================================
# 2. หน้าจัดการตอน (CHAPTER MANAGEMENT)
# ==========================================
def manage_chapters_view():
    novel_name = st.session_state.get('editing_novel_name', 'นิยายของฉัน')
    
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1:
        st.title(f"📖 จัดการตอน: {novel_name}")
    with col_h2:
        if st.button("◀ กลับไปพื้นที่นักเขียน", use_container_width=True):
            go_to('workspace')
            
    st.divider()
    
    col_list, col_editor = st.columns([1, 2])
    with col_list:
        st.subheader("📑 รายการตอนทั้งหมด")
        with st.container(border=True):
            st.info("ยังไม่มีเนื้อหาในเรื่องนี้")

    with col_editor:
        st.subheader("➕ เพิ่มตอนใหม่")
        with st.container(border=True):
            chapter_name = st.text_input("ชื่อตอน")
            st.markdown("เนื้อหาตอน (พิมพ์หรือวางเนื้อหาที่นี่)")
            chapter_content = st.text_area("เนื้อหาตอน", height=350, label_visibility="collapsed")
            st.caption(f"จำนวนคำคร่าวๆ: {len(chapter_content.split())} คำ")
            
            st.markdown("### 🕒 ตั้งค่าการเผยแพร่")
            publish_mode = st.radio("เลือกรูปแบบการเผยแพร่", ["🚀 เผยแพร่ทันที", "⏰ ตั้งเวลาล่วงหน้า", "💾 บันทึกฉบับร่าง"], horizontal=True)
            
            if publish_mode == "⏰ ตั้งเวลาล่วงหน้า":
                c_date, c_time = st.columns(2)
                with c_date:
                    sched_date = st.date_input("วันที่", value=datetime.today() + timedelta(days=1))
                with c_time:
                    sched_time = st.time_input("เวลา", value=datetime.strptime("18:00", "%H:%M").time())
                st.info(f"จะอัปเดตอัตโนมัติในวันที่ {sched_date.strftime('%d/%m/%Y')} เวลา {sched_time.strftime('%H:%M')} น.")
                
            if st.button("✅ บันทึกและตั้งค่า", type="primary", use_container_width=True):
                if chapter_name and chapter_content:
                    st.success(f"บันทึกตอน '{chapter_name}' เรียบร้อยแล้ว!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("กรุณาใส่ชื่อตอนและเนื้อหาก่อนบันทึก")

# ==========================================
# 3. หน้าแดชบอร์ดสถิติ (ANALYTICS - ZERO STATE)
# ==========================================
def analytics_dashboard_view():
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1:
        st.title("📊 สถิติผู้เข้าชมเชิงลึก")
    with col_h2:
        if st.button("◀ กลับไปพื้นที่นักเขียน", use_container_width=True):
            go_to('workspace')
            
    st.info("ℹ️ โหมดพร้อมใช้งาน: รอการเชื่อมต่อข้อมูลสถิติจากฐานข้อมูลจริง")
    
    df_traffic, df_demo, z_data = get_empty_analytics_data()
    
    st.markdown("### 📈 ภาพรวม 30 วันย้อนหลัง")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👁️ ยอดวิวรวม", "0", "")
    m2.metric("👤 ผู้เข้าชมแบบไม่ซ้ำ", "0", "")
    m3.metric("⏱️ เวลาอ่านเฉลี่ย", "0m 0s", "")
    m4.metric("🔄 อัตราการกลับมาอ่านซ้ำ", "0.0%", "")
    
    st.divider()

    st.markdown("### 🚀 แนวโน้มการเข้าชมรายวัน")
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=df_traffic['Date'], y=df_traffic['Views'], mode='lines', name='ยอดวิว', line=dict(color='#E63946', width=2)))
    fig_trend.add_trace(go.Scatter(x=df_traffic['Date'], y=df_traffic['Unique Visitors'], mode='lines', name='ผู้เข้าชม', line=dict(color='#1D3557', width=2)))
    fig_trend.update_layout(template="plotly_white", hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0))
    # กำหนดแกน Y ให้เริ่มที่ 0 เสมอแม้ไม่มีข้อมูล
    fig_trend.update_yaxes(range=[0, 100])
    st.plotly_chart(fig_trend, use_container_width=True)

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("### 🌍 สัดส่วนนักอ่านตามพื้นที่")
        fig_pie = px.pie(df_demo, values='Percentage', names='Country', hole=0.4, color_discrete_sequence=['#D3D3D3'])
        fig_pie.update_traces(textposition='inside', textinfo='label')
        fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_chart2:
        st.markdown("### 🕒 ช่วงเวลาที่คนอ่านมากที่สุด")
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = [f"{i:02d}:00" for i in range(24)]
        fig_heat = px.imshow(z_data, x=hours, y=days, color_continuous_scale="Greys", aspect="auto")
        fig_heat.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_heat, use_container_width=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📕 MinichikoNovel")
    
    if st.session_state['logged_in']:
        st.success(f"👤 ผู้ใช้: {st.session_state['username']}")
        st.divider()
        if st.button("✒️ พื้นที่นักเขียน", use_container_width=True):
             go_to('workspace')
        if st.button("📊 สถิติแบบละเอียด", use_container_width=True):
             go_to('analytics')
        st.divider()
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            logout_user()
    else:
        st.info("สถานะ: บุคคลทั่วไป")
        if st.button("🏠 หน้าแรก (Home)", use_container_width=True):
             go_to('home')
        if st.button("🔐 เข้าสู่ระบบ (Login)", type="primary", use_container_width=True):
             go_to('login')

# --- MAIN CONTROLLER ---
if st.session_state['current_view'] == 'login':
    login_page_view()
elif st.session_state['current_view'] == 'workspace' and st.session_state['logged_in']:
    writer_workspace_view()
elif st.session_state['current_view'] == 'manage_chapters' and st.session_state['logged_in']:
    manage_chapters_view()
elif st.session_state['current_view'] == 'analytics' and st.session_state['logged_in']:
    analytics_dashboard_view()
elif st.session_state['current_view'] == 'home':
    home_page_view()
else:
    if st.session_state['logged_in']:
        go_to('workspace')
    else:
        go_to('home')