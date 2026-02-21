import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- CONFIGURATION & STATE MANAGEMENT ---
st.set_page_config(page_title="MinichikoNovel - Writer Portal", page_icon="📕", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'home'
if 'show_create_form' not in st.session_state:
    st.session_state['show_create_form'] = False

# --- เชื่อมต่อ SUPABASE DATABASE ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        return None

supabase = init_connection()

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

# --- DATA GENERATOR (ANALYTICS ZERO STATE) ---
@st.cache_data
def get_empty_analytics_data():
    dates = pd.date_range(end=datetime.today(), periods=30)
    df_traffic = pd.DataFrame({"Date": dates, "Views": [0]*30, "Unique Visitors": [0]*30})
    df_demo = pd.DataFrame({"Country": ["รอข้อมูล"], "Percentage": [100]})
    z_data = [[0]*24 for _ in range(7)]
    return df_traffic, df_demo, z_data

# --- PAGE VIEWS ---
def home_page_view():
    st.title("📕 MinichikoNovel Platform")
    st.markdown("---")
    st.info("ℹ️ โหมดนักอ่าน: ขณะนี้ยังไม่มีนิยายเผยแพร่")

def login_page_view():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 เข้าสู่ระบบ")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In", type="primary", use_container_width=True):
                if username and password:
                    login_user(username)
                else:
                    st.error("กรุณากรอก Username และ Password")

# ==========================================
# 1. หน้าพื้นที่นักเขียน (WRITER WORKSPACE)
# ==========================================
def writer_workspace_view():
    st.title(f"✒️ พื้นที่นักเขียน (Workspace)")
    st.caption(f"ผู้ใช้งาน: {st.session_state['username']}")
    st.divider()

    if supabase is None:
        st.error("🚨 ไม่สามารถเชื่อมต่อฐานข้อมูลได้ กรุณาตั้งค่า Secrets ใน Streamlit Cloud")
        return

    if st.button("➕ เพิ่มงานเขียนใหม่", type="primary"):
        st.session_state['show_create_form'] = not st.session_state['show_create_form']

    if st.session_state['show_create_form']:
        with st.container(border=True):
            st.markdown("### ✨ สร้างนิยายเรื่องใหม่")
            novel_title = st.text_input("ชื่อเรื่อง", placeholder="เช่น เมื่อรัชทายาทสวมหน้ากาก...")
            
            c_form1, c_form2 = st.columns(2)
            with c_form1:
                pen_name_input = st.text_input("นามปากกา (ถ้าปล่อยว่างจะใช้ Username)", placeholder="เช่น Minichiko หรือ Meilifang")
                category = st.selectbox("หมวดหมู่", ["นิยายวาย (BL)", "นิยายจีนโบราณ", "โรมานซ์", "แฟนตาซี"])
            with c_form2:
                cover_image = st.file_uploader("🖼️ หน้าปก (จำลอง)", type=['png', 'jpg'])
            
            if st.button("💾 บันทึกเรื่องใหม่ลง Database", type="primary"):
                if novel_title:
                    try:
                        final_pen_name = pen_name_input.strip() if pen_name_input.strip() != "" else st.session_state['username']
                        
                        supabase.table("novels").insert({
                            "title": novel_title,
                            "pen_name": final_pen_name,
                            "category": category,
                            "status": "ฉบับร่าง"
                        }).execute()
                        
                        st.success(f"บันทึก '{novel_title}' โดย {final_pen_name} สำเร็จ!")
                        st.session_state['show_create_form'] = False
                        time.sleep(1.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"🚨 ข้อผิดพลาดจากฐานข้อมูล: {e}")
                else:
                    st.error("กรุณาตั้งชื่อเรื่อง")

    st.markdown("### 📚 งานเขียนของฉัน")
    
    try:
        response = supabase.table("novels").select("*").order("created_at", desc=True).execute()
        db_novels = response.data

        if not db_novels:
            st.info("คุณยังไม่มีผลงานในระบบ กดปุ่ม 'เพิ่มงานเขียนใหม่' เลย!")
        else:
            for novel in db_novels:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                    c1.subheader(f"📕 {novel.get('title', 'ไม่มีชื่อเรื่อง')}")
                    c1.caption(f"นามปากกา: {novel.get('pen_name', 'ไม่ระบุ')} | หมวด: {novel.get('category', '')} | สถานะ: {novel.get('status', '')}")
                    c2.write(f"👁‍🗨 {novel.get('views', 0)} วิว")
                    c2.write(f"💬 {novel.get('comments', 0)} คอมเมนต์")
                    
                    if c3.button("✏️ จัดการตอน", key=f"edit_{novel['id']}", type="secondary", use_container_width=True):
                        go_to('manage_chapters', novel['title'])
                    if c3.button("📊 ดูสถิติ", key=f"stat_{novel['id']}", use_container_width=True):
                        go_to('analytics')
                    
                    # ปุ่มลบนิยายออกจากฐานข้อมูล
                    if c4.button("🗑️ ลบเรื่องนี้", key=f"del_{novel['id']}", use_container_width=True):
                        try:
                            # สั่งลบข้อมูลจากตาราง novels โดยอิงจาก id
                            supabase.table("novels").delete().eq("id", novel['id']).execute()
                            st.success(f"ลบนิยายเรื่อง {novel.get('title')} ออกจากระบบแล้ว")
                            time.sleep(1)
                            st.rerun()
                        except Exception as e:
                            st.error(f"🚨 ไม่สามารถลบได้: {e}")

    except Exception as e:
        st.error(f"🚨 ไม่สามารถดึงข้อมูลได้: {e}")

# ==========================================
# 2. หน้าจัดการตอน (CHAPTER MANAGEMENT)
# ==========================================
def manage_chapters_view():
    novel_name = st.session_state.get('editing_novel_name', 'นิยาย')
    
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1:
        st.title(f"📖 จัดการตอน: {novel_name}")
    with col_h2:
        if st.button("◀ กลับพื้นที่นักเขียน", use_container_width=True): 
            go_to('workspace')
            
    st.divider()
    
    if supabase is None:
        st.error("🚨 ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
        return

    col_list, col_editor = st.columns([1, 2])
    
    # --- ฝั่งซ้าย: แสดงรายการตอนทั้งหมด ---
    with col_list:
        st.subheader("📑 รายการตอนทั้งหมด")
        try:
            res = supabase.table("chapters").select("*").eq("novel_title", novel_name).order("created_at", desc=False).execute()
            db_chapters = res.data

            if not db_chapters:
                with st.container(border=True):
                    st.info("ยังไม่มีเนื้อหาในเรื่องนี้ เริ่มเขียนตอนแรกเลย!")
            else:
                for i, ch in enumerate(db_chapters):
                    with st.container(border=True):
                        st.markdown(f"**ตอนที่ {i+1}:** {ch.get('chapter_name', 'ไม่มีชื่อตอน')}  \n`สถานะ: {ch.get('status', '')} | 👁‍🗨 {ch.get('views', 0)} วิว`")
                        
                        # ปุ่มลบแต่ละตอน
                        if st.button("🗑️ ลบตอน", key=f"del_ch_{ch['id']}", help="ลบตอนนี้ทิ้ง"):
                            try:
                                supabase.table("chapters").delete().eq("id", ch['id']).execute()
                                st.success("ลบตอนสำเร็จ")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"ลบไม่ได้: {e}")
                                
        except Exception as e:
            st.error(f"🚨 ดึงข้อมูลตอนล้มเหลว: {e}")
            st.info("ตรวจสอบว่าสร้างตาราง 'chapters' และปิด RLS ใน Supabase แล้วหรือยัง")

    # --- ฝั่งขวา: ฟอร์มเพิ่มตอนใหม่ ---
    with col_editor:
        st.subheader("➕ เพิ่มตอนใหม่")
        with st.container(border=True):
            chapter_name = st.text_input("ชื่อตอน", placeholder="เช่น ตอนที่ 1: จุดเริ่มต้น...")
            st.markdown("เนื้อหาตอน (พิมพ์หรือวางเนื้อหาที่นี่)")
            chapter_content = st.text_area("เนื้อหาตอน", height=350, label_visibility="collapsed")
            st.caption(f"จำนวนคำคร่าวๆ: {len(chapter_content.split())} คำ")
            
            st.markdown("### 🕒 ตั้งค่าการเผยแพร่")
            publish_mode = st.radio("เลือกรูปแบบ", ["🚀 เผยแพร่ทันที", "💾 บันทึกเป็นฉบับร่าง"], horizontal=True)
            status_val = "เผยแพร่แล้ว" if publish_mode == "🚀 เผยแพร่ทันที" else "ฉบับร่าง"
                
            if st.button("✅ บันทึกตอนใหม่", type="primary", use_container_width=True):
                if chapter_name and chapter_content:
                    try:
                        supabase.table("chapters").insert({
                            "novel_title": novel_name,
                            "chapter_name": chapter_name,
                            "content": chapter_content,
                            "status": status_val
                        }).execute()
                        
                        st.success(f"บันทึกตอน '{chapter_name}' สำเร็จ!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"🚨 บันทึกไม่สำเร็จ: {e}")
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