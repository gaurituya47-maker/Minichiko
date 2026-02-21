import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime, timedelta
from supabase import create_client, Client

# --- CONFIGURATION & STATE MANAGEMENT ---
st.set_page_config(page_title="MinichikoNovel", page_icon="📕", layout="wide")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'home' # home, novel_detail, read_chapter, login, workspace, manage_chapters, analytics
if 'show_create_form' not in st.session_state:
    st.session_state['show_create_form'] = False
if 'editing_novel_name' not in st.session_state:
    st.session_state['editing_novel_name'] = ""
if 'reading_chapter' not in st.session_state:
    st.session_state['reading_chapter'] = None

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
def go_to(view, novel_name="", chapter_data=None):
    st.session_state['current_view'] = view
    if novel_name:
        st.session_state['editing_novel_name'] = novel_name
    if chapter_data is not None:
        st.session_state['reading_chapter'] = chapter_data
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
    st.session_state['reading_chapter'] = None
    go_to('home')

# --- DATA GENERATOR (ANALYTICS ZERO STATE) ---
@st.cache_data
def get_empty_analytics_data():
    dates = pd.date_range(end=datetime.today(), periods=30)
    df_traffic = pd.DataFrame({"Date": dates, "Views": [0]*30, "Unique Visitors": [0]*30})
    df_demo = pd.DataFrame({"Country": ["รอข้อมูล"], "Percentage": [100]})
    z_data = [[0]*24 for _ in range(7)]
    return df_traffic, df_demo, z_data

# ==========================================
# 0. ระบบหน้าบ้านสำหรับนักอ่าน (READER FRONTEND)
# ==========================================

# หน้าแรก: รวมนิยายทั้งหมด
def home_page_view():
    st.title("📕 MinichikoNovel")
    st.markdown("แหล่งรวมนิยายฮิตฮอตที่สุดในตอนนี้")
    st.markdown("---")
    
    if supabase is None:
        st.warning("รอการเชื่อมต่อฐานข้อมูล...")
        return

    try:
        res = supabase.table("novels").select("*").order("created_at", desc=True).execute()
        db_novels = res.data
        
        if not db_novels:
            st.info("ยังไม่มีนิยายในระบบตอนนี้นะคะ รอติดตามผลงานจากนักเขียนได้เลยค่ะ!")
        else:
            cols = st.columns(4)
            for i, novel in enumerate(db_novels):
                with cols[i % 4]:
                    with st.container(border=True):
                        st.markdown(f"### {novel.get('title')}")
                        st.caption(f"✍️ โดย: {novel.get('pen_name')}")
                        st.caption(f"🏷️ หมวด: {novel.get('category')}")
                        if st.button("📖 เข้าสู่นิยาย", key=f"read_home_{novel['id']}", use_container_width=True):
                            go_to('novel_detail', novel['title'])
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดหน้าแรก: {e}")

# หน้าสารบัญ: รายละเอียดนิยายและตอนต่างๆ
def novel_detail_view():
    novel_name = st.session_state['editing_novel_name']
    
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1:
        st.title(f"📕 {novel_name}")
    with col_h2:
        if st.button("◀ กลับหน้าแรก", use_container_width=True): 
            go_to('home')
            
    st.divider()
    st.subheader("📑 สารบัญตอน")
    
    try:
        # ดึงมาเฉพาะตอนที่สถานะเป็น "เผยแพร่แล้ว" (คนอ่านจะไม่เห็นฉบับร่าง)
        res = supabase.table("chapters").select("*").eq("novel_title", novel_name).eq("status", "เผยแพร่แล้ว").order("created_at", desc=False).execute()
        published_chapters = res.data
        
        if not published_chapters:
            st.info("นิยายเรื่องนี้ยังไม่มีตอนที่เผยแพร่ค่ะ รอติดตามนะคะ!")
        else:
            for i, ch in enumerate(published_chapters):
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    c1.markdown(f"**ตอนที่ {i+1}:** {ch.get('chapter_name')}")
                    c1.caption(f"👁‍🗨 {ch.get('views', 0)} วิว")
                    if c2.button("อ่านตอนนี้", key=f"read_ch_{ch['id']}", use_container_width=True):
                        # อัปเดตยอดวิวปลอมๆ (ถ้าจะทำจริงต้องยิง API กลับไปบวก 1)
                        go_to('read_chapter', novel_name, chapter_data=ch)
    except Exception as e:
        st.error(f"โหลดข้อมูลตอนไม่สำเร็จ: {e}")

# หน้าอ่านนิยาย: แสดงเนื้อหา
def read_chapter_view():
    novel_name = st.session_state['editing_novel_name']
    ch_data = st.session_state['reading_chapter']
    
    if st.button("◀ กลับสารบัญ"):
        go_to('novel_detail', novel_name)
        
    st.divider()
    st.title(f"{ch_data.get('chapter_name')}")
    st.caption(f"เรื่อง: {novel_name} | เข้าชม: {ch_data.get('views', 0)}")
    st.markdown("---")
    
    # แสดงเนื้อหานิยายแบบจัดหน้าสวยๆ
    st.write(ch_data.get('content', 'ไม่มีเนื้อหา'))
    
    st.markdown("---")
    if st.button("◀ กลับสารบัญ (จบตอน)"):
        go_to('novel_detail', novel_name)

# ==========================================
# 1. หน้าเข้าสู่ระบบ
# ==========================================
def login_page_view():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 เข้าสู่ระบบนักเขียน")
        st.info("💡 โหมดทดสอบ: พิมพ์ Username กับ Password อะไรก็ได้ เพื่อเข้าสู่ระบบครับ")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In", type="primary", use_container_width=True):
                if username and password:
                    login_user(username)
                else:
                    st.error("กรุณากรอกข้อมูล")

# ==========================================
# 2. หน้าพื้นที่นักเขียน (WRITER WORKSPACE)
# ==========================================
def writer_workspace_view():
    st.title(f"✒️ พื้นที่นักเขียน")
    st.caption(f"ผู้ใช้งาน: {st.session_state['username']}")
    st.divider()

    if supabase is None:
        st.error("🚨 ไม่สามารถเชื่อมต่อฐานข้อมูลได้")
        return

    if st.button("➕ เพิ่มงานเขียนใหม่", type="primary"):
        st.session_state['show_create_form'] = not st.session_state['show_create_form']

    if st.session_state['show_create_form']:
        with st.container(border=True):
            st.markdown("### ✨ สร้างนิยายเรื่องใหม่")
            novel_title = st.text_input("ชื่อเรื่อง")
            c_form1, c_form2 = st.columns(2)
            with c_form1:
                pen_name_input = st.text_input("นามปากกา (เว้นว่างเพื่อใช้ Username)")
                category = st.selectbox("หมวดหมู่", ["นิยายวาย (BL)", "นิยายจีนโบราณ", "โรมานซ์", "แฟนตาซี"])
            with c_form2:
                st.file_uploader("🖼️ หน้าปก (จำลอง)", type=['png', 'jpg'])
            
            if st.button("💾 บันทึกเรื่องใหม่", type="primary"):
                if novel_title:
                    try:
                        final_pen_name = pen_name_input.strip() if pen_name_input.strip() != "" else st.session_state['username']
                        supabase.table("novels").insert({
                            "title": novel_title, "pen_name": final_pen_name, 
                            "category": category, "status": "ฉบับร่าง"
                        }).execute()
                        st.success("บันทึกสำเร็จ!")
                        st.session_state['show_create_form'] = False
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"🚨 ข้อผิดพลาด: {e}")
                else:
                    st.error("กรุณาตั้งชื่อเรื่อง")

    st.markdown("### 📚 งานเขียนของฉัน")
    try:
        res = supabase.table("novels").select("*").order("created_at", desc=True).execute()
        for novel in res.data:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                c1.subheader(f"📕 {novel.get('title')}")
                c1.caption(f"นามปากกา: {novel.get('pen_name')} | สถานะ: {novel.get('status')}")
                c2.write(f"👁‍🗨 {novel.get('views', 0)} วิว")
                if c3.button("✏️ จัดการตอน", key=f"edit_{novel['id']}", use_container_width=True):
                    go_to('manage_chapters', novel['title'])
                if c4.button("🗑️ ลบเรื่อง", key=f"del_{novel['id']}", use_container_width=True):
                    supabase.table("novels").delete().eq("id", novel['id']).execute()
                    st.rerun()
    except Exception as e:
        st.error("ไม่สามารถดึงข้อมูลได้")

# ==========================================
# 3. หน้าจัดการตอน (CHAPTER MANAGEMENT)
# ==========================================
def manage_chapters_view():
    novel_name = st.session_state.get('editing_novel_name', 'นิยาย')
    
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1:
        st.title(f"📖 จัดการตอน: {novel_name}")
    with col_h2:
        if st.button("◀ กลับพื้นที่นักเขียน", use_container_width=True): go_to('workspace')
            
    st.divider()
    col_list, col_editor = st.columns([1, 2])
    
    with col_list:
        st.subheader("📑 รายการตอนทั้งหมด")
        try:
            res = supabase.table("chapters").select("*").eq("novel_title", novel_name).order("created_at", desc=False).execute()
            for i, ch in enumerate(res.data):
                with st.container(border=True):
                    st.markdown(f"**ตอนที่ {i+1}:** {ch.get('chapter_name')} \n`สถานะ: {ch.get('status')}`")
                    if st.button("🗑️ ลบ", key=f"del_ch_{ch['id']}"):
                        supabase.table("chapters").delete().eq("id", ch['id']).execute()
                        st.rerun()
        except:
            st.info("ยังไม่มีตอนในระบบ")

    with col_editor:
        st.subheader("➕ เพิ่มตอนใหม่")
        with st.container(border=True):
            chapter_name = st.text_input("ชื่อตอน")
            chapter_content = st.text_area("เนื้อหาตอน", height=300)
            publish_mode = st.radio("เลือกรูปแบบ", ["🚀 เผยแพร่ทันที", "💾 บันทึกเป็นฉบับร่าง"], horizontal=True)
            status_val = "เผยแพร่แล้ว" if publish_mode == "🚀 เผยแพร่ทันที" else "ฉบับร่าง"
                
            if st.button("✅ บันทึกตอน", type="primary", use_container_width=True):
                if chapter_name and chapter_content:
                    supabase.table("chapters").insert({
                        "novel_title": novel_name, "chapter_name": chapter_name,
                        "content": chapter_content, "status": status_val
                    }).execute()
                    st.rerun()

# ==========================================
# 4. หน้าแดชบอร์ดสถิติ (ANALYTICS)
# ==========================================
def analytics_dashboard_view():
    st.title("📊 สถิติผู้เข้าชมเชิงลึก")
    if st.button("◀ กลับไปพื้นที่นักเขียน"): go_to('workspace')
    st.info("รอการเชื่อมต่อข้อมูลสถิติจากฐานข้อมูลจริง")

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📕 MinichikoNovel")
    
    if st.session_state['logged_in']:
        st.success(f"👤 นักเขียน: {st.session_state['username']}")
        st.divider()
        if st.button("✒️ พื้นที่นักเขียน", use_container_width=True): go_to('workspace')
        if st.button("📊 สถิติหลังบ้าน", use_container_width=True): go_to('analytics')
        st.divider()
        if st.button("🚪 ออกจากระบบ", use_container_width=True): logout_user()
    else:
        st.info("สถานะ: นักอ่านทั่วไป")
        if st.button("🏠 หน้าแรกนิยาย", use_container_width=True): go_to('home')
        if st.button("🔐 เข้าสู่ระบบนักเขียน", type="primary", use_container_width=True): go_to('login')

# --- MAIN CONTROLLER ---
if st.session_state['current_view'] == 'login': login_page_view()
elif st.session_state['current_view'] == 'workspace' and st.session_state['logged_in']: writer_workspace_view()
elif st.session_state['current_view'] == 'manage_chapters' and st.session_state['logged_in']: manage_chapters_view()
elif st.session_state['current_view'] == 'analytics' and st.session_state['logged_in']: analytics_dashboard_view()
elif st.session_state['current_view'] == 'novel_detail': novel_detail_view()
elif st.session_state['current_view'] == 'read_chapter': read_chapter_view()
elif st.session_state['current_view'] == 'home': home_page_view()
else: go_to('workspace' if st.session_state['logged_in'] else 'home')