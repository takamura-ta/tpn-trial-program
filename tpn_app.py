import streamlit as st
import pandas as pd
import math
from fpdf import FPDF
import os

# --- 1. ประกาศค่าเริ่มต้น (Global) เพื่อป้องกัน NameError ตั้งแต่เปิดแอป ---
if 'naf_score' not in st.session_state:
    st.session_state.naf_score = 0
if 'pdf_output' not in st.session_state:
    st.session_state.pdf_output = None

# ดึงค่าจาก session_state มาใส่ตัวแปรปกติเพื่อใช้งานง่าย
naf_score = st.session_state.naf_score
name = "-"
ibw = 0.0
bmi = 0.0
pdf_output = st.session_state.pdf_output
report_data = {}

# --- 2. FUNCTION: CREATE PDF REPORT ---
def create_pdf_report(data):
    try:
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(current_dir, 'THSarabunNew.ttf')
        font_bold_path = os.path.join(current_dir, 'THSarabunNew_Bold.ttf')

        # เช็คว่ามีไฟล์ฟอนต์จริงไหม
        if not os.path.exists(font_path) or not os.path.exists(font_bold_path):
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(190, 10, "Error: Thai Font not found (.ttf)", 0, 1, 'C')
	
            return bytes(pdf.output())

        # โหลดฟอนต์
        pdf.add_font('THSarabun', '', font_path)
        pdf.add_font('THSarabun', 'B', font_bold_path)
        font_main = 'THSarabun'
        
        pdf.set_font(font_main, 'B', 20)
        pdf.add_page()

        # --- ส่วนเนื้อหา PDF ---
        pdf.cell(190, 10, "รายงานแผนการให้โภชนบำบัดทางหลอดเลือดดำ (TPN Report)", 0, 1, 'C')
        pdf.set_font(font_main, '', 13)
        pdf.cell(190, 6, f"Report Date: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, 'R')
        pdf.line(10, 28, 200, 28)
        pdf.ln(6)

        # 1. ข้อมูลผู้ป่วย
        pdf.set_font(font_main, 'B', 15)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(190, 9, " 1. ข้อมูลผู้ป่วย (Patient Information)", 0, 1, 'L', True)
        pdf.set_font(font_main, '', 14)
        pdf.ln(2)
        pdf.set_x(15)
        pdf.cell(63, 8, f"ชื่อ: {data.get('name', '-')}", 0, 0)
        pdf.cell(63, 8, f"อายุ: {data.get('age', '-')} ปี", 0, 0)
        pdf.cell(64, 8, f"หอผู้ป่วย: {data.get('ward', '-')}", 0, 1)
        pdf.set_x(15)
        pdf.cell(63, 8, f"น้ำหนัก: {data.get('weight', 0)} kg", 0, 0)
        pdf.cell(63, 8, f"IBW/AdjBW: {data.get('ibw', 0):.1f} / {data.get('adj_bw', 0):.1f} kg", 0, 0) # เพิ่ม AdjBW
        pdf.cell(64, 8, f"BMI: {data.get('bmi', 0):.1f} kg/m2", 0, 1)
        comorb_list = data.get('comorbidities', [])
        if comorb_list:
            pdf.set_x(15)
            pdf.multi_cell(180, 7, f"ภาวะโรคร่วม: {', '.join(comorb_list)}", 0, 'L')

        # 2. ผลการประเมินและข้อบ่งชี้
        pdf.ln(5)
        pdf.set_font(font_main, 'B', 15)
        pdf.cell(190, 9, " 2. ผลการประเมินและข้อบ่งชี้", 0, 1, 'L', True)
        pdf.set_font(font_main, '', 14)
        pdf.ln(2)
        
        pdf.set_x(15)
        pdf.cell(0, 8, f"ระดับความรุนแรง: {data.get('mal_level', '-')}", 0, 1)
        
        pdf.set_x(15)
        pdf.cell(0, 8, f"คะแนน NAF: {data.get('naf_score', 0)} ({data.get('naf_cat', '-')})", 0, 1)
        
        # แสดงระดับความเสี่ยง Refeeding
        is_high_risk = data.get('is_refeeding') == "High Risk"
        risk_text = f"ความเสี่ยง Refeeding: {data.get('is_refeeding', '-')}"
        pdf.set_x(15)
        if is_high_risk:
            pdf.set_text_color(200, 0, 0)  # เปลี่ยนสีเป็นสีแดงถ้าเสี่ยงสูง
        pdf.cell(0, 8, risk_text, 0, 1)
        pdf.set_text_color(0, 0, 0)    # กลับมาเป็นสีดำปกติ

        # ดึงรายละเอียดที่ถูกเลือกออกมาแสดง
        rf_details = data.get('refeeding_details', [])
        if rf_details:
            pdf.set_x(20) # ขยับเข้าไปเป็น bullet
            detail_str = "ความเสี่ยง: " + ", ".join(rf_details)
            # ใช้ multi_cell เพื่อให้ตัดบรรทัดอัตโนมัติหากข้อความยาวเกินไป
            pdf.multi_cell(170, 7, detail_str, 0, 'L')
        
        # แสดงข้อบ่งชี้ PN (Indications) เพิ่มเติมเพื่อให้ครบถ้วน
        inds = data.get('indications', [])
        if inds:
            pdf.set_x(15)
            pdf.cell(0, 8, f"ข้อบ่งชี้ในการให้ PN: {', '.join(inds)}", 0, 1)

        # แสดง EN Contraindications (ถ้ามี)
        en_contra = data.get('en_contra', [])
        if en_contra:
            pdf.set_x(15)
            # ใช้ multi_cell เพราะข้อห้าม EN มักจะมีหลายข้อและชื่อยาว
            pdf.set_text_color(200, 0, 0) # ใช้สีแดงเข้มเพื่อระบุเป็นข้อห้าม/ปัญหา
            pdf.multi_cell(180, 7, f"ข้อห้ามในการให้ EN (Contraindications): {', '.join(en_contra)}", 0, 'L')
            pdf.set_text_color(0, 0, 0) # กลับเป็นสีดำปกติ

        # แสดงเป้าหมายสารอาหาร (Nutritional Target Setting)
        pdf.set_x(15)
        pdf.set_font(font_main, 'B', 14)
        pdf.cell(0, 8, "เป้าหมายสารอาหาร (Nutritional Target Setting):", 0, 1)
        pdf.set_font(font_main, '', 14)
        
        # ดึงค่าเป้าหมายจาก data dictionary
        t_kcal = data.get('target_kcal', 0)
        t_pro = data.get('target_pro', 0)
        f_limit = data.get('fluid_limit', 0)
        
        pdf.set_x(20)
        pdf.cell(0, 8, f"• Energy Target: {data.get('target_kcal', 0):.0f} kcal/day", 0, 1)
        pdf.set_x(20)

        pdf.cell(0, 8, f"• Protein Target: {data.get('pro_display', '-')}", 0, 1)
        pdf.set_x(20)
        pdf.cell(0, 8, f"• Fluid Limit: {f_limit:.0f} ml/day", 0, 1)

        # 3. แผนการให้สารอาหาร (PN Order)
        pdf.ln(5)
        pdf.set_font(font_main, 'B', 15)
        pdf.cell(190, 9, " 3. รายละเอียดแผนการให้สารอาหาร (PN Order)", 0, 1, 'L', True)
        pdf.set_font(font_main, '', 14)

        # --- ต้องมีก้อนนี้ก่อนเริ่มวาดตาราง ---
        # 1. เตรียมข้อมูล Vitamins
        vits_list = []
        if data.get('soluvit'): vits_list.append("Soluvit")
        if data.get('vitalipid'): vits_list.append("Vitalipid")
        if data.get('addamel'): vits_list.append("Addamel")
        b_vials = data.get('b_complex', 0)
        if b_vials > 0: vits_list.append(f"B-complex ({b_vials})")
        
        has_vitamins = len(vits_list) > 0

        # 2. เตรียมข้อมูล Electrolytes
        kcl = data.get('kcl', 0)
        k2po4 = data.get('k2po4', 0)
        elec_str = []
        if kcl > 0: elec_str.append(f"KCl {kcl}")
        if k2po4 > 0: elec_str.append(f"K2PO4 {k2po4}")
        
        # --- เปลี่ยนจากข้อความธรรมดาเป็นรูปแบบตาราง (Table Style) ---
        pdf.ln(2)
        pdf.set_x(15)
        
        # ตั้งค่าสีหัวตาราง (เขียวอ่อนตามธีมแอป)
        pdf.set_fill_color(230, 245, 230) 
        pdf.set_font(font_main, 'B', 13)
        
        # ส่วนประกอบตาราง (Header)
        pdf.cell(95, 8, " รายการ (Item Description)", 1, 0, 'C', True)
        pdf.cell(85, 8, " รายละเอียดการบริหารยา (Specification)", 1, 1, 'C', True)
        
        # คืนค่าฟอนต์ปกติสำหรับเนื้อหา
        pdf.set_font(font_main, '', 13)
        
        # บรรทัดที่ 1: ชนิด PN
        pdf.set_x(15)
        pdf.cell(95, 8, f" PN: {data.get('pn_name', '-')}", 1, 0, 'L')
        pdf.cell(85, 8, f" {data.get('final_rate', 0)} ml/hr (Total {data.get('hours', 0)} hrs)", 1, 1, 'L')
        
        # บรรทัดที่ 2: Amiparen (ถ้ามี)
        if data.get('add_amiparen'):
            pdf.set_x(15)
            pdf.cell(95, 8, " Supplement: Amiparen 10%", 1, 0, 'L')
            pdf.cell(85, 8, f" {data.get('final_ami_rate', 0)} ml/hr", 1, 1, 'L')
            
        # บรรทัดที่ 3: Vitamins (ถ้ายุบรวมกันจะประหยัดที่มาก)
        if has_vitamins:
            v_text = ", ".join(vits_list)
            pdf.set_x(15)
            pdf.cell(95, 8, " Vitamins & Trace Elements", 1, 0, 'L')
            # ใช้พิกัด x,y ช่วยกรณีข้อความยาว (หรือใช้ cell ปกติถ้าสั้น)
            pdf.cell(85, 8, f" {v_text[:45]}{'...' if len(v_text)>45 else ''}", 1, 1, 'L')
            
        # บรรทัดที่ 4: Electrolytes
        if kcl > 0 or k2po4 > 0:
            e_text = " / ".join(elec_str)
            pdf.set_x(15)
            pdf.cell(95, 8, " Electrolytes Supplement", 1, 0, 'L')
            pdf.cell(85, 8, f" {e_text}", 1, 1, 'L')

        # เพิ่มเส้นใต้ตารางเล็กน้อย
        pdf.ln(4)

        # 4. สารอาหารที่ได้รับจริง (Actual Delivered)
        pdf.ln(5)
        pdf.set_font(font_main, 'B', 15)
        pdf.cell(190, 9, " 4. สรุปสารอาหารที่ได้รับจริง (Actual Delivered)", 0, 1, 'L', True)
        pdf.set_font(font_main, '', 14)
        pdf.ln(2)
        pdf.set_x(15)
        pdf.cell(63, 8, f"Energy: {data.get('delivered_kcal', 0):.0f} kcal", 0, 0)
        pdf.cell(63, 8, f"Protein: {data.get('delivered_pro', 0):.1f} g", 0, 0)
        pdf.cell(64, 8, f"Volume: {data.get('delivered_vol', 0):.0f} ml", 0, 1)

        # 6. ส่วน Signature Section
        signature_y = 260 
        pdf.set_y(signature_y)
        pdf.set_font(font_main, 'B', 14)
        p1_name = data.get('physician_1', "").strip() or ".........................."
        p2_name = data.get('physician_2', "").strip() or ".........................."
        
        pdf.set_x(15)
        pdf.multi_cell(85, 7, f"( {p1_name} )\nแพทย์ผู้สั่งการรักษา", 0, 'C')
        pdf.set_xy(110, signature_y)
        pdf.multi_cell(85, 7, f"( {p2_name} )\nแพทย์ผู้ตรวจสอบ/ผู้ให้คำปรึกษา", 0, 'C')

        # --- บรรทัดที่สำคัญมาก: การ Output ข้อมูล ---
        pdf_bytes = pdf.output()
        if isinstance(pdf_bytes, str): 
            return pdf_bytes.encode('latin-1')
        return bytes(pdf_bytes)

    except Exception as e:
        # เปลี่ยนจาก print(f"PDF Error: {e}") เป็น st.error ด้านล่าง
        st.error(f"รายละเอียดข้อผิดพลาดทางเทคนิค: {e}")
        return None

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

st.sidebar.divider()
st.sidebar.header("3. Clinical Condition")
comorbidities = st.sidebar.multiselect(
    "ภาวะโรคร่วม (Diseases & Co-morbidities):",
    options=[
        "Acute kidney injury (AKI)",
        "Cancer",
        "Cirrhosis",
        "Intermittent hemodialysis",
        "CRRT",
        "Peritoneal dialysis (PD)",
        "Infected PD",
        "Burn",
        "Traumatic brain injury (TBI)",
        "Protein Losing Enteropathy (PLE)"
    ]
)

# --- BASELINE MATH ---
if gender == "ชาย":
    ibw = (height - 105) * 0.9 # สูตร IBW มาตรฐาน (หรือใช้ค่าที่คุณต้องการ)
else:
    ibw = (height - 100) * 0.9

# 2. Body Mass Index (BMI)
bmi = weight / ((height/100)**2)

# 3. Adjusted Body Weight (AdjBW)
# สูตร: Adjusted BW = Ideal BW + 0.33 * (Actual BW - Ideal BW)
adj_bw = ibw + 0.33 * (weight - ibw)

rf_m1 = rf_m2 = rf_m3 = rf_m4 = False
rf_min1 = rf_min2 = rf_min3 = rf_min4 = False
rf_vh1 = False
refeed_level = "No Risk"
is_refeeding_risk = False
target_kcal = 0.0 
pro_display = "-"

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
    diseases_high = st.multiselect("กลุ่มโรค 6 คะแนน:", ["Stroke/CVA", "Severe Pneumonia", "Multiple fracture", "Hematologic malignancy", "Critically ill"])
    diseases_mid = st.multiselect("กลุ่มโรค 3 คะแนน:", ["DM", "CKD-ESRD", "Cirrhosis/Hepatic encephalopathy", "Solid cancer", "Chronic heart failure", "Severe head injury", "Hip fracture", "COPD", ">2º of burn", "Septicemia"])

    if st.button("คำนวณและบันทึกคะแนน Mod.NAF"):
        sc7 = (len(diseases_high) * 6) + (len(diseases_mid) * 3)
        p5 = len(sc5_1) * 2
        total = int(sc1_1[0]) + bmi_p + int(sc2[0]) + int(sc3[0]) + int(sc4_1[0]) + int(sc4_2[0]) + p5 + int(sc6[0]) + sc7
        st.session_state.naf_score_total = total
        st.session_state.naf_category = "A" if total <= 5 else ("B" if total <= 14 else "C")
        st.success(f"ประเมินสำเร็จ! คะแนนโรค: {sc7} | คะแนนรวม: {total}")

# --- ผลสรุปเบื้องต้น & คำแนะนำ ---
c_res1, c_res2, c_res3, c_res4 = st.columns(4)
with c_res1: st.metric("BMI", f"{bmi:.1f}")
with c_res2: st.metric("Ideal BW (kg)", f"{ibw:.1f}")
with c_res3: st.metric("Adj. BW (kg)", f"{adj_bw:.1f}")
with c_res4: st.metric("Mod.NAF Category", st.session_state.naf_category)

# ดึงค่า NAF Category มาใช้งาน
naf_cat = st.session_state.naf_category

# ปรับ Logic ใหม่: ใช้แค่ BMI และ NAF Category
if (bmi < 16 or naf_cat == "C"):
    mal_level, sev_color = "Severe", "red"
    rec_text = "หากไม่สามารถให้ EN ได้ แนะนำเริ่มให้อาหารทางหลอดเลือดดำทันที"
elif (16 <= bmi <= 16.99 or naf_cat == "B"):
    mal_level, sev_color = "Moderate", "orange"
    rec_text = "หากไม่สามารถให้ EN ได้ แนะนำเริ่มให้อาหารทางหลอดเลือดดำภายใน 3-5 วัน"
else:
    mal_level, sev_color = "Normal/Mild", "blue"
    rec_text = "หากไม่สามารถให้ EN ที่เพียงพอหลังวันที่ 7 แนะนำเริ่มให้อาหารทางหลอดเลือดดำ"

st.subheader(f"ระดับความรุนแรง: :{sev_color}[{mal_level} Malnutrition]")
st.markdown(f"""<div style="padding: 10px; border-radius: 5px; background-color: rgba(0,0,0,0.05); border-left: 5px solid {sev_color};">
    <p style="margin:0; font-weight:bold; color:{sev_color};">📌 คำแนะนำทางคลินิก:</p><p style="margin:0;">{rec_text}</p></div>""", unsafe_allow_html=True)
st.divider()

# --- 2. INDICATION ---
st.header("2. Indication for PN")
with st.expander("ตรวจสอบข้อบ่งชี้", expanded=True):
    c1 = st.checkbox("ทุพโภชนาการ/เสี่ยงระดับปานกลางขึ้นไป")
    c2 = st.checkbox("ได้รับอาหาร < 60% ของเป้าหมาย")
    c3 = st.checkbox("ไม่ใช่ระยะสุดท้าย")
    e_list = st.multiselect("EN Contraindications:", ["Hemodynamic instability (Shock index(HR/SBP)>1, Vasopressor >0.3-0.5 mcg/kg/min, MAP <50 mmHg)", "Mechanical Obstruction", "Impaired Absorption", "Severe Ileus", "Bowel Rest", "Abdominal Compartment Syndrome", "ไม่สามารถใส่สายให้อาหารเข้าทางเดินอาหารได้"])

is_ready = all([c1, c2, c3]) and len(e_list) > 0

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
        
        calc_bw = weight if bmi < 30 else adj_bw
        # กำหนดช่วงโปรตีนเริ่มต้น (Baseline)
        low_ratio, high_ratio = 1.2, 1.5 
        
        # ปรับค่า Ratio ตามโรคที่เลือก (Multi-select)
        if "Acute kidney injury (AKI)" in comorbidities:
            low_ratio, high_ratio = 1.0, 1.2
        if any(x in comorbidities for x in ["Cirrhosis", "Cancer", "Intermittent hemodialysis"]):
            low_ratio, high_ratio = 1.2, 1.5
        if "CRRT" in comorbidities:
            low_ratio, high_ratio = 1.5, 1.7
        if "Burn" in comorbidities:
            low_ratio, high_ratio = 1.2, 2.0
        if "Traumatic brain injury (TBI)" in comorbidities:
            low_ratio, high_ratio = 1.5, 2.5
        if "Protein Losing Enteropathy (PLE)" in comorbidities:
            low_ratio, high_ratio = 3.0, 3.0 # ค่าเดียว

        # คำนวณเป็นค่า Range
        p_low = calc_bw * low_ratio
        p_high = calc_bw * high_ratio
        
        # จัดรูปแบบการแสดงผล (ถ้าค่าเท่ากันให้โชว์เลขเดียว)
        if p_low == p_high:
            pro_display = f"{p_low:.1f} g/day"
            target_pro = p_low # ใช้ค่านี้คำนวณต่อ
        else:
            pro_display = f"{p_low:.1f} - {p_high:.1f} g/day"
            target_pro = p_high # ใช้ค่า Max ในการตั้งเป็นเป้าหมายในเครื่องมือคำนวณ
            
        st.session_state.pro_display = pro_display # เก็บไว้โชว์ใน PDF

    else:
        col_m1, col_m2 = st.columns(2)
        target_kcal = col_m1.number_input("Energy (kcal/day):", value=2000.0, step=50.0)
        target_pro = col_m2.number_input("Protein (g/day):", value=80.0, step=5.0)

# --- 3.1 REFEEDING RISK ASSESSMENT (Latest Update) ---
    st.subheader("Refeeding Syndrome Risk Assessment")
    with st.expander("🔍 แบบทดสอบความเสี่ยงภาวะ Refeeding syndrome", expanded=True):
        col_rf1, col_rf2 = st.columns(2)
        
        with col_rf1:
            st.markdown("**[Major Criteria]**")
            rf_m1 = st.checkbox("BMI < 16.5 kg/m²", value=(bmi < 16.5))
            rf_m2 = st.checkbox("น้ำหนักลดโดยไม่ตั้งใจ > 15% ใน 3-6 เดือน")
            rf_m3 = st.checkbox("กินอาหารน้อยมาก/ไม่ได้เลย > 10 วัน")
            rf_m4 = st.checkbox("K, PO4 หรือ Mg ในเลือดต่ำก่อนเริ่ม")

        with col_rf2:
            st.markdown("**[Minor Criteria]**")
            rf_min1 = st.checkbox("BMI < 18.5 kg/m²", value=(16.5 <= bmi < 18.5))
            rf_min2 = st.checkbox("น้ำหนักลดโดยไม่ตั้งใจ > 10% ใน 3-6 เดือน")
            rf_min3 = st.checkbox("กินอาหารน้อยมาก/ไม่ได้เลย > 5 วัน")
            rf_min4 = st.checkbox("ประวัติ Alcohol abuse / Insulin / Chemo / Diuretics")

        st.markdown("**[Very High Risk Criteria]**")
        rf_vh1 = st.checkbox("BMI < 14 kg/m² หรือ น้ำหนักลด > 20% หรือ Starvation > 15 วัน")

        # --- Logic การตัดสินระดับความเสี่ยง ---
        major_count = sum([rf_m1, rf_m2, rf_m3, rf_m4])
        minor_count = sum([rf_min1, rf_min2, rf_min3, rf_min4])

        if rf_vh1:
            refeed_level = "Very High Risk"
            start_kcal_rate = 5
        elif major_count >= 1 or minor_count >= 2:
            refeed_level = "High Risk"
            start_kcal_rate = 10
        elif minor_count == 1:
            refeed_level = "Intermediate Risk"
            start_kcal_rate = 15
        else:
            refeed_level = "No Risk"
            start_kcal_rate = 25

    # --- การจัดการตามระดับความเสี่ยง ---
    if refeed_level != "No Risk":
        refeeding_kcal = weight * start_kcal_rate
        color_map = {"Very High Risk": "#8b0000", "High Risk": "#ff4b4b", "Intermediate Risk": "#ffa500"}
        current_color = color_map.get(refeed_level, "#2e7d32")
        
        st.markdown(f"""
        <div style="padding:15px; border-radius:10px; background-color:rgba(255,0,0,0.05); border:2px solid {current_color};">
            <h4 style='margin:0; color:{current_color};'>⚠️ ระดับความเสี่ยง: {refeed_level}</h4>
            <p>• <b>พลังงานเริ่มต้น:</b> แนะนำ {refeeding_kcal:.0f} kcal/day ({start_kcal_rate} kcal/kg)</p>
            <p>• <b>ก่อนเริ่ม PN:</b> Correct electrolyte imbalance, ตรวจติดตามค่า Electrolyte  3 วันแรก และทุก 2-3 วัน, Thiamine 200-300 mg/day IV, Vitamin BCO</p>
        </div>
        """, unsafe_allow_html=True)

# --- 3.2 CALORIE TITRATION PLAN (ICU 7-Day Policy & Refeeding) ---
    if refeed_level != "No Risk":
        st.subheader("แผนการปรับเพิ่มพลังงาน (CALORIE TITRATION PLAN)")
        
        # 1. เช็คเงื่อนไข ICU Admission Day (เพิ่มตัวเลือกสำหรับ ICU)
        limit_70_permissive = False
        if location == "ICU":
            is_early_icu = st.checkbox("ICU Admission Day ≤ 7 วัน (ICU Early Phase)", value=True)
            if is_early_icu:
                limit_70_permissive = True
                st.info("ℹ️ ICU Early Phase: จำกัดพลังงานสูงสุดไม่เกิน 70% ของ Energy Goal")

        # 2. เลือกน้ำหนักที่จะใช้คำนวณ
        calc_bw_ref = weight if bmi < 30 else adj_bw

        # 3. กำหนดแผนตามระดับความเสี่ยง
        if refeed_level == "Very High Risk":
            steps = ["Step 1 (Day 1-3)", "Step 2 (Day 4-6)", "Step 3 (Day 7-9)", "Step 4 (Day 10+)"]
            ranges = ["5 - 10", "10 - 20", "20 - 30", "30 - 35"]
        elif refeed_level == "High Risk":
            steps = ["Step 1 (Day 1-3)", "Step 2 (Day 4-5)", "Step 3 (Day 6+)"]
            ranges = ["10 - 15", "15 - 25", "30 - 35"]
        else: # Intermediate Risk
            steps = ["Step 1 (Day 1-3)", "Step 2 (Day 4)", "Step 3 (Day 5+)"]
            ranges = ["15 - 25", "30", "30 - 35"]

        titration_summary = []
        for s, r_text in zip(steps, ranges):
            # แยกค่า Low/High จาก range text
            low_val = float(r_text.split(' - ')[0]) if ' - ' in r_text else float(r_text)
            high_val = float(r_text.split(' - ')[1]) if ' - ' in r_text else float(r_text)
            
            # --- Logic การปรับลด 70% สำหรับ ICU Early Phase ---
            if limit_70_permissive:
                low_val = low_val * 0.7
                high_val = high_val * 0.7
            
            # สร้างข้อความแสดงผลในตาราง
            if low_val == high_val:
                energy_range_str = f"{low_val * calc_bw_ref:.0f}"
                kcal_kg_str = f"{low_val:.1f}"
            else:
                energy_range_str = f"{low_val * calc_bw_ref:.0f} - {high_val * calc_bw_ref:.0f}"
                kcal_kg_str = f"{low_val:.1f} - {high_val:.1f}"

            titration_summary.append({
                "ลำดับขั้นตอน": s,
                "Target (kcal/kg)": f"{kcal_kg_str} kcal/kg",
                "Target Energy (kcal/day)": energy_range_str
            })

        # แสดงผลตาราง
        st.dataframe(pd.DataFrame(titration_summary), hide_index=True, use_container_width=True)
        st.session_state.titration_data = titration_summary

        # ปุ่มเลือกใช้ค่า Step 1 สำหรับวันนี้
        step1_low = float(titration_summary[0]["Target Energy (kcal/day)"].split(' - ')[0]) if ' - ' in titration_summary[0]["Target Energy (kcal/day)"] else float(titration_summary[0]["Target Energy (kcal/day)"])
        if st.checkbox(f"ใช้พลังงานตั้งต้น Step 1 ({step1_low:.0f} kcal) สำหรับวันนี้", value=True):
            target_kcal = step1_low

# --- การแสดงผล Final Targets (เพิ่มตัวเลือก 70% สำหรับ ICU) ---
    # 1. เตรียมค่าพื้นฐาน
    calc_bw_energy = weight if bmi < 30 else adj_bw
    e_low = calc_bw_energy * 25
    e_high = calc_bw_energy * 30
    
    # 2. ตรวจสอบเงื่อนไข ICU และการเลือกสัดส่วนพลังงาน
    use_70_percent = False
    if location == "ICU" and refeed_level == "No Risk":
        # แสดงตัวเลือกเฉพาะใน ICU และไม่มีความเสี่ยง Refeeding (เพราะ Refeeding จะถูกบังคับ Hypocaloric อยู่แล้ว)
        use_70_percent = st.checkbox("Use 70% Energy Target (ICU Permissive Underfeeding)", value=True)

    # 3. จัดการการแสดงผล Energy Display
    if refeed_level != "No Risk":
        energy_display = f"{target_kcal:.0f} kcal/day (Hypocaloric Goal)"
    else:
        if use_70_percent:
            e_low, e_high = e_low * 0.7, e_high * 0.7
            energy_display = f"{e_low:.0f} - {e_high:.0f} kcal/day (70% Target)"
        else:
            energy_display = f"{e_low:.0f} - {e_high:.0f} kcal/day"
            
        # อัปเดตค่า target_kcal (ค่าสูงสุดของช่วง) เพื่อใช้คำนวณในส่วนถัดไป
        target_kcal = e_high

    # 4. แสดงผลด้วย Markdown
    st.markdown(f"""
        <div class="target-box">
            <h4 style='margin:0; color:#2196f3;'>🎯 Final Targets</h4>
            <p style='margin:5px 0 0 0;'>
                <b>Energy goal:</b> {energy_display} | 
                <b>Protein goal:</b> {st.session_state.get('pro_display', '-')}
            </p>
        </div>
    """, unsafe_allow_html=True)

    # --- PN Database & Selection ---
    df_bags = pd.DataFrame([
        # --- Peripheral Line Bags ---
        {"Name": "B-fluid", "Type": "Peripheral", "Volume": 1000, "Kcal": 480, "Protein": 30, "Lipid": 0, "Glucose": 75},
        {"Name": "Oliclinamel N4-1500", "Type": "Peripheral", "Volume": 1500, "Kcal": 910, "Protein": 33, "Lipid": 30, "Glucose": 120},
        {"Name": "Oliclinamel N4-2000", "Type": "Peripheral", "Volume": 2000, "Kcal": 1215, "Protein": 44, "Lipid": 40, "Glucose": 160},
        {"Name": "SmofKabiven Peri-1448", "Type": "Peripheral", "Volume": 1448, "Kcal": 1000, "Protein": 46, "Lipid": 41, "Glucose": 103},
        {"Name": "SmofKabiven Peri-1904", "Type": "Peripheral", "Volume": 1904, "Kcal": 1300, "Protein": 60, "Lipid": 54, "Glucose": 135},
        {"Name": "Nutriflex Lipid Peri-1250", "Type": "Peripheral", "Volume": 1250, "Kcal": 955, "Protein": 40, "Lipid": 50, "Glucose": 80},
        {"Name": "Nutriflex Lipid Peri-1875", "Type": "Peripheral", "Volume": 1875, "Kcal": 1435, "Protein": 60, "Lipid": 75, "Glucose": 120},

        # --- Central Line Bags ---
        {"Name": "50% DW 500 ml", "Type": "Central", "Volume": 500, "Kcal": 850, "Protein": 0, "Lipid": 0, "Glucose": 250},
        {"Name": "Oliclinamel N7-1000", "Type": "Central", "Volume": 1000, "Kcal": 1200, "Protein": 40, "Lipid": 40, "Glucose": 160},
        {"Name": "Oliclinamel N7-1500", "Type": "Central", "Volume": 1500, "Kcal": 1800, "Protein": 60, "Lipid": 60, "Glucose": 240},
        {"Name": "Oliclinamel N7-2000", "Type": "Central", "Volume": 2000, "Kcal": 2400, "Protein": 80, "Lipid": 80, "Glucose": 320},
        {"Name": "SmofKabiven Central-986", "Type": "Central", "Volume": 986, "Kcal": 1100, "Protein": 50, "Lipid": 38, "Glucose": 125},
        {"Name": "SmofKabiven Central-1477", "Type": "Central", "Volume": 1477, "Kcal": 1600, "Protein": 75, "Lipid": 56, "Glucose": 187},
        {"Name": "SmofKabiven Central-1970", "Type": "Central", "Volume": 1970, "Kcal": 2200, "Protein": 100, "Lipid": 75, "Glucose": 250}, 
        {"Name": "Nutriflex Lipid VR-625", "Type": "Central", "Volume": 625, "Kcal": 740, "Protein": 36, "Lipid": 25, "Glucose": 90},
        {"Name": "Nutriflex Lipid VR-1250", "Type": "Central", "Volume": 1250, "Kcal": 1475, "Protein": 72, "Lipid": 50, "Glucose": 180},
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
    # GIR ---
    # 1. คำนวณ Glucose รวม (g) และ GIR (mg/kg/min)
    # สูตร GIR: (g Glucose * 1000) / (น้ำหนัก * นาทีที่ให้)
    delivered_cho = (actual_pn_vol * (pn_info['Glucose'] / pn_info['Volume']))
    current_gir = (delivered_cho * 1000) / (weight * infusion_hours * 60)
    current_gm_kg_day = delivered_cho / weight
    
    # 2. กำหนดเกณฑ์ Limit (ICU: 5, General: 7 mg/kg/min)
    max_gir = 5.0 if location == "ICU" else 7.0

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
        st.info("ℹ️ ส่วนประกอบ KCl และ K2PO4 จะเปิดให้ add ใน PN เมื่อเลือก Central Line")

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

    # แสดง GIR และสถานะความปลอดภัย
    status_g_color = "green" if current_gir <= max_gir else "red"
    st.markdown(f"**GIR:** :{status_g_color}[{current_gir:.2f} mg/kg/min] (Max {max_gir})")
    st.caption(f"Glucose Load: {current_gm_kg_day:.2f} g/kg/day")
    
    # Lipid Safety
    actual_lipid_rate = (final_rate * lipid_per_ml) / weight
    sum_col3.metric("Lipid Infusion Rate", f"{actual_lipid_rate:.3f} g/kg/hr", "Max 0.11")

    if current_gir > max_gir: 
        st.error(f"🚨 GIR ({current_gir:.2f}) สูงเกินเกณฑ์มาตรฐานสำหรับ {location}!")
    if actual_lipid_rate > 0.11: 
        st.error(f"🚨 Lipid Rate ({actual_lipid_rate:.3f}) > 0.11 g/kg/hr!")
    if actual_lipid_rate > 0.11: st.error(f"🚨 Lipid Rate ({actual_lipid_rate:.3f}) > 0.11 g/kg/hr!")
    if delivered_vol > fluid_limit: st.error(f"⚠️ Volume ({delivered_vol:.0f}ml) > Limit ({fluid_limit}ml)")

    # --- 5. REPORT GENERATION ---
st.divider()

# สร้างปุ่มสำหรับจัดเตรียมข้อมูล
if st.button("📄 Prepare Report & Generate PDF"):
    # 1. รวบรวมข้อมูล Indications
    inds = []
    if c1: inds.append("Malnutrition/Risk")
    if c2: inds.append("Inadequate intake <60%")
    if c3: inds.append("Not End-of-life")

    # 2. เตรียมรายละเอียดความเสี่ยง Refeeding
    rf_details = []
    if rf_vh1: rf_details.append("Very High Risk Criteria")
    if rf_m1: rf_details.append("BMI < 16.5")
    if rf_m2: rf_details.append("Weight loss > 15%")
    if rf_m3: rf_details.append("Starvation > 10 days")
    if rf_m4: rf_details.append("Low electrolytes")
    
    if rf_min1: rf_details.append("BMI < 18.5")
    if rf_min2: rf_details.append("Weight loss > 10%")
    if rf_min3: rf_details.append("Starvation > 5 days")
    if rf_min4: rf_details.append("Alcohol abuse/Insulin/Chemo/Diuretic history")

    # 3. จัดเตรียมข้อมูล (ใส่ข้อมูลให้ครบถ้วนใน dictionary)
    report_data = {
        "name": name, "age": age, "ward": ward, "weight": weight, "height": height, "bmi": bmi, "ibw": ibw, "adj_bw": adj_bw,
        "comorbidities": comorbidities,
        "indications": inds, "en_contra": e_list,
        "naf_score": st.session_state.naf_score_total, "naf_cat": st.session_state.naf_category,
        "mal_level": mal_level, "is_refeeding": refeed_level,
        "refeeding_details": rf_details,
        "target_kcal": target_kcal, "target_pro": target_pro, "pro_display": pro_display, "fluid_limit": fluid_limit,
        "pn_name": selected_pn_name, "final_rate": final_rate, "final_ami_rate": final_ami_rate,
        "hours": infusion_hours, "actual_pn_vol": actual_pn_vol, "actual_ami_vol": actual_ami_vol,
        "add_amiparen": add_amiparen, "delivered_kcal": delivered_kcal, "delivered_pro": delivered_pro,
        "delivered_vol": delivered_vol, "actual_lipid_rate": actual_lipid_rate, "current_gir": current_gir, "max_gir": max_gir, "current_gm_kg": current_gm_kg_day,
        "soluvit": add_soluvit, "vitalipid": add_vitalipid, "addamel": add_addamel, "b_complex": b_complex_vials,
        "kcl": kcl_val, "k2po4": k2po4_val,
        "physician_1": physician_1 if physician_1 else "....................",
        "physician_2": physician_2, 
    }

    # 4. สร้าง PDF และเก็บลง Session State เพื่อไม่ให้หายไปเมื่อกด Download
    pdf_content = create_pdf_report(report_data)
    if pdf_content:
        st.session_state.pdf_output = pdf_content
        st.success("✅ สร้างไฟล์ PDF สำเร็จ! โปรดกดปุ่มดาวน์โหลดด้านล่าง")
    else:
        st.error("❌ เกิดข้อผิดพลาดในการสร้าง PDF")

# --- 6. ส่วนแสดงปุ่มดาวน์โหลด (ต้องอยู่นอกปุ่ม Generate เพื่อให้แสดงค้างไว้ได้) ---
if st.session_state.pdf_output is not None:
    try:
        # บังคับแปลงจาก bytearray เป็น bytes ที่นี่อีกครั้งหนึ่ง
        # และใช้ BytesIO เพื่อให้ Streamlit อ่านข้อมูลได้แน่นอน
        from io import BytesIO
        download_data = BytesIO(st.session_state.pdf_output)
        
        st.download_button(
            label="💾 CLICK HERE TO DOWNLOAD PDF REPORT",
            data=download_data, # ส่งเป็น BytesIO object แทน
            file_name=f"TPN_Report_{name}.pdf",
            mime="application/pdf",
            key="download_pdf_final"
        )
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเตรียมไฟล์ดาวน์โหลด: {e}")
