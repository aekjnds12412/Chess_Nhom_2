from pathlib import Path
import json
import re
from html import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether

ROOT = Path(__file__).resolve().parents[3]
INPUT = ROOT / 'presentation/content_script.json'
OUT = ROOT / 'presentation/output/Kich_ban_va_phan_cong_Pixel_Chess.pdf'
d = json.loads(INPUT.read_text(encoding='utf-8'))
assert d['duration_minutes'] == 7, 'Await final 7-minute source'
slides = d['slides']
assert sum(s['duration_seconds'] for s in slides[:8]) == 420
for f,n in [('arial.ttf','Arial'), ('arialbd.ttf','Arial-Bold'), ('ariali.ttf','Arial-Italic')]:
    pdfmetrics.registerFont(TTFont(n, str(Path('C:/Windows/Fonts')/f)))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-Bold')

ST = {
 'title':ParagraphStyle('title',fontName='Arial-Bold',fontSize=21,leading=26,spaceAfter=12,textColor=colors.black),
 'h1':ParagraphStyle('h1',fontName='Arial-Bold',fontSize=16,leading=21,spaceBefore=6,spaceAfter=10,textColor=colors.black),
 'h2':ParagraphStyle('h2',fontName='Arial-Bold',fontSize=12.3,leading=17,spaceBefore=11,spaceAfter=5,textColor=colors.black),
 'body':ParagraphStyle('body',fontName='Arial',fontSize=10.7,leading=15.7,spaceAfter=7,textColor=colors.black),
 'small':ParagraphStyle('small',fontName='Arial',fontSize=9,leading=12.8,spaceAfter=5,textColor=colors.HexColor('#333333')),
 'cell':ParagraphStyle('cell',fontName='Arial',fontSize=9.5,leading=13,textColor=colors.black),
 'headcell':ParagraphStyle('headcell',fontName='Arial-Bold',fontSize=9.3,leading=12.7,textColor=colors.white),
 'quote':ParagraphStyle('quote',fontName='Arial',fontSize=10.7,leading=16.2,spaceAfter=8,leftIndent=0,rightIndent=0),
}
story=[]
def P(txt,style='body'):
    txt = re.sub('[\u2010-\u2015]', '-', str(txt))
    return Paragraph(escape(txt).replace('\n','<br/>'),ST[style])
def add(txt,style='body'):
    story.append(P(txt,style))
def h(txt): add(txt,'h1')
def hh(txt): add(re.sub(r'[?:]', '', txt),'h2')
def note(label,txt):
    txt = re.sub('[\u2010-\u2015]', '-', str(txt))
    label = re.sub('[\u2010-\u2015]', '-', str(label))
    story.append(Paragraph('<b>'+escape(label)+'</b> '+escape(txt).replace('\n','<br/>'),ST['body']))
def table(headers,rows,widths):
    data=[[P(v,'headcell') for v in headers]]+[[P(v,'cell') for v in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([
      ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#263B4A')),
      ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3F5F7')]),
      ('GRID',(0,0),(-1,-1),.5,colors.HexColor('#D9D9D9')),
      ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
      ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
      ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
    ]))
    story.append(t)
    story.append(Spacer(1,9))
def page(): story.append(PageBreak())
def timefmt(sec): return f'{sec//60:02d}:{sec%60:02d}'

# Page 1: roles and the exact timed running order.
add('Kịch bản thuyết trình Pixel Chess','title')
add('Cờ vua trực tuyến đa luồng kết hợp TCP và UDP', 'h2')
add('Tổng thời lượng 7 phút gồm 1 phút giới thiệu, 3 phút demo và 3 phút thảo luận. Nguyễn Trọng Trình thực hiện và thuyết minh toàn bộ demo. Các phần nói dưới đây giúp cả sáu thành viên tham gia đúng thời gian.')
hh('Phân công thành viên')
roles={
 'Nguyễn Trọng Trình':('Nhóm trưởng, demo','2 đến 4'),
 'Huỳnh Xuân Huy':('Giới thiệu','1'),
 'Lê Công Thịnh':('Thảo luận TCP','5'),
 'Trần Phúc Hậu':('Thảo luận UDP','6'),
 'Đinh Quang Linh':('Thảo luận reconnect','7'),
 'Đỗ Đức Huy':('Kiểm thử và giới hạn','8'),
}
table(['Họ và tên','Mã thành viên','Phần trình bày','Slide'],[
 [r['name'],r['id'],roles[r['name']][0],roles[r['name']][1]] for r in d['roster']
],[150,97,151,60])
add('Đây là phân công trình bày đề xuất, không phải xác nhận người viết từng phần mã nguồn. Mã thành viên giữ nguyên theo danh sách nhóm.','small')
hh('Lịch trình trên sân khấu')
elapsed=0
rows=[]
for s in slides[:8]:
    end=elapsed+s['duration_seconds']
    rows.append([f'{timefmt(elapsed)} - {timefmt(end)}',str(s['number']),s['presenter'],s['title']])
    elapsed=end
table(['Thời gian tổng','Slide','Người nói','Nội dung'],rows,[93,40,145,180])
add('Slide 9 đến 12 là phần tra cứu kỹ thuật. Chỉ mở khi có câu hỏi sau phần chính, không đọc thêm trong 7 phút.','small')

# Page 2: introductory script and preflight.
page()
h('Giới thiệu và chuẩn bị demo')
hh('Slide 1 giới thiệu trong 60 giây')
note('Người nói', 'Huỳnh Xuân Huy. Thời gian tổng từ 00:00 đến 01:00.')
add(slides[0]['notes'],'quote')
note('Chuyển lượt',slides[0]['transition'])
hh('Chuẩn bị trước khi bấm giờ')
preflight=d.get('demo',{}).get('preflight',[])
for i,item in enumerate(preflight,1):
    add(f'{i}. {item}')
add('Chọn phòng thường 5+0 để đủ thời gian quan sát và có cập nhật ELO. Tránh chế độ PixelBot hoặc tên phòng bắt đầu bằng “Luyện tập · ” nếu muốn minh họa điểm ELO. Không tạo tài khoản mới trong 3 phút demo.','body')
hh('Trình dẫn demo và các bạn hỗ trợ')
add('Trình dùng máy A làm client Trắng và giữ cửa sổ server riêng hoạt động. Hậu giữ client B với quân Đen và chuẩn bị IP. Linh giữ client C ở vai trò khán giả. Khi Trình ra hiệu, B phản hồi nước đi và C vào xem. Những người hỗ trợ không thuyết minh thay Trình. Thịnh theo dõi server, Xuân Huy bấm giờ, Đức Huy giữ kết quả kiểm thử và bản dự phòng đã thử trước.')
add('Nếu chỉ có một máy, mở ba cửa sổ client với ba tài khoản khác nhau và nói rõ đang chạy qua loopback. Không mô tả kết quả trên một máy là đã kiểm thử ba máy thật.','small')

# Page 3: the demo with actions/words/outcome close to one another.
page()
h('Demo 3 phút do Trình thực hiện')
add('Mốc dưới đây tính riêng từ khi Trình bắt đầu demo, tương ứng 01:00 đến 04:00 toàn bài. Chiếu ứng dụng trong 3 phút. Slide 2 đến 4 là trang nhắc nội dung, không cần chuyển qua lại mỗi phút.')
demo_actions=[
 ('Slide 2 từ giây 0 đến giây 60',
  'Tìm server LAN, đăng nhập tài khoản đã chuẩn bị, tạo phòng thường 5+0. Ra hiệu cho B vào đấu và C vào xem.',
  'Hai kỳ thủ và khán giả cùng mã phòng. Có địa chỉ server phản hồi hoặc đã thông báo dùng IP thủ công.'),
 ('Slide 3 từ giây 60 đến giây 120',
  'Đi e2 đến e4 ở A, B đáp e7 đến e5. So sánh ba bàn cờ và nhật ký. Gửi một chat ngắn, chờ hơn 0,5 giây rồi gửi biểu cảm.',
  'Ba client có cùng vị trí quân và lượt. Chat và biểu cảm xuất hiện. Đồng hồ tiếp tục chạy.'),
 ('Slide 4 từ giây 120 đến giây 180',
  'Bấm tên tài khoản, chọn Thử ngắt mạng & kết nối lại. Sau khi nối lại, đối chiếu phòng, bàn cờ và đồng hồ. Đầu hàng, xác nhận và mở Lịch sử & ELO.',
  'Ứng dụng phục hồi ván cũ. Kết quả xuất hiện trong lịch sử, nhãn ELO cập nhật khi mở lịch sử.'),
]
for idx,(title,act,obs) in enumerate(demo_actions,1):
    hh(title)
    note('Thao tác',act)
    note('Lời Trình nói',slides[idx]['notes'])
    note('Cần thấy',obs)
add('Nếu chậm hơn kế hoạch, bỏ thao tác lưu PGN ra file. Không chờ đủ 60 giây để minh họa hết hạn phiên. Không dùng Rời phòng, Đăng xuất hay tắt server thay cho nút ngắt socket.','small')

# Pages 4 and 5: each pair of discussion leads gets an uncluttered page.
for a,b,title in [(4,6,'Thảo luận về TCP và UDP'),(6,8,'Thảo luận về phiên và giới hạn')]:
    page()
    h(title)
    add('Mỗi lượt 45 giây gồm hỏi ngắn, dành khoảng 5 giây cho phản hồi, trả lời trọng tâm rồi chuyển lượt. Nếu thầy cô đã nêu câu hỏi phù hợp, trả lời câu hỏi đó thay cho việc đọc lại câu hỏi gợi ý. Không cộng thêm một phần lý thuyết ngoài 3 phút thảo luận.')
    for s in slides[a:b]:
        hh(f'Slide {s["number"]} {s["presenter"]}')
        # Read source notes verbatim so speaker notes and handout agree.
        note('Chủ đề',s['title'])
        segments=re.split(r'\[([^\]]+)\]',s['notes'])
        if len(segments)>2:
            for j in range(1,len(segments),2):
                note(segments[j].strip().capitalize()+'.',segments[j+1].strip())
        else:
            add(s['notes'],'quote')
        if len(segments)<=2:
            note('Chuyển lượt',s['transition'])
    if b==6:
        hh('Khi câu trả lời kéo dài')
        add('Thịnh và Hậu chốt bằng một câu về quyết định giao thức. Nước đi cần đến đủ và đúng thứ tự nên đi qua TCP. UDP phục vụ dò LAN và cập nhật ngắn hạn. Hết giờ vẫn do server quyết định, không do gói UDP tại client.')
    else:
        hh('Mốc dừng phần chính')
        add('Đức Huy kết thúc trước hoặc đúng 07:00. Các slide tra cứu và câu hỏi bên dưới chỉ dùng nếu buổi bảo vệ cho thêm thời gian. Trình điều phối khi nhiều người muốn trả lời cùng lúc.')

# Page 6: recovery and references, genuinely untimed.
page()
h('Phương án dự phòng và tra cứu')
add('Phần chuẩn bị này không đọc trong lịch trình 7 phút. Nhóm cần thử đường lui trước buổi bảo vệ để Trình chuyển thao tác nhanh khi có sự cố.')
for i,item in enumerate(d.get('demo',{}).get('fallback',[]),1):
    add(f'{i}. {item}')
hh('Các slide kỹ thuật dự phòng')
for s in slides[8:]:
    hh(f'Slide {s["number"]} {s["title"]}')
    add('. '.join(v.rstrip('.') for v in s['body'])+'.')
hh('Bằng chứng và phạm vi kiểm thử')
add('Ngày 19 tháng 11 năm 2026, bộ kiểm thử hiện tại chạy đạt 14 trên 14 bài bằng socket loopback TCP và UDP. Các bài bao phủ framing, quyền đi quân, luật cờ đặc biệt, nhiều phòng, reconnect, đồng hồ, chat, lịch sử và ELO. Kết quả này không phải đo tải 128 kết nối hoặc kiểm chứng triển khai Internet. Nhóm chạy lại trước buổi bảo vệ nếu đã thay đổi mã nguồn.')
hh('Tài liệu để thành viên tự ôn')
add('README.md và các file chessnet/protocol.py, server.py, client.py, gui.py, storage.py cùng tests/test_network.py. Luật cờ dùng thư viện python-chess. Danh sách tên và mã thành viên theo tài liệu nhóm cung cấp. Các nguồn này dùng để đối chiếu khi tập nói và trả lời câu hỏi.','small')

# Page 7: backup Q&A remains separate from the guided discussion.
page()
h('Câu hỏi bổ sung sau phần chính')
add('Không dành thêm thời gian đọc toàn bộ danh sách này. Trình mời thành viên phụ trách trả lời câu hỏi thực tế của thầy cô. Mỗi câu trả lời nên nêu cơ chế, sau đó nói rõ giới hạn.')
for i,q in enumerate(d.get('qa',[])[:8],1):
    hh(f'{i} {q["q"].rstrip("?")}')
    add(q['a'])
    add('Người trả lời: '+q['owner'],'small')

def on_page(canvas,doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor('#555555'))
    canvas.setFont('Arial',8.1)
    canvas.drawString(48,30,'Pixel Chess  |  Kịch bản 7 phút')
    canvas.drawRightString(A4[0]-48,30,f'{doc.page}')
    canvas.restoreState()

OUT.parent.mkdir(parents=True,exist_ok=True)
doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=48,leftMargin=48,topMargin=43,bottomMargin=46,
                      title='Kịch bản và phân công thuyết trình Pixel Chess',author='Nhóm Pixel Chess')
doc.build(story,onFirstPage=on_page,onLaterPages=on_page)
print(str(OUT))
