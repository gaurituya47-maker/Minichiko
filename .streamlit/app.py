import streamlit as st
import time
from datetime import datetime, timedelta

# --- CONFIGURATION & STATE MANAGEMENT ---
st.set_page_config(page_title="MinichikoNovel - อ่านเขียนนิยาย", page_icon="📕", layout="wide")

# ตรวจสอบสถานะและตัวแปรควบคุมหน้าต่างๆ
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'home' # home, login, writer, manage_chapters
if 'show_create_form' not in st.session_state:
    st.session_state['show_create_form'] = False
if 'editing_novel_name' not in st.session_state:
    st.session_state['editing_novel_name'] = ""

# --- MOCK DATA (จำลองฐานข้อมูล) ---
USERS = {
    "writer001": "password123",
    "admin": "admin"
}

MOCK_NOVELS = [
    {"id": 1, "title": "เมื่อรัชทายาทสวมหน้ากาก...", "author": "Minichiko", "desc": "เมื่อรัชทายาทสวมหน้ากาก ทรราชจะครองแผ่นดิน...", "cover": "https://via.placeholder.com/150/E63946/FFFFFF?text=CrownPrince"},
    {"id": 2, "title": "The Omega's Redemption", "author": "Meilifang", "desc": "เส้นทางการไถ่บาปและโชคชะตาที่ไม่อาจหลีกเลี่ยง...", "cover": "https://via.placeholder.com/150/E63946/FFFFFF?text=Omega"},
    {"id": 3, "title": "เกิดใหม่เป็นคุณชายไฮโซ", "author": "Minichiko", "desc": "ชีวิตใหม่ในฐานะคุณชายตระกูลใหญ่...", "cover": "https://via.placeholder.com/150/E63946/FFFFFF?text=YoungMaster"},
    {"id": 4, "title": "วันวาน (The Past Day)", "author": "Minichiko", "desc": "เรื่องราวความทรงจำและความรักในวันวาน...", "cover": "https://via.placeholder.com/150/E63946/FFFFFF?text=PastDay"},
]

# --- FUNCTIONS สำหรับควบคุมระบบ ---
def go_to(view, novel_name=""):
    st.session_state['current_view'] = view
    if novel_name:
         st.session_state['editing_novel_name'] = novel_name
    st.rerun()

def login_user(username):
    st.session_state['logged_in'] = True
    st.session_state['username'] = username
    st.success(f"ยินดีต้อนรับคุณ {username} เข้าสู่ระบบ!")
    time.sleep(1)
    go_to('writer')

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state['username'] = None
    st.session_state['show_create_form'] = False
    st.session_state['editing_novel_name'] = ""
    go_to('home')

# --- PAGE VIEWS (หน้าระบบต่างๆ) ---

def home_page_view():
    st.title("📕 MinichikoNovel")
    st.markdown("แหล่งรวมนิยาย BL และนิยายจีนโบราณฮิตติดชาร์ต")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    
    for i, novel in enumerate(MOCK_NOVELS):
        with cols[i % 4]:
            st.image(novel['cover'], use_column_width=True)
            st.subheader(novel['title'])
            st.caption(f"โดย: {novel['author']}")
            st.write(novel['desc'])
            if st.button(f"📖 อ่านเลย", key=f"read_{novel['id']}", use_container_width=True):
                st.toast("กำลังเข้าสู่หน้าอ่าน (Demo Mode)")

def login_page_view():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 เข้าสู่ระบบ")
        st.markdown("สำหรับนักเขียนและนักอ่าน MinichikoNovel")
        with st.form("login_form"):
            username = st.text_input("Username (ลองใช้: writer001)")
            password = st.text_input("Password (ลองใช้: password123)", type="password")
            submit = st.form_submit_button("เข้าสู่ระบบ", type="primary", use_container_width=True)
            
            if submit:
                if username in USERS and USERS[username] == password:
                    login_user(username)
                else:
                    st.error("Username หรือ Password ไม่ถูกต้อง")

def writer_dashboard_view():
    st.title(f"✒️ ระบบจัดการนักเขียน")
    st.caption(f"ผู้ใช้งาน: {st.session_state['username']}")
    
    st.markdown("### 📈 ภาพรวมสถิติเดือนนี้")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ยอดวิวรวม", "245.8K", "+18%")
    col2.metric("คอมเมนต์ใหม่", "4,120", "+12%")
    col3.metric("ผู้ติดตามเพิ่ม", "350", "+45")
    col4.metric("รายได้โดยประมาณ", "฿52,500", "+฿4,200")
    
    st.divider()

    if st.button("➕ เพิ่มงานเขียนใหม่", type="primary", use_container_width=True):
        st.session_state['show_create_form'] = not st.session_state['show_create_form']

    if st.session_state['show_create_form']:
        with st.container(border=True):
            st.markdown("### ✨ สร้างนิยายเรื่องใหม่")
            novel_title = st.text_input("ชื่อเรื่อง", placeholder="ใส่ชื่อนิยายของคุณที่นี่...")
            c_form1, c_form2 = st.columns(2)
            with c_form1:
                pen_name = st.selectbox("นามปากกา", ["Minichiko", "Meilifang", "อื่นๆ"])
                category = st.selectbox("หมวดหมู่", ["นิยายวาย (BL)", "นิยายจีนโบราณ", "โรมานซ์", "แฟนตาซี"])
                novel_desc = st.text_area("คำโปรย (Synopsis)", height=150)
            with c_form2:
                cover_image = st.file_uploader("🖼️ อัปโหลดไฟล์รูปภาพหน้าปก", type=['png', 'jpg', 'jpeg'])
                if cover_image: st.image(cover_image, caption="พรีวิวหน้าปก", width=200)
            
            if st.button("💾 บันทึกและสร้างเรื่อง", type="primary"):
                st.success(f"สร้างโปรเจกต์นิยายสำเร็จ!")
                st.session_state['show_create_form'] = False
                time.sleep(1)
                st.rerun()

    st.markdown("### 📚 งานเขียนของฉัน")
    tab1, tab2 = st.tabs(["เผยแพร่แล้ว (2)", "ฉบับร่าง (0)"])
    
    with tab1:
        # นิยายเรื่องที่ 1
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.subheader(f"📕 เมื่อรัชทายาทสวมหน้ากาก...")
            c1.caption(f"นามปากกา: Minichiko | หมวด: BL")
            c2.write(f"👁‍🗨 103,800 วิว")
            c2.write(f"💬 920 คอมเมนต์")
            if c3.button("✏️ จัดการตอน", key="edit_1", type="secondary", use_container_width=True):
                go_to('manage_chapters', "เมื่อรัชทายาทสวมหน้ากาก...")
            c3.button("📊 สถิติเชิงลึก", key="stat_1", use_container_width=True)
            
        # นิยายเรื่องที่ 2
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.subheader(f"📕 The Omega's Redemption")
            c1.caption(f"นามปากกา: Meilifang | หมวด: BL / โอเมก้าเวิร์ส")
            c2.write(f"👁‍🗨 142,000 วิว")
            c2.write(f"💬 3,200 คอมเมนต์")
            if c3.button("✏️ จัดการตอน", key="edit_2", type="secondary", use_container_width=True):
                go_to('manage_chapters', "The Omega's Redemption")
            c3.button("📊 สถิติเชิงลึก", key="stat_2", use_container_width=True)

# --- หน้าต่างจัดการตอนและเพิ่มตอนใหม่ (Chapter Management) ---
def manage_chapters_view():
    novel_name = st.session_state.get('editing_novel_name', 'นิยายของฉัน')
    
    # Header สไตล์ Writer
    col_h1, col_h2 = st.columns([5, 1])
    with col_h1:
        st.title(f"📖 จัดการตอน: {novel_name}")
    with col_h2:
        if st.button("◀ กลับไปหน้าหลัก", use_container_width=True):
            go_to('writer')
            
    st.divider()
    
    # แบ่งหน้าจอเป็น 2 ส่วน: รายการตอนเดิม (ซ้าย) กับ ฟอร์มเพิ่มตอนใหม่ (ขวา)
    col_list, col_editor = st.columns([1, 2])
    
    with col_list:
        st.subheader("📑 รายการตอนทั้งหมด")
        with st.container(border=True):
            st.markdown("**ตอนที่ 1:** จุดเริ่มต้นของโชคชะตา  \n`[เผยแพร่แล้ว] 👁‍🗨 12.5K วิว`")
            st.markdown("---")
            st.markdown("**ตอนที่ 2:** การพบกันอีกครั้ง  \n`[เผยแพร่แล้ว] 👁‍🗨 10.2K วิว`")
            st.markdown("---")
            st.markdown("**ตอนที่ 3:** ความลับที่ถูกซ่อน  \n`[ตั้งเวลา] 🗓️ 25 ก.พ. 2026 18:00`")
            st.button("⚙️ จัดการตอนทั้งหมด", use_container_width=True)

    with col_editor:
        st.subheader("➕ เพิ่มตอนใหม่")
        with st.container(border=True):
            chapter_name = st.text_input("ชื่อตอน", placeholder="เช่น ตอนที่ 4: ลางร้ายคืบคลาน...")
            
            # ช่องเขียนเนื้อหา (Text Editor แบบง่าย)
            st.markdown("เนื้อหาตอน (พิมพ์หรือวางเนื้อหาที่นี่)")
            chapter_content = st.text_area("เนื้อหาตอน", height=350, label_visibility="collapsed")
            st.caption(f"จำนวนคำคร่าวๆ: {len(chapter_content.split())} คำ")
            
            # ระบบตั้งเวลา Publish
            st.markdown("### 🕒 ตั้งค่าการเผยแพร่")
            publish_mode = st.radio("เลือกรูปแบบการเผยแพร่", ["🚀 เผยแพร่ทันที", "⏰ ตั้งเวลาล่วงหน้า", "💾 บันทึกเป็นฉบับร่าง (Draft)"], horizontal=True)
            
            if publish_mode == "⏰ ตั้งเวลาล่วงหน้า":
                c_date, c_time = st.columns(2)
                with c_date:
                    # ค่าเริ่มต้นเป็นวันพรุ่งนี้
                    sched_date = st.date_input("วันที่", value=datetime.today() + timedelta(days=1))
                with c_time:
                    # ค่าเริ่มต้น 18:00 (เวลาไพร์มไทม์คนอ่านนิยาย)
                    sched_time = st.time_input("เวลา", value=datetime.strptime("18:00", "%H:%M").time())
                st.info(f"นิยายจะอัปเดตอัตโนมัติในวันที่ {sched_date.strftime('%d/%m/%Y')} เวลา {sched_time.strftime('%H:%M')} น.")
                
            # ปุ่มบันทึก
            if st.button("✅ บันทึกและตั้งค่า", type="primary", use_container_width=True):
                if chapter_name and chapter_content:
                    st.success(f"บันทึกตอน '{chapter_name}' เรียบร้อยแล้ว! (ระบบจำลอง)")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.error("กรุณาใส่ชื่อตอนและเนื้อหาก่อนบันทึก")

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("📕 MinichikoNovel")
    
    if st.session_state['logged_in']:
        st.success(f"👤 ผู้ใช้: {st.session_state['username']}")
        if st.button("🏠 หน้าแรกนิยาย", use_container_width=True):
             go_to('home')
        if st.button("✒️ โหมดนักเขียน", type="primary", use_container_width=True):
             go_to('writer')
        st.divider()
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            logout_user()
    else:
        st.info("สถานะ: บุคคลทั่วไป")
        if st.button("🏠 หน้าแรกนิยาย", use_container_width=True):
             go_to('home')
        if st.button("🔐 เข้าสู่ระบบ / สมัครสมาชิก", type="primary", use_container_width=True):
             go_to('login')
    
    st.markdown("---")
    st.caption("MinichikoNovel Platform © 2026")

# --- MAIN APP CONTROLLER ---
if st.session_state['logged_in']:
    if st.session_state['current_view'] == 'writer':
        writer_dashboard_view()
    elif st.session_state['current_view'] == 'manage_chapters':
        manage_chapters_view()
    elif st.session_state['current_view'] == 'home':
        home_page_view()
    else:
        go_to('writer') 
else:
    if st.session_state['current_view'] == 'login':
        login_page_view()
    else:
        home_page_view()