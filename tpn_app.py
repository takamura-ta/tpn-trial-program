import streamlit as st
import pandas as pd
import math
from fpdf import FPDF
import os

# --- FUNCTION: CREATE PDF REPORT (ฉบับอัปเดต Indication & Supplements) ---
def create_pdf_report(data):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(current_dir, 'THSarabunNew.ttf')
    font_bold_path = os.path.join(current_dir, 'THSarabunNew_Bold.ttf')

    if os.path.exists(font_path) and os.path.exists(font_bold_path):
        pdf.add_font('THSarabun', '', font_path)
        pdf.add_font('THSarabun', 'B', font_bold_path)
        font_main = 'THSarabun'
    else:
        font_main = 'Arial'

    pdf.add_page()
    
    # 1. Header
    pdf.set_font(font_main, 'B', 20)
    pdf.cell(190, 10, "รายงานแผนการให้โภชนบำบัดทางหลอดเลือดดำ (TPN Report)", 0, 1, 'C')
    pdf.set_font(font_main, '', 12)
    pdf.cell(190, 7, f"วันที่ออกรายงาน: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, 'R')
    pdf.line(10, 32, 200, 32)
    pdf.ln(5)

    # 2. ข้อมูลผู้ป่วย
    pdf.set_font(font_main, 'B', 15)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(190, 8, " 1. ข้อมูลผู้ป่วย (Patient Information)", 0, 1, 'L', True)
    pdf.set_font(font_main, '', 14)
    pdf.set_x(15)
    pdf.cell(63, 8, f"ชื่อ-นามสกุล: {data['name']}", 0, 0)
    pdf.cell(63, 8, f"อายุ: {data['age']} ปี", 0, 0)
    pdf.cell(64, 8, f"หอผู้ป่วย: {data['ward']}", 0, 1)
    pdf.set_x(15)
    pdf.cell(63, 8, f"น้ำหนัก: {data['weight']} kg", 0, 0)
    pdf.cell(63, 8, f"IBW: {data['ibw']:.1f} kg", 0, 0)
    pdf.cell(64, 8, f"BMI: {data['bmi']:.1f} kg/m2", 0, 1)
    pdf.ln(2)

    # 3. ข้อบ่งชี้และความจำเป็น (Indications)
    pdf.set_font(font_main, 'B', 15)
    pdf.cell(190, 8, " 2. ข้อบ่งชี้และความจำเป็น (Indications)", 0, 1, 'L', True)
    pdf.ln(2)

    # หัวข้อ: PN Indication
    pdf.set_x(15)
    pdf.set_font(font_main, 'B', 13)
    pdf.cell(35, 7, "[ PN Indication ] : ", 0, 0) # พิมพ์หัวข้อหนาๆ และไม่ขึ้นบรรทัดใหม่
    
    pdf.set_font(font_main, '', 13)
    pn_text = ", ".join(data['indications']) if data['indications'] else "-"
    # ใช้ multi_cell เพื่อให้ถ้าข้อความยาวเกิน 155mm มันจะตัดลงบรรทัดใหม่ให้เองโดยไม่ตกขอบ
    pdf.multi_cell(155, 7, pn_text, 0, 'L')

    # หัวข้อ: EN Contraindications
    pdf.set_x(15)
    pdf.set_font(font_main, 'B', 13)
    pdf.cell(45, 7, "[ EN Contraindications ] : ", 0, 0)
    
    pdf.set_font(font_main, '', 13)
    en_text = ", ".join(data['en_contra']) if data['en_contra'] else "-"
    pdf.multi_cell(145, 7, en_text, 0, 'L')

    # 4. ผลการประเมิน Nutritional assessment
    pdf.ln(2)
    pdf.set_x(10)
    pdf.set_font(font_main, 'B', 15)
    pdf.cell(190, 8, " 3. การประเมินโภชนาการและความเสี่ยงการขาดสารอาหาร", 0, 1, 'L', True)
    pdf.ln(2)
    # แสดง NAF Score และระดับความรุนแรง
    pdf.set_font(font_main, '', 15)
    pdf.set_x(15)
    pdf.cell(95, 7, f"NAF Score: {data['naf_score']} ({data['naf_cat']})", 0, 0)
    pdf.cell(95, 7, f"ระดับความรุนแรง: {data['mal_level']}", 0, 1)

    # แสดงความเสี่ยง Refeeding Syndrome (ตัวหนังสือสีแดงถ้าเป็น High Risk)
    if data['is_refeeding'] == "High Risk":
        pdf.set_text_color(200, 0, 0) # สีแดง
    
    pdf.set_x(15)
    pdf.set_font(font_main, 'B', 13)
    pdf.cell(190, 7, f"ความเสี่ยง Refeeding Syndrome: {data['is_refeeding']}", 0, 1)
    
    # แสดงปัจจัยเสี่ยง (ถ้ามี)
    if data['refeeding_details']:
        pdf.set_font(font_main, '', 12)
        pdf.set_x(15)
        pdf.multi_cell(180, 6, f"ปัจจัยเสี่ยงที่พบ: {data['refeeding_details']}", 0, 'L')
    
    pdf.set_text_color(0, 0, 0) # รีเซ็ตสีเป็นสีดำปกติ
    pdf.ln(2)

    # 5. เป้าหมายและแผนการให้ (Prescription)
    pdf.set_font(font_main, 'B', 15)
    pdf.cell(190, 8, " 4. แผนการให้สารอาหาร (Prescription)", 0, 1, 'L', True)
    pdf.ln(2)
    
    # ส่วนแสดง Target (เพิ่มใหม่เพื่อให้เห็นเป้าหมายก่อนดูแผนการให้)
    pdf.set_font(font_main, 'B', 13)
    pdf.set_x(15)
    pdf.cell(180, 7, f"เป้าหมายการคำนวณ (Target): Energy {data['target_kcal']:.0f} kcal/day | Protein {data['target_pro']:.1f} g/day", 0, 1, 'L')
    pdf.ln(1)

    # หัวตาราง
    pdf.set_font(font_main, 'B', 14)
    pdf.cell(75, 10, "รายการสารอาหาร", 1, 0, 'C')
    pdf.cell(45, 10, "Rate (ml/hr)", 1, 0, 'C')
    pdf.cell(35, 10, "เวลา (hr)", 1, 0, 'C')
    pdf.cell(35, 10, "ปริมาณรวม (ml)", 1, 1, 'C')
    
    # ข้อมูลในตาราง
    pdf.set_font(font_main, '', 14)
    pdf.cell(75, 10, f"{data['pn_name']}", 1, 0, 'C')
    pdf.cell(45, 10, f"{data['final_rate']}", 1, 0, 'C')
    pdf.cell(35, 10, f"{data['hours']}", 1, 0, 'C')
    pdf.cell(35, 10, f"{data['actual_pn_vol']:.0f}", 1, 1, 'C')
    
    if data['add_amiparen']:
        pdf.cell(75, 10, "10% Amiparen", 1, 0, 'C')
        pdf.cell(45, 10, f"{data['final_ami_rate']}", 1, 0, 'C')
        pdf.cell(35, 10, f"{data['hours']}", 1, 0, 'C')
        pdf.cell(35, 10, f"{data['actual_ami_vol']:.0f}", 1, 1, 'C')

    # แถวสรุป Actual Delivered (ต่อท้ายตารางทันที)
    pdf.set_font(font_main, 'B', 13)
    pdf.set_fill_color(245, 245, 245)
    summary_text = f"ได้รับจริง (Actual): Energy {data['delivered_kcal']:.0f} kcal ({ (data['delivered_kcal']/data['target_kcal']*100):.0f}%) | Protein {data['delivered_pro']:.1f} g ({ (data['delivered_pro']/data['target_pro']*100):.0f}%)"
    pdf.cell(190, 10, summary_text, 1, 1, 'C', True)
    pdf.ln(4)

    # 6. Vitamin & Trace Elements (แสดงรายละเอียดการเลือก)
    pdf.set_font(font_main, 'B', 15)
    pdf.cell(190, 8, " 5. วิตามินและแร่ธาตุ (Vitamin & Trace Elements)", 0, 1, 'L', True)
    pdf.ln(1)
    
    pdf.set_font(font_main, '', 14)
    # ใช้ตัวแปร flag เพื่อเช็คว่ามีการเลือกอย่างน้อย 1 รายการหรือไม่
    has_any_supp = False
    
    # รายการวิตามินและแร่ธาตุ (บังคับ set_x(15) ทุกครั้งเพื่อกันตกขอบ)
    supps = []
    if data.get('b_complex', 0) > 0: supps.append(f"Vitamin B complex {data['b_complex']} vial(s)")
    if data.get('soluvit'): supps.append("Soluvit-N 1 vial")
    if data.get('vitalipid'): supps.append("Vitalipid-N Adult 1 vial")
    if data.get('addamel'): supps.append("Addamel-N 1 vial")
    
    if supps:
        pdf.set_x(15)
        pdf.multi_cell(180, 7, f"• วิตามิน/แร่ธาตุ: {', '.join(supps)}", 0, 'L')
        has_any_supp = True

    # รายการเกลือแร่ (Electrolytes)
    if data.get('kcl', 0) > 0 or data.get('k2po4', 0) > 0:
        pdf.set_x(15)
        pdf.cell(190, 7, f"• Electrolytes: KCl {data['kcl']} mEq/L, K2PO4 {data['k2po4']} mEq/L", 0, 1)
        has_any_supp = True
    
    if not has_any_supp:
        pdf.set_x(15)
        pdf.cell(190, 7, "  - ไม่มีการให้วิตามินหรือเกลือแร่เสริม", 0, 1)
    
    pdf.ln(2)

    # 7. บทสรุปสารอาหารจริง (Actual vs Target)
    pdf.ln(2)
    pdf.set_font(font_main, 'B', 15)
    pdf.cell(190, 8, "สรุปสารอาหารที่ได้รับจริง (Actual Delivered):", 0, 1)
    
    pdf.set_font(font_main, '', 15)
    pdf.set_x(15) # ขยับเยื้องเข้ามาเล็กน้อยให้สวยงาม
    pdf.cell(63, 8, f"- พลังงาน: {data['delivered_kcal']:.0f} kcal/day", 0, 0)
    pdf.cell(63, 8, f"- โปรตีน: {data['delivered_pro']:.1f} g/day", 0, 0)
    pdf.cell(64, 8, f"- สารน้ำรวม: {data['delivered_vol']:.0f} ml/day", 0, 1)
    
    pdf.set_x(15)
    pdf.cell(190, 8, f"- Lipid Infusion Rate: {data['actual_lipid_rate']:.3f} g/kg/hr", 0, 1)
    
    # แสดงข้อมูลอื่นๆ
    pdf.set_x(15)
    pdf.cell(95, 8, f"• สารน้ำรวม (Total Vol): {data['delivered_vol']:.0f} ml/day (Limit: {data.get('fluid_limit', '-')})", 0, 0)
    pdf.cell(95, 8, f"• Lipid Infusion Rate: {data['actual_lipid_rate']:.3f} g/kg/hr", 0, 1)
    
    # --- ส่วนท้ายของรายงาน: ลายเซ็นแพทย์ ---
    pdf.ln(10) 
    
    # เช็คว่าพื้นที่พอพิมพ์ไหม ถ้าเหลือน้อยกว่า 40mm ให้ขึ้นหน้าใหม่
    if pdf.get_y() > 250:
        pdf.add_page()

    pdf.set_font(font_main, 'B', 13)
    current_y = pdf.get_y()
    
    # แพทย์ #1 (ชิดซ้าย)
    pdf.set_xy(15, current_y)
    pdf.multi_cell(85, 7, f"ลงชื่อ: {data['physician_1']}\nแพทย์ผู้สั่งการรักษา", 0, 'C')
    
    # แพทย์ #2 (ชิดขวาในระยะกระดาษ)
    pdf.set_xy(110, current_y)
    pdf.multi_cell(85, 7, f"ลงชื่อ: {data['physician_2']}\nแพทย์ผู้ตรวจสอบ", 0, 'C')

    return pdf.output(dest='S')

# 1. Setup Theme และหน้าจอ
st.set_page_config(page_title="Thai TPN Support System", layout="wide")

# CSS สำหรับความสวยงามและการมองเห็น
st.markdown("""
    <style>
    .main, p, div, span, h1, h2, h3 { color: var(--text-color); }
    .stTable { background-color: transparent !important; }
    .stTable td, .stTable th { color: var(--text-color) !important; border-bottom: 1px solid #444 !important; }
    h1, h2, h3 { color: #2e7d32 !important; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #2e7d32; color: white; border: none; }
    [data-testid="stMetricValue"] { color: var(--text-color); }
    .highlight-box { padding: 20px; border-radius: 10px; background-color: rgba(46, 125, 50, 0.1); border: 1px solid #2e7d32; margin-bottom: 20px; }
    .target-box { padding: 15px; border-radius: 8px; background-color: rgba(33, 150, 243, 0.1); border: 1px solid #2196f3; margin-bottom: 15px; }
    .caution-box { padding: 10px; border-radius: 5px; background-color: rgba(255, 75, 75, 0.1); border-left: 5px solid #ff4b4b; margin-top: 10px; font-size: 0.85em; }
    .lipid-box { padding: 15px; border-radius: 8px; background-color: rgba(156, 39, 176, 0.05); border: 1px solid #9c27b0; margin-top: 10px; }
    .infusion-control { background-color: rgba(46, 125, 50, 0.05); padding: 15px; border-radius: 10px; border: 1px dashed #2e7d32; }
    .manual-input-box { border: 1px solid #ccc; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
    .amiparen-box { padding: 15px; border-radius: 8px; background-color: rgba(255, 152, 0, 0.1); border: 1px solid #ff9800; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
if 'naf_score_total' not in st.session_state:
    st.session_state.naf_score_total = 0
if 'naf_category' not in st.session_state:
    st.session_state.naf_category = "A"

st.title("🏥 Thai TPN Clinical Support")
st.caption("Ref. : Thai JPEN Clinical Practice Recommendation for Parenteral Nutrition Management in Adult Hospitalized Patients in 2019")

# --- SIDEBAR: ข้อมูลพื้นฐาน ---
st.sidebar.header("1. Patient data")
name = st.sidebar.text_input("ชื่อ-นามสกุล")
age = st.sidebar.text_input("อายุ")
ward = st.sidebar.text_input("Ward")
gender = st.sidebar.radio("เพศ", ["ชาย", "หญิง"])
height = st.sidebar.number_input("ส่วนสูง (cm)", value=165.0)
weight = st.sidebar.number_input("น้ำหนักปัจจุบัน (kg)", value=60.0)
location = st.sidebar.selectbox("Setting", ["General Ward", "ICU"])

st.sidebar.divider()
st.sidebar.header("2. Supplement data")
route = st.sidebar.selectbox("Access Route", ["Peripheral Line", "Central Line"])
fluid_limit = st.sidebar.number_input("Fluid Limit (ml/day)", value=2500)

# --- BASELINE MATH ---
ibw = (height - 100) if gender == "ชาย" else (height - 105)
bmi = weight / ((height/100)**2)

# --- 1. MODIFIED NAF ASSESSMENT ---
st.header("1. Nutritional Assessment (Modified NAF)")
st.caption("Ref. : ปรับปรุงจาก Surat Komindr, et al. Asia Pac J Clin Nutr 2013:22(4) : 516-521")
with st.expander("📝 ประเมิน NAF (คลิกที่นี่)", expanded=False):
    st.markdown("### การประเมินภาวะโภชนาการ (ศิริราช)")
    col1, col2 = st.columns(2)
    with col1:
        sc1_1 = st.selectbox("1. วิธีการชั่งน้ำหนัก:", ["0: ชั่งไม่ได้/ญาติบอก/ท่ายืน", "1: ชั่งในท่านอน"])
        bmi_p = 2 if bmi < 17.0 else (1 if (17.0 <= bmi <= 18.0) or (bmi > 30.0) else 0)
        st.write(f"2. คะแนน BMI ({bmi:.1f}): **{bmi_p} คะแนน**")
        sc2 = st.selectbox("3. ลักษณะรูปร่าง:", ["0: ปกติ-อ้วนปานกลาง", "1: ผอม หรือ อ้วนมาก", "2: ผอมมาก"])
        sc3 = st.selectbox("4. น้ำหนักที่เปลี่ยนใน 4 สัปดาห์:", ["0: ไม่ทราบ / คงเดิม", "1: เพิ่มขึ้น / อ้วนขึ้น", "2: ลดลง / ผอมลง"])
    with col2:
        sc4_1 = st.selectbox("5. ประเภทอาหารที่กิน (2 สัปดาห์):", ["0: อาหารปกติ", "1: อาหารนุ่มกว่าปกติ", "2: อาหารน้ำๆ / อาหารเหลว"])
        sc4_2 = st.selectbox("6. ปริมาณอาหารที่กิน (2 สัปดาห์):", ["0: ปกติ", "1: กินน้อยลง", "2: กินน้อยมาก"])
        sc5_1 = st.multiselect("7. อาการต่อเนื่อง (> 2 สัปดาห์):", ["สำลัก/กลืนลำบาก", "ท้องเสีย/ปวดท้อง", "อาเจียน/คลื่นไส้"])
        sc6 = st.selectbox("8. ความสามารถในการเข้าถึงอาหาร:", ["0: ปกติ / นั่งๆ นอนๆ", "1: ต้องมีผู้ช่วยบ้าง", "2: ช่วยเหลือตัวเองไม่ได้"])
    
    st.markdown("**9. โรคที่เป็นอยู่ (เลือกได้หลายโรคเพื่อรวมคะแนน)**")
    diseases_high = st.multiselect("กลุ่มโรค 6 คะแนน:", ["Stroke/CVA", "Severe Pneumonia", "Multiple fracture", "Malignant hematologic", "Critically ill"])
    diseases_mid = st.multiselect("กลุ่มโรค 3 คะแนน:", ["DM", "CKD-ESRD", "Cirrhosis/Hepatic encephalopathy", "Solid cancer", "Chronic heart failure", "Severe head injury", "Hip fracture", "COPD", ">2º of burn", "Septicemia"])

    if st.button("คำนวณและบันทึกคะแนน Mod.NAF"):
        sc7 = (len(diseases_high) * 6) + (len(diseases_mid) * 3)
        p5 = len(sc5_1) * 2
        total = int(sc1_1[0]) + bmi_p + int(sc2[0]) + int(sc3[0]) + int(sc4_1[0]) + int(sc4_2[0]) + p5 + int(sc6[0]) + sc7
        st.session_state.naf_score_total = total
        st.session_state.naf_category = "A" if total <= 5 else ("B" if total <= 14 else "C")
        st.success(f"ประเมินสำเร็จ! คะแนนโรค: {sc7} | คะแนนรวม: {total}")

# --- ผลสรุปเบื้องต้น & คำแนะนำ ---
st.divider()
c_res1, c_res2, c_res3 = st.columns(3)
with c_res1: st.metric("BMI", f"{bmi:.1f}")
with c_res2: st.metric("Ideal BW (kg)", f"{ibw:.1f}")
with c_res3: st.metric("Mod.NAF Category", st.session_state.naf_category)

nt_score = st.selectbox("NT 2013 Score (Nutrition Triage)", [1, 2, 3, 4])
naf_cat = st.session_state.naf_category

if (bmi < 16 or naf_cat == "C" or nt_score == 4):
    mal_level, sev_color = "Severe", "red"
    rec_text = "แนะนำเริ่มให้อาหารทางหลอดเลือดดำภายใน 3-5 วัน"
elif (16 <= bmi <= 16.99 or naf_cat == "B" or nt_score == 3):
    mal_level, sev_color = "Moderate", "orange"
    rec_text = "แนะนำเริ่มให้อาหารทางหลอดเลือดดำภายใน 3-5 วัน"
else:
    mal_level, sev_color = "Normal/Mild", "blue"
    rec_text = "แนะนำเริ่มให้อาหารทางหลอดเลือดดำหลังวันที่ 7"

st.subheader(f"ระดับความรุนแรง: :{sev_color}[{mal_level} Malnutrition]")
st.markdown(f"""<div style="padding: 10px; border-radius: 5px; background-color: rgba(0,0,0,0.05); border-left: 5px solid {sev_color};">
    <p style="margin:0; font-weight:bold; color:{sev_color};">📌 คำแนะนำทางคลินิก:</p><p style="margin:0;">{rec_text}</p></div>""", unsafe_allow_html=True)

# --- 2. INDICATION ---
st.header("2. Indication for PN")
with st.expander("ตรวจสอบข้อบ่งชี้", expanded=True):
    c1 = st.checkbox("ทุพโภชนาการ/เสี่ยงระดับปานกลางขึ้นไป")
    c2 = st.checkbox("ได้รับอาหาร < 60% ของเป้าหมาย")
    c3 = st.checkbox("Hemodynamically Stable")
    c4 = st.checkbox("ไม่ใช่ระยะสุดท้าย")
    e_list = st.multiselect("EN Contraindications:", ["Mechanical Obstruction", "Impaired Absorption", "Severe Ileus", "Bowel Rest", "Abdominal Compartment Syndrome", "ไม่สามารถใส่สายให้อาหารเข้าทางเดินอาหารได้"])

is_ready = all([c1, c2, c3, c4]) and len(e_list) > 0

# --- 3. TARGET & REFEEDING & CALCULATOR ---
if is_ready:
    st.success("✅ มีข้อบ่งชี้ในการเริ่ม TPN")
    st.header("3. Nutritional Target Setting")
    
    target_mode = st.radio("วิธีการกำหนดเป้าหมายสารอาหาร:", ["คำนวณอัตโนมัติตามเกณฑ์", "กำหนดเอง (Manual)"])
    
    if target_mode == "คำนวณอัตโนมัติตามเกณฑ์":
        if location == "General Ward":
            target_kcal = weight * 32.5 if bmi < 30 else (weight * 12.5 if bmi <= 50 else ibw * 23.5)
        else: # ICU
            target_kcal = weight * 22.5 if bmi < 30 else (weight * 12.5 if bmi <= 50 else ibw * 23.5)
        
        target_pro = weight * 1.35 if bmi < 30 else (ibw * 2.0 if bmi <= 40 else ibw * 2.25)
    else:
        col_m1, col_m2 = st.columns(2)
        target_kcal = col_m1.number_input("Energy (kcal/day):", value=2000.0, step=50.0)
        target_pro = col_m2.number_input("Protein (g/day):", value=80.0, step=5.0)

    # --- 3.1 REFEEDING RISK ASSESSMENT ---
    st.subheader("3.1 Refeeding Syndrome Risk Assessment")
    with st.expander("🔍 แบบทดสอบความเสี่ยงภาวะ Refeeding syndrome (NICE Criteria)", expanded=True):
        col_rf1, col_rf2 = st.columns(2)
        with col_rf1:
            rf_a1 = st.checkbox("BMI < 16 kg/m²", value=(bmi < 16))
            rf_a2 = st.checkbox("น้ำหนักลดโดยไม่ตั้งใจ > 15% ใน 3-6 เดือน")
            rf_a3 = st.checkbox("กินอาหารน้อยมาก/ไม่ได้เลย > 10 วัน")
            rf_a4 = st.checkbox("K, PO4 หรือ Mg ในเลือดต่ำก่อนเริ่ม")
        with col_rf2:
            rf_b1 = st.checkbox("BMI < 18.5 kg/m²", value=(16 <= bmi < 18.5))
            rf_b2 = st.checkbox("น้ำหนักลดโดยไม่ตั้งใจ > 10% ใน 3-6 เดือน")
            rf_b3 = st.checkbox("กินอาหารน้อยมาก/ไม่ได้เลย > 5 วัน")
            rf_b4 = st.checkbox("ประวัติ Alcohol abuse / ยา Insulin, Chemo, Diuretics")

        is_refeeding_risk = (sum([rf_a1, rf_a2, rf_a3, rf_a4]) >= 1) or (sum([rf_b1, rf_b2, rf_b3, rf_b4]) >= 2)

    if is_refeeding_risk:
        refeeding_kcal = weight * 10
        st.warning("⚠️ High Risk of Refeeding Syndrome")
        
        # 1. Hypocaloric Info Box
        st.markdown(f"""<div style="padding:15px; border-radius:10px; background-color:rgba(255,75,75,0.1); border:2px solid #ff4b4b; margin-bottom: 10px;">
            <h4 style='margin:0; color:#ff4b4b;'>คำแนะนำที่ 1: Hypocaloric Nutrition</h4>
            <p>• <b>พลังงานเริ่มต้น:</b> แนะนำ {refeeding_kcal:.0f} kcal/day (10 kcal/kg/day)</p>
            <p>• <b>การปรับเพิ่ม:</b> ค่อยๆ titrate จนได้เป้าหมาย ({target_kcal:.0f} kcal) ใน 7 วัน</p></div>""", unsafe_allow_html=True)

        # 2. Lead-in B-fluid Recommendation
        b_fluid_vol_needed = refeeding_kcal / 0.42
        b_fluid_rate_int = round(b_fluid_vol_needed / 24) # ปรับเป็นจำนวนเต็ม
        
        st.markdown(f"""<div style="padding:15px; border-radius:10px; background-color:rgba(33, 150, 243, 0.1); border:2px solid #2196f3; margin-bottom: 25px;">
            <h4 style='margin:0; color:#2196f3;'>คำแนะนำที่ 2: Lead-in Parenteral Nutrition</h4>
            <p>• <b>Fluid Type:</b> แนะนำ <b>B-fluid 1,000 ml</b> (Glucose 75g, AA 30g, 420 kcal)</p>
            <p>• <b>Volume Needed:</b> {b_fluid_vol_needed:.0f} ml (เพื่อให้ได้ {refeeding_kcal:.0f} kcal)</p>
            <p style='font-size:18px;'>• <b>Infusion Rate: <span style='color:#2196f3;'>{b_fluid_rate_int} ml/hr</span></b> (continuous 24 hrs)</p>
            <p style='font-size:0.85em; color:gray;'>*หมายเหตุ: ปรับเป็นจำนวนเต็มตามเป้าหมาย Hypocaloric 10 kcal/kg/day</p></div>""", unsafe_allow_html=True)

        if st.checkbox(f"ใช้ค่า Hypocaloric ({refeeding_kcal:.0f} kcal) ในการคำนวณวันนี้", value=True):
            target_kcal = refeeding_kcal

    st.markdown(f"""<div class="target-box"><h4 style='margin:0; color:#2196f3;'>🎯 Final Targets</h4>
        <p style='margin:5px 0 0 0;'><b>Energy:</b> {target_kcal:.0f} kcal/day | <b>Protein:</b> {target_pro:.1f} g/day</p></div>""", unsafe_allow_html=True)

    # --- PN Database & Selection ---
    df_bags = pd.DataFrame([
        {"Name": "B-fluid", "Type": "Peripheral", "Volume": 1000, "Kcal": 480, "Protein": 30, "Lipid": 0},
	{"Name": "Oliclinamel N4-1500", "Type": "Peripheral", "Volume": 1500, "Kcal": 910, "Protein": 33, "Lipid": 30},
        {"Name": "Oliclinamel N4-2000", "Type": "Peripheral", "Volume": 2000, "Kcal": 1215, "Protein": 44, "Lipid": 40},
        {"Name": "Oliclinamel N7-1000", "Type": "Central", "Volume": 1000, "Kcal": 1200, "Protein": 40, "Lipid": 40},
        {"Name": "Oliclinamel N7-1500", "Type": "Central", "Volume": 1500, "Kcal": 1800, "Protein": 60, "Lipid": 60},
        {"Name": "Oliclinamel N7-2000", "Type": "Central", "Volume": 2000, "Kcal": 2400, "Protein": 80, "Lipid": 80},
        {"Name": "SmofKabiven Peri-1500", "Type": "Peripheral", "Volume": 1500, "Kcal": 1100, "Protein": 45, "Lipid": 46},
        {"Name": "SmofKabiven Peri-1900", "Type": "Peripheral", "Volume": 1904, "Kcal": 1400, "Protein": 57, "Lipid": 60},
        {"Name": "SmofKabiven Central-1000", "Type": "Central", "Volume": 1012, "Kcal": 1100, "Protein": 51, "Lipid": 38},
        {"Name": "SmofKabiven Central-1500", "Type": "Central", "Volume": 1477, "Kcal": 1600, "Protein": 75, "Lipid": 56},
        {"Name": "SmofKabiven Central-2000", "Type": "Central", "Volume": 1970, "Kcal": 2200, "Protein": 100, "Lipid": 75}, 
        {"Name": "Nutriflex Lipid Peri-1250", "Type": "Peripheral", "Volume": 1250, "Kcal": 955, "Protein": 40, "Lipid": 50},
        {"Name": "Nutriflex VR-1250", "Type": "Central", "Volume": 1250, "Kcal": 1475, "Protein": 72, "Lipid": 50}
    ])

    available_bags = df_bags[(route == "Central Line") | (df_bags['Type'] == "Peripheral")]
    selected_pn_name = st.selectbox("เลือกชนิด PN:", available_bags['Name'].tolist())
    pn_info = available_bags[available_bags['Name'] == selected_pn_name].iloc[0]

    num_bags = st.number_input("จำนวนถุงต่อวัน:", min_value=0.1, max_value=5.0, value=float(round(target_kcal/pn_info['Kcal'], 1)), step=0.1)
    
    # Base calculation for UI initialization
    pn_pro_base = pn_info['Protein']*num_bags
    pn_vol_base = pn_info['Volume']*num_bags

    add_amiparen, amiparen_vol = False, 0
    if pn_pro_base < target_pro:
        st.info(f"💡 ยังขาดโปรตีนอีก {target_pro - pn_pro_base:.1f} g")
        add_amiparen = st.checkbox("➕ เสริม 10% Amiparen")
        if add_amiparen:
            amiparen_vol = st.number_input("Amiparen Volume (ml):", min_value=10, value=math.ceil((target_pro-pn_pro_base)*10), step=10)

    # --- INFUSION CONTROLLER ---
    st.markdown('<div class="infusion-control">', unsafe_allow_html=True)
    infusion_hours = st.slider("ระยะเวลาที่ให้ (Hours):", 12, 24, 24)
    col_r1, col_r2 = st.columns(2)
    final_rate = col_r1.number_input("PN Infusion Rate (ml/hr):", value=round(pn_vol_base/infusion_hours))
    final_ami_rate = col_r2.number_input("Amiparen Rate (ml/hr):", value=round(amiparen_vol/infusion_hours)) if add_amiparen else 0
    st.markdown('</div>', unsafe_allow_html=True)

    # --- DYNAMIC CALCULATION BASED ON RATE ---
    actual_pn_vol = final_rate * infusion_hours
    actual_ami_vol = final_ami_rate * infusion_hours if add_amiparen else 0
    
    # Get nutrients per ml
    kcal_per_ml = pn_info['Kcal'] / pn_info['Volume']
    pro_per_ml = pn_info['Protein'] / pn_info['Volume']
    lipid_per_ml = pn_info['Lipid'] / pn_info['Volume']

    # Actual Delivered
    delivered_kcal = (actual_pn_vol * kcal_per_ml) + (actual_ami_vol * 0.4) # Amiparen 10% has ~0.4 kcal/ml
    delivered_pro = (actual_pn_vol * pro_per_ml) + (actual_ami_vol * 0.1)
    delivered_vol = actual_pn_vol + actual_ami_vol
    delivered_lipid = (actual_pn_vol * lipid_per_ml)

# --- 4. VITAMIN & TRACE ELEMENTS ---
    is_central_line = (route == "Central Line")
    c_v1, c_v2, c_v3, c_v4 = st.columns(4)

    with c_v4:
        # Vitamin B complex: ให้ได้ทั้ง Central และ Peripheral line
        add_b_complex = st.checkbox("Vitamin B complex")
        b_complex_vials = 0
        if add_b_complex:
            b_complex_vials = st.selectbox("จำนวน (vials):", [1, 2], key="b_vial")
            st.info("**B-complex:** ให้ได้ทุก Access Route")

    with c_v1:
        # Soluvit: เฉพาะ Central line
        add_soluvit = st.checkbox("Soluvit 1 vial", disabled=not is_central_line)
        if add_soluvit: st.warning("**Soluvit Caution:** Hypersensitivity, Hemochromatosis, Hyperoxaluria/Stones")
        elif not is_central_line: st.caption("🚫 เฉพาะ Central line")

    with c_v2:
        # Vitalipid: เฉพาะ Central line
        add_vitalipid = st.checkbox("Vitalipid 1 vial", disabled=not is_central_line)
        if add_vitalipid: st.warning("**Vitalipid Caution:** Soybean/Egg allergy, Hypervitaminosis A,D,E, Jaundice, Liver cholestasis")
        elif not is_central_line: st.caption("🚫 เฉพาะ Central line")

    with c_v3:
        # Addamel: เฉพาะ Central line
        add_addamel = st.checkbox("Addamel 1 vial", disabled=not is_central_line)
        if add_addamel: st.warning("**Addamel Caution:** Wilson’s disease, Hemochromatosis, Biliary obstruction, Parkinsonism risk")
        elif not is_central_line: st.caption("🚫 เฉพาะ Central line")

    st.divider()

    # ส่วน Electrolytes: เฉพาะ Central line เท่านั้น
    if is_central_line:
        st.subheader("Electrolytes (mEq/L) - Central Line Only")
        c_e1, c_e2 = st.columns(2)
        with c_e1:
            kcl_val = st.number_input("KCl (mEq/L):", min_value=0.0, step=1.0, value=0.0)
        with c_e2:
            k2po4_val = st.number_input("K2PO4 (mEq/L):", min_value=0.0, step=1.0, value=0.0)
    else:
        kcl_val = k2po4_val = 0.0
        st.info("ℹ️ ส่วนประกอบ KCl และ K2PO4 จะเปิดให้ระบุเมื่อเลือก Central Line")

# --- 5. PHYSICIAN SIGNATURE ---
    st.header("5. Physician Signature")
    col_p1, col_p2 = st.columns(2)

    with col_p1:
        physician_1 = st.text_input("แพทย์ผู้สั่งการรักษา :", placeholder="พิมพ์ชื่อ-นามสกุล แพทย์")

    with col_p2:
    # ปรับเป็น selectbox สำหรับเลือกแพทย์ผู้ตรวจสอบ
        physician_options = [
        "นพ.บุลากร จันหฤทัย ว.62323",
        "นพ.บำรุง ผิวสวย ว.12345"
    ]
    physician_2 = st.selectbox("แพทย์ผู้ตรวจสอบ :", options=physician_options)


    # --- SUMMARY ---
    st.divider()
    st.markdown("### 📊 Summary (Calculated from Actual Rate)")
    sum_col1, sum_col2, sum_col3 = st.columns(3)
    sum_col1.metric("Delivered PN Rate", f"{final_rate} ml/hr", f"Total: {actual_pn_vol:.0f} ml")
    sum_col1.metric("Actual Energy", f"{delivered_kcal:.0f} kcal", f"Target: {target_kcal:.0f}")
    
    sum_col2.metric("Delivered 10% Amiparen Rate", f"{final_ami_rate} ml/hr", f"Total: {actual_ami_vol:.0f} ml")
    sum_col2.metric("Actual Protein", f"{delivered_pro:.1f} g", f"Target: {target_pro:.1f}")
    
    sum_col3.metric("Total Volume", f"{delivered_vol:.0f} ml", f"Limit: {fluid_limit} ml")
    
    # Lipid Safety
    actual_lipid_rate = (final_rate * lipid_per_ml) / weight
    sum_col3.metric("Lipid Infusion Rate", f"{actual_lipid_rate:.3f} g/kg/hr", "Max 0.11")

    if actual_lipid_rate > 0.11: st.error(f"🚨 Lipid Rate ({actual_lipid_rate:.3f}) > 0.11 g/kg/hr!")
    if delivered_vol > fluid_limit: st.error(f"⚠️ Volume ({delivered_vol:.0f}ml) > Limit ({fluid_limit}ml)")

    # --- 5. REPORT GENERATION ---
    st.divider()
    if st.button("📄 Generate PDF Report (A4)"):
        # ทุกบรรทัดด้านล่างนี้ต้องย่อหน้า (Indent) เข้ามาภายใต้ if
        inds = []
        if c1: inds.append("Malnutrition/Risk")
        if c2: inds.append("Inadequate intake <60%")
        if c3: inds.append("Stable Hemodynamic")
        if c4: inds.append("Not End-of-life")

        # เตรียมรายละเอียดความเสี่ยง Refeeding
        rf_details = []
        if rf_a1: rf_details.append("BMI < 16")
        if rf_a2: rf_details.append("Weight loss > 15%")
        if rf_a3: rf_details.append("Starvation > 10 days")
        if rf_a4: rf_details.append("Low electrolytes")
        if rf_b1: rf_details.append("BMI < 18.5")
        if rf_b2: rf_details.append("Weight loss > 10%")
        if rf_b3: rf_details.append("Starvation > 5 days")
        if rf_b4: rf_details.append("Alcohol/Drugs history")

        # จัดเตรียมข้อมูลสำหรับส่งเข้าฟังก์ชัน PDF
        report_data = {
            "name": name,"age": age, "ward": ward, "weight": weight, "height": height, "bmi": bmi, "ibw": ibw,
            "indications": inds, "en_contra": e_list,
            "naf_score": st.session_state.naf_score_total, "naf_cat": st.session_state.naf_category,
            "mal_level": mal_level, "is_refeeding": is_refeeding_risk, "refeeding_details": rf_details,
            "target_kcal": target_kcal, "target_pro": target_pro, "fluid_limit": fluid_limit,
            "pn_name": selected_pn_name, "final_rate": final_rate, "final_ami_rate": final_ami_rate,
            "hours": infusion_hours, "actual_pn_vol": actual_pn_vol, "actual_ami_vol": actual_ami_vol,
            "add_amiparen": add_amiparen, "delivered_kcal": delivered_kcal, "delivered_pro": delivered_pro,
            "delivered_vol": delivered_vol, "actual_lipid_rate": actual_lipid_rate,
            "soluvit": add_soluvit, "vitalipid": add_vitalipid, "addamel": add_addamel, "b_complex": b_complex_vials,
            "kcl": kcl_val, "k2po4": k2po4_val,
            "physician_1": physician_1 if physician_1 else "(......................................................)",
            "physician_2": physician_2, 
        }
        
        # เรียกสร้าง PDF และสร้างปุ่มดาวน์โหลด
        pdf_bytes = create_pdf_report(report_data)
        if pdf_bytes:
            st.download_button(
                label="💾 Download TPN Report",
                data=bytes(pdf_bytes),
                file_name=f"TPN_Report_{name}.pdf",
                mime="application/pdf"
            )

        else:
            st.warning("⚠️ โปรดประเมิน NAF และยืนยัน Indication ก่อนเริ่ม")

        st.divider()
        st.caption(f"Support Tool: {name} | IBW: {ibw} kg | BMI: {bmi:.1f}")