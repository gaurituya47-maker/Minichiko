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
            novel_title = st.text_input("ชื่อเรื่อง")
            c_form1, c_form2 = st.columns(2)
            with c_form1:
                pen_name = st.text_input("นามปากกา")
                category = st.selectbox("หมวดหมู่", ["นิยายวาย (BL)", "นิยายจีนโบราณ", "โรมานซ์", "แฟนตาซี"])
            with c_form2:
                cover_image = st.file_uploader("🖼️ หน้าปก (จำลอง)", type=['png', 'jpg'])
            
            if st.button("💾 บันทึกเรื่องใหม่ลง Database", type="primary"):
                if novel_title:
                    try:
                        # ลองส่งข้อมูลเข้าตาราง 'novels' ใน Supabase
                        data, count = supabase.table("novels").insert({
                            "title": novel_title,
                            "pen_name": pen_name if pen_name else st.session_state['username'],
                            "category": category,
                            "status": "ฉบับร่าง"
                        }).execute()
                        
                        st.success(f"บันทึก '{novel_title}' ลงฐานข้อมูลสำเร็จ!")
                        st.session_state['show_create_form'] = False
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        # ถ้าพัง ให้คายข้อความ Error จริงๆ ออกมาหน้าเว็บเลย
                        st.error(f"🚨 ข้อผิดพลาดจากฐานข้อมูล: {e}")
                        st.info("💡 คำแนะนำ: ตรวจสอบว่าใน Supabase ได้ปิด RLS (Disable RLS) แล้ว และชื่อคอลัมน์สะกดตรงกันเป๊ะๆ ตัวพิมพ์เล็กทั้งหมดครับ")
                else:
                    st.error("กรุณาตั้งชื่อเรื่อง")

    st.markdown("### 📚 งานเขียนของฉัน (ดึงจาก Database)")
    
    try:
        # ดึงข้อมูลนิยายทั้งหมดจาก Supabase
        response = supabase.table("novels").select("*").order("created_at", desc=True).execute()
        db_novels = response.data

        if not db_novels:
            st.info("คุณยังไม่มีผลงานในระบบ กดปุ่ม 'เพิ่มงานเขียนใหม่' เลย!")
        else:
            for novel in db_novels:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.subheader(f"📕 {novel['title']}")
                    c1.caption(f"นามปากกา: {novel['pen_name']} | หมวด: {novel['category']} | สถานะ: {novel['status']}")
                    # ใช้ .get() เพื่อป้องกันกรณีที่คอลัมน์ยังไม่ถูกสร้างสมบูรณ์
                    c2.write(f"👁‍🗨 {novel.get('views', 0)} วิว")
                    c2.write(f"💬 {novel.get('comments', 0)} คอมเมนต์")
                    
                    if c3.button("✏️ จัดการตอน", key=f"edit_{novel['id']}", type="secondary", use_container_width=True):
                        go_to('manage_chapters', novel['title'])
                    if c3.button("📊 ดูสถิติ", key=f"stat_{novel['id']}", use_container_width=True):
                        go_to('analytics')
    except Exception as e:
        st.error(f"🚨 ไม่สามารถดึงข้อมูลได้: {e}")

# ==========================================
# 2. หน้าจัดการตอน (CHAPTER MANAGEMENT)
# ==========================================
def manage_chapters_view():
    novel_name = st.session_state.get('editing_novel_name', 'นิยาย')
    st.title(f"📖 จัดการตอน: {novel_name}")
    if st.button("◀ กลับ", use_container_width=False): go_to('workspace')
    st.info("ระบบจัดการตอนกำลังเชื่อมต่อกับตาราง chapters (Coming Soon)")

# ==========================================
# 3. หน้าแดชบอร์ดสถิติ (ANALYTICS)
# ==========================================
def analytics_dashboard_view():
    st.title("📊 สถิติผู้เข้าชมเชิงลึก")
    if st.button("◀ กลับ", use_container_width=False): go_to('workspace')
    st.info("โหมดพร้อมใช้งาน: รอการดึงข้อมูลสถิติจากฐานข้อมูลจริง")

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📕 MinichikoNovel")
    if st.session_state['logged_in']:
        if st.button("✒️ พื้นที่นักเขียน"): go_to('workspace')
        if st.button("📊 สถิติ"): go_to('analytics')
        st.divider()
        if st.button("🚪 ออกจากระบบ"): logout_user()
    else:
        if st.button("🏠 หน้าแรก"): go_to('home')
        if st.button("🔐 เข้าสู่ระบบ"): go_to('login')

# --- MAIN CONTROLLER ---
if st.session_state['current_view'] == 'login': login_page_view()
elif st.session_state['current_view'] == 'workspace' and st.session_state['logged_in']: writer_workspace_view()
elif st.session_state['current_view'] == 'manage_chapters' and st.session_state['logged_in']: manage_chapters_view()
elif st.session_state['current_view'] == 'analytics' and st.session_state['logged_in']: analytics_dashboard_view()
elif st.session_state['current_view'] == 'home': home_page_view()
else: go_to('workspace' if st.session_state['logged_in'] else 'home')