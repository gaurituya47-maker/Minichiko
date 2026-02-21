import streamlit as st
import time

# --- CONFIGURATION & STATE MANAGEMENT ---
st.set_page_config(page_title="RedNovel - อ่านเขียนนิยาย", page_icon="📕", layout="wide")

# ตรวจสอบสถานะการ Login ถ้ายังไม่มีให้ตั้งเป็น False
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'home' # home, login, writer, reader

# --- MOCK DATA (จำลองฐานข้อมูล) ---
# จำลองบัญชีผู้ใช้ (Username: Password)
USERS = {
    "writer001": "password123",
    "reader_a": "read123"
}

# จำลองข้อมูลนิยายสำหรับหน้าแรก
MOCK_NOVELS = [
    {"id": 1, "title": "กุหลาบสีเลือด", "author": "RedQueen", "desc": "ความรักในคฤหาสน์ต้องสาป...", "cover": "https://via.placeholder.com/150/E63946/FFFFFF?text=Rose"},
    {"id": 2, "title": "ระบบพลิกชะตานางร้าย", "author": "หมี่เหลือง", "desc": "ทะลุมิติไปเป็นนางร้ายเกรด B...", "cover": "https://via.placeholder.com/150/E63946/FFFFFF?text=Villainess"},
    {"id": 3, "title": "CEO คลั่งรัก", "author": "SugarDaddy", "desc": "เขาเย็นชากับทั้งโลก แต่เร่าร้อนกับเธอ...", "cover": "https://via.placeholder.com/150/E63946/FFFFFF?text=CEO"},
    {"id": 4, "title": "จอมยุทธ์เซียน", "author": "เทพกระบี่", "desc": "เส้นทางสู่ความเป็นอมตะ...", "cover": "https://via.placeholder.com/150/E63946/FFFFFF?text=Xianxia"},
]

# จำลองงานเขียนของนักเขียน (สำหรับ Writer Mode)
MOCK_MY_WORKS = [
    {"title": "โปรเจกต์ลับ S", "status": "เผยแพร่แล้ว", "views": 15420, "comments": 320, "income": "฿4,500"},
    {"title": "บันทึกของแม่มดแดง", "status": "ฉบับร่าง", "views": 0, "comments": 0, "income": "฿0"},
]

# --- FUNCTIONS สำหรับเปลี่ยนหน้า ---
def go_to(view):
    st.session_state['current_view'] = view
    st.rerun()

def login_user(username):
    st.session_state['logged_in'] = True
    st.session_state['username'] = username
    st.success(f"ยินดีต้อนรับคุณ {username} เข้าสู่ระบบ!")
    time.sleep(1)
    go_to('writer') # Login สำเร็จให้เด้งไปหน้า Writer ทันที

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    go_to('home')

# --- PAGE VIEWS (หน้าระบบต่างๆ) ---

def home_page_view():
    st.title("📕 RedNovel แหล่งรวมนิยายมาแรง")
    st.markdown("---")
    
    # แสดงรายการนิยายแบบการ์ด
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    
    for i, novel in enumerate(MOCK_NOVELS):
        with cols[i % 4]:
            st.image(novel['cover'], use_column_width=True)
            st.subheader(novel['title'])
            st.caption(f"โดย: {novel['author']}")
            st.write(novel['desc'])
            if st.button(f"📖 อ่านเลย ({novel['id']})", key=f"read_{novel['id']}"):
                st.toast("กำลังเข้าสู่หน้าอ่าน (Demo Mode)")
                # ในระบบจริงจะลิงก์ไปหน้า Reader view

def login_page_view():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 เข้าสู่ระบบ")
        st.markdown("สำหรับนักเขียนและนักอ่าน")
        with st.form("login_form"):
            username = st.text_input("Username (ลองใช้: writer001)")
            password = st.text_input("Password (ลองใช้: password123)", type="password")
            submit = st.form_submit_button("เข้าสู่ระบบ", type="primary")
            
            if submit:
                if username in USERS and USERS[username] == password:
                    login_user(username)
                else:
                    st.error("Username หรือ Password ไม่ถูกต้อง")
        st.markdown("ยังไม่มีบัญชี? [สมัครสมาชิก](#)")

def writer_dashboard_view():
    # เลียนแบบ Header ของ ReadAWrite
    st.title(f"✒️ สวัสดีคุณ {st.session_state['username']}")
    st.caption("จัดการงานเขียนของคุณได้ที่นี่")
    
    # ส่วนสรุปสถิติ (Stats Overview)
    st.markdown("### 📈 ภาพรวมสถิติเดือนนี้")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ยอดวิวรวม", "15.4K", "+12%")
    col2.metric("คอมเมนต์ใหม่", "320", "+5%")
    col3.metric("ผู้ติดตามเพิ่ม", "45", "+2")
    col4.metric("รายได้โดยประมาณ", "฿4,500", "+฿500")
    
    st.divider()

    # ปุ่ม Action หลัก
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        st.button("➕ เพิ่มงานเขียนใหม่", type="primary", use_container_width=True)
    
    # ส่วนจัดการงานเขียน (Tabbed Interface)
    st.markdown("### 📚 งานเขียนของฉัน")
    tab1, tab2 = st.tabs(["เผยแพร่แล้ว (1)", "ฉบับร่าง (1)"])
    
    with tab1:
        work = MOCK_MY_WORKS[0]
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.subheader(f"📕 {work['title']}")
            c1.caption(f"สถานะ: {work['status']} | 👁‍🗨 {work['views']} วิว")
            c2.write(f"💬 {work['comments']} คอมเมนต์")
            c2.write(f"💰 รายได้: {work['income']}")
            c3.button("✏️ แก้ไข/เพิ่มตอน", key="edit_1", type="secondary", use_container_width=True)
            c3.button("📊 ดูสถิติ", key="stat_1", use_container_width=True)

    with tab2:
        work = MOCK_MY_WORKS[1]
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.subheader(f"📓 {work['title']}")
            c1.caption(f"สถานะ: {work['status']}")
            c3.button("✏️ เขียนต่อ", key="edit_2", type="primary", use_container_width=True)
            c3.button("🗑️ ลบ", key="del_2", use_container_width=True)

# --- SIDEBAR NAVIGATION (เมนูหลัก) ---
with st.sidebar:
    st.title("📕 RedNovel")
    
    if st.session_state['logged_in']:
        st.success(f"👤 ผู้ใช้: {st.session_state['username']}")
        if st.button("🏠 หน้าแรกนิยาย", use_container_width=True):
             go_to('home')
        if st.button("✒️ โหมดนักเขียน (Dashboard)", type="primary", use_container_width=True):
             go_to('writer')
        st.divider()
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            logout_user()
    else:
        st.info("ยังไม่ได้เข้าสู่ระบบ")
        if st.button("🏠 หน้าแรกนิยาย", use_container_width=True):
             go_to('home')
        if st.button("🔐 เข้าสู่ระบบ / สมัครสมาชิก", type="primary", use_container_width=True):
             go_to('login')
    
    st.markdown("---")
    st.caption("RedNovel Demo © 2024")

# --- MAIN APP CONTROLLER (ตัวควบคุมการแสดงผลหน้า) ---
if st.session_state['logged_in']:
    # Logic สำหรับผู้ที่ Login แล้ว
    if st.session_state['current_view'] == 'writer':
        writer_dashboard_view()
    elif st.session_state['current_view'] == 'home':
        home_page_view()
    else:
        # ถ้าหลงไปหน้า login ทั้งที่ login แล้ว ให้เด้งไป writer
        go_to('writer') 
else:
    # Logic สำหรับผู้ที่ยังไม่ Login
    if st.session_state['current_view'] == 'login':
        login_page_view()
    else:
        home_page_view()