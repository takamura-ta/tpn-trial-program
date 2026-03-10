[README.md.txt](https://github.com/user-attachments/files/25877699/README.md.txt)
# 🏥 Thai TPN Clinical Support System

แอปพลิเคชันสำหรับช่วยคำนวณและวางแผนการให้โภชนบำบัดทางหลอดเลือดดำ (Parenteral Nutrition) ให้สอดคล้องกับแนวทางเวชปฏิบัติของประเทศไทย (Thai JPEN 2019)

## 🌟 คุณสมบัติหลัก (Features)
- **Nutritional Assessment:** ประเมินภาวะโภชนาการด้วยแบบจำลอง Mod.NAF และ Nutrition Triage (NT 2013)
- **Automatic Target Calculation:** คำนวณเป้าหมายพลังงาน (Energy) และโปรตีน (Protein) ตามน้ำหนักตัวและสภาวะของผู้ป่วย (General Ward / ICU)
- **Refeeding Syndrome Screening:** ระบบคัดกรองความเสี่ยงตาม NICE Criteria พร้อมแนะนำแผนการให้แบบ Hypocaloric
- **PN Database:** รวบรวมข้อมูลสูตรสารอาหารสำเร็จรูปที่มีใช้ในประเทศไทย (เช่น Oliclinamel, SmofKabiven, Nutriflex)
- **Safety Checks:** ระบบแจ้งเตือนอัตโนมัติหาก Lipid Infusion Rate เกินเกณฑ์มาตรฐาน (0.11 g/kg/hr) หรือปริมาณน้ำเกินที่กำหนด
- **PDF Report:** ออกรายงานสรุปแผนการรักษา (Prescription) และบันทึกข้อมูลผู้ป่วยในรูปแบบไฟล์ PDF ที่สวยงามและพร้อมใช้งาน

## 🛠 การติดตั้ง (Installation)
หากต้องการรันแอปพลิเคชันนี้บนเครื่องคอมพิวเตอร์ของคุณเอง:

1. ติดตั้ง Python 3.9 ขึ้นไป
2. Clone โปรเจกต์นี้ลงในเครื่อง
3. ติดตั้ง Library ที่จำเป็น:
   ```bash
   pip install streamlit pandas fpdf
