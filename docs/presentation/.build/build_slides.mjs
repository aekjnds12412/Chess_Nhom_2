import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const root=path.resolve('.');
const dep='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1118-904-0_26.1118.904.0_x64__3k8sg7r9htsxt/dependencies';
const modules=dep+'/node/node_modules';
const skill='C:/Users/Nguye/.codex/plugins/cache/openai-primary-runtime/presentations/26.1118.11504/skills/presentations';
const {Presentation,PresentationFile}=await import(pathToFileURL(modules+'/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const {createRequire}=await import('node:module');
const require=createRequire(pathToFileURL(modules+'/package.json'));
const sharp=require('sharp');
const source=JSON.parse(await fs.readFile('presentation/content_script.json','utf8'));
if(source.slides.length!==12 || source.slides.slice(0,8).reduce((a,b)=>a+b.duration_seconds,0)!==420){throw new Error('Expected final 7-minute content, 8 main + 4 appendix slides');}
const build=path.join(root,'presentation/.build');
const out=path.join(root,'presentation/output');
await fs.mkdir(out,{recursive:true});
await fs.mkdir(path.join(build,'renders'),{recursive:true});
const C={bg:'#101B15',light:'#F1F3E9',muted:'#AFBEA7',green:'#B6DC88',salmon:'#EAB190',rule:'#4F6453'};
const p=Presentation.create({slideSize:{width:1280,height:720}});
function text(slide,str,x,y,w,h,size=22,color=C.light,bold=false){
 const s=slide.shapes.add({name:str.slice(0,42),geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 s.text=str;s.text.style={fontFamily:'Arial',fontSize:`${size}pt`,color,bold,insets:0,autoFit:'none',wrap:'square'};
 return s;
}
async function bitmap(slide,file,x,y,w,h,alt){
 const b=await fs.readFile(file);
 slide.images.add({blob:new Uint8Array(b),contentType:'image/png',alt,fit:'contain',position:{left:x,top:y,width:w,height:h}});
}
async function piece(slide,key,x=1040,y=405){
 const file=path.join(build,key+'-large.png');
 await sharp(path.join(root,'assets',key+'.png')).resize(256,320,{kernel:'nearest'}).toFile(file);
 await bitmap(slide,file,x,y,150,188,'Quân cờ pixel từ bộ asset người dùng cung cấp');
}
function footer(slide,n,phase,who,time){
 text(slide,phase,72,651,280,28,12,C.muted);
 text(slide,who,360,651,565,28,12,C.muted);
 text(slide,time,980,651,140,28,12,C.green,true);
 text(slide,String(n).padStart(2,'0'),1160,651,52,28,12,C.muted);
}
function newSlide(n,phase,title,who,time){
 const s=p.slides.add();s.background.fill=C.bg;
 text(s,phase,72,44,1060,28,12,C.green,true);
 text(s,title,72,100,1120,110,34,C.light,true);
 footer(s,n,n<=8?'PIXEL CHESS':'PHỤ LỤC THAM KHẢO',who,time);
 return s;
}
function notes(slide,index,extra=''){
 const d=source.slides[index];
 slide.speakerNotes.text=`Người trình bày: ${d.presenter}\nThời lượng: ${d.duration_seconds?d.duration_seconds+' giây':'Tham khảo ngoài phần 7 phút'}\n\n${d.notes}\n\nChuyển lời: ${d.transition}\n\n${extra}\nNguồn: ${d.source}. Bộ asset: assets/original.png do người dùng cung cấp. Phân công dành cho buổi trình bày, không xác nhận tác giả mã nguồn.`;
}
function rows(slide,items,{x=72,y=240,gap=112,w=1000}={}){
 items.forEach((item,i)=>{
  text(slide,String(i+1).padStart(2,'0'),x,y+i*gap,66,50,27,C.green,true);
  text(slide,item[0],x+88,y+i*gap,w-100,48,24,C.light,true);
  text(slide,item[1],x+88,y+49+i*gap,w-100,52,18,C.muted);
 });
}
function nativeTable(slide,values,widths,y=230,height=330,font=20){
 const table=slide.tables.add({rows:values.length,columns:values[0].length,left:72,top:y,width:1136,height,values,columnWidths:widths});
 table.borders.assign({fill:C.rule,style:'solid',width:1});
 table.cells.block({row:0,column:0,rowCount:values.length,columnCount:values[0].length}).assign({
  fill:C.bg,textStyle:{fontFamily:'Arial',fontSize:`${font}pt`,color:C.light},
  margins:{left:16,right:16,top:12,bottom:12},anchor:'center',
 });
 for(let r=0;r<values.length;r++)for(let col=0;col<values[0].length;col++){
  const cell=table.getCell(r,col);
  cell.fill=r===0?'#253A2A':C.bg;
  cell.text.style={fontFamily:'Arial',fontSize:`${font}pt`,color:r===0?C.green:C.light,bold:r===0};
 }
 return table;
}

// 1. Introduction. Original source board, cropped only to its original boundaries.
{
 const s=p.slides.add();s.background.fill=C.bg;
 text(s,'BÀI TẬP LỚN MÔN LẬP TRÌNH MẠNG',72,48,1136,32,13,C.green,true);
 text(s,'PIXEL\nCHESS',72,138,690,230,68,C.light,true);
 text(s,'Cờ vua trực tuyến đa luồng\nkết hợp TCP và UDP',76,402,650,116,27,C.muted);
 text(s,'Giới thiệu 1 phút\nDemo 3 phút\nThảo luận 3 phút',820,440,390,115,20,C.green,true);
 const crop=path.join(build,'board-crop.png');
 await sharp(path.join(root,'assets/original.png')).extract({left:9,top:9,width:380,height:380}).resize(360,360,{kernel:'nearest'}).toFile(crop);
 await bitmap(s,crop,820,83,340,340,'Bàn cờ trong sprite sheet gốc người dùng cung cấp');
 footer(s,1,'NHÓM 2','Huỳnh Xuân Huy','0:00–1:00');
 notes(s,0,'Từ 0:00 đến 1:00. Kết thúc giới thiệu bằng lời mời trưởng nhóm Nguyễn Trọng Trình demo.');
}
// 2–4. Demo cues. Trình controls the demo, members only assist on clients B/C.
{
 let s=newSlide(2,'DEMO 1 / 3','Tìm server và vào phòng','Nguyễn Trọng Trình','1:00–2:00');
 rows(s,[['Tìm server LAN','Client dò máy chủ qua UDP cổng 9999.'],['Tạo phòng và vào đấu','Hai tài khoản đã chuẩn bị trước, thời gian 5+0.'],['Vào xem cùng một bàn','Client C theo dõi với vai trò khán giả.']],{w:965,gap:110,y:224});
 await piece(s,'wn');notes(s,1,'Slide là mốc dẫn. Trình chuyển sang ứng dụng để thao tác, không đọc lại toàn bộ nội dung slide. Hậu hỗ trợ client B, Linh hỗ trợ client C trong im lặng theo hiệu lệnh.');
 s=newSlide(3,'DEMO 2 / 3','Một nước đi, cùng một trạng thái','Nguyễn Trọng Trình','2:00–3:00');
 text(s,'e2–e4',72,225,640,135,64,C.green,true);
 text(s,'Server kiểm tra lượt và luật cờ',76,377,940,55,25,C.light,true);
 text(s,'Hai kỳ thủ và khán giả cùng nhận STATE mới.',76,439,930,70,23,C.muted);
 text(s,'Chat qua TCP. Biểu cảm qua UDP.',76,552,940,44,20,C.salmon);
 await piece(s,'wp');notes(s,2,'Đi e2e4, client B đáp e7e5. Chỉ ra cùng bàn cờ/nhật ký, đồng hồ do server quyết định. Gửi chat, đợi hơn 0,5 giây rồi gửi emoji. Không dùng GUI để chứng minh server từ chối gói sai vì GUI đã lọc nước sai.');
 s=newSlide(4,'DEMO 3 / 3','Khôi phục phiên và lưu kết quả','Nguyễn Trọng Trình','3:00–4:00');
 text(s,'60 giây',72,225,850,140,64,C.green,true);
 text(s,'Thời hạn giữ phiên sau khi server phát hiện ngắt',76,360,1030,58,24,C.light,true);
 rows(s,[['Ngắt socket rồi tự nối lại','FEN và vai trò giữ nguyên. Đồng hồ tiếp tục chạy.'],['Đầu hàng, sau đó mở lịch sử','Kiểm tra kết quả ván và ELO của tài khoản demo.']],{x:76,y:447,w:945,gap:87});
 await piece(s,'wr',1050,430);notes(s,3,'Chọn tên tài khoản > Thử ngắt mạng & kết nối lại. Giữ server riêng chạy. Đợi WELCOME/STATE khôi phục rồi đi thêm một nước nếu kịp. Đầu hàng và xác nhận, mở Lịch sử & ELO để cập nhật nhãn ELO. Không chờ mất mạng đủ 60 giây trong demo.');
}
// 5–8. Four guided questions, 45 seconds each.
{
 let s=newSlide(5,'THẢO LUẬN 1 / 4','Vì sao TCP vẫn cần đóng gói?','Lê Công Thịnh','4:00–4:45');
 text(s,'Một lần recv()\ncó bằng một JSON?',72,222,1000,138,37,C.light,true);
 text(s,'4 byte độ dài + JSON UTF-8',76,421,1030,60,29,C.green,true);
 text(s,'Đọc đủ header, rồi đọc đủ payload.\nXử lý thông điệp bị chia nhỏ hoặc ghép liền.',76,504,950,95,22,C.muted);
 await piece(s,'bn',1050,460);notes(s,4,'Mời một câu trả lời ngắn. Nếu không có người phản hồi, Thịnh tự giải thích sau 5 giây. Tổng cả câu hỏi và trả lời không quá 45 giây.');
 s=newSlide(6,'THẢO LUẬN 2 / 4','Mất gói UDP có làm sai ván cờ?','Trần Phúc Hậu','4:45–5:30');
 nativeTable(s,[['TCP','UDP'],['Nước đi, STATE, chat','Dò LAN, đồng hồ, emoji'],['Cần đầy đủ và đúng thứ tự','Chấp nhận mất một cập nhật']], [568,568],245,250,22);
 text(s,'Server giữ thời gian và kết quả chính thức.',76,537,1090,54,25,C.green,true);
 notes(s,5,'Đồng hồ client nội suy từ các gói mới. UDP có thể mất/đảo thứ tự, nên không dùng một gói CLOCK làm căn cứ xử thắng. TCP dự phòng mỗi 2 giây. UDP không phải luôn nhanh hơn mọi giao thức trong mọi tình huống.');
 s=newSlide(7,'THẢO LUẬN 3 / 4','Mất mạng 10 giây thì đồng hồ ra sao?','Đinh Quang Linh','5:30–6:15');
 text(s,'02:00 còn khoảng 01:50',72,244,1110,100,40,C.green,true);
 text(s,'Nếu đó là lượt đang chạy của kỳ thủ mất mạng',76,350,1100,62,23,C.muted);
 text(s,'RESUME kèm token lấy lại phòng và FEN.',76,462,1050,58,24,C.light,true);
 text(s,'Server phải tiếp tục chạy. Ván hiện tại nằm trong RAM.',76,534,1030,55,21,C.muted);
 await piece(s,'wb',1050,424);notes(s,6,'Ví dụ là khoảng 10 giây trên lượt kỳ thủ bị ngắt, bỏ qua độ trễ. Băm mật khẩu bảo vệ DB, không thay thế mã hóa kết nối. Token là dữ liệu riêng, không chiếu token thật.');
 s=newSlide(8,'THẢO LUẬN 4 / 4','Bản hiện tại đã kiểm chứng đến đâu?','Đỗ Đức Huy','6:15–7:00');
 text(s,'14/14',72,220,660,130,70,C.green,true);
 text(s,'ca kiểm thử đạt trên loopback',76,369,1050,60,27,C.light,true);
 text(s,'TCP/UDP, luật đặc biệt, khán giả và reconnect',76,433,1030,65,22,C.muted);
 text(s,'Chưa benchmark tải lớn. Chưa có TLS và voice chat.',76,536,1050,66,22,C.salmon);
 await piece(s,'bk',1050,270);notes(s,7,'Kiểm thử thực tế ngày 19/11/2026: python app.py --test, 14 tests OK. Đây là kiểm thử loopback, không phải benchmark 128 máy hoặc bằng chứng đã triển khai Internet. Đức Huy kết thúc phần thảo luận đúng 7:00 và cảm ơn.');
}
// Appendices retain technical facts for questions outside the timed talk.
{
 let s=newSlide(9,'PHỤ LỤC A1','Kiến trúc của Pixel Chess','Tham khảo khi được hỏi','Ngoài 7 phút');
 nativeTable(s,[['Thành phần','Trách nhiệm'],['Tkinter client','Hiển thị, gửi thao tác, nhận sự kiện'],['TCP server','Phiên, phòng, luật cờ, STATE và chat'],['UDP server','Discovery, CLOCK và EMOJI'],['SQLite','Tài khoản, ELO, lịch sử và PGN']],[330,806],220,350,20);
 text(s,'Nhiều luồng đọc kết nối. Khóa bảo vệ trạng thái chung.',76,590,1120,44,18,C.muted);
 notes(s,8,'RLock tuần tự hóa phần cập nhật trạng thái. ThreadPoolExecutor cho phép các kết nối chờ đọc đồng thời. Giới hạn 128 chỉ là cấu hình chưa benchmark.');
 s=newSlide(10,'PHỤ LỤC A2','Framing và xử lý MOVE','Tham khảo khi được hỏi','Ngoài 7 phút');
 text(s,'[4 byte N][N byte JSON UTF-8]',72,229,1135,74,30,C.green,true);
 text(s,'{"type":"MOVE","from":"e2","to":"e4"}',76,324,1125,70,23,C.light);
 text(s,'1. Kiểm tra vai trò, lượt và thời gian\n2. python-chess kiểm tra nước đi\n3. Cập nhật bàn cờ rồi phát STATE',76,438,1100,150,24,C.muted);
 notes(s,9,'Giới hạn frame64KiB. FEN mô tả thế cờ hiện tại, không thay thế lịch sử. SAN/UCI lưu nhật ký, PGN lưu ván. Chống chỉnh trạng thái client không ngăn được dùng engine ngoài.');
 s=newSlide(11,'PHỤ LỤC A3','UDP và vòng đời phiên','Tham khảo khi được hỏi','Ngoài 7 phút');
 nativeTable(s,[['Cơ chế','Nhịp hoặc thời hạn'],['UDP CLOCK','Khoảng 5 lần/giây'],['TCP CLOCK dự phòng','Mỗi 2 giây'],['Heartbeat client','Mỗi 3 giây'],['Giữ phiên ngắt kết nối','60 giây từ lúc server phát hiện']],[520,616],220,350,20);
 text(s,'Broadcast trong LAN có thể bị chặn. Có thể nhập IP thủ công.',76,590,1120,44,18,C.muted);
 notes(s,10,'Không tuyên bố tự dò Internet xuyên NAT. Client thử resume trong khoảng58giây sau khi bắt lỗi. Server ngắt im lặng khi seen hơn12giây, socket read timeout15giây. Server restart mất ván đang chơi trong RAM.');
 s=newSlide(12,'PHỤ LỤC A4','Dữ liệu và phạm vi kiểm thử','Tham khảo khi được hỏi','Ngoài 7 phút');
 text(s,'SQLite lưu tài khoản và ván đã kết thúc',72,225,1130,60,27,C.light,true);
 text(s,'PBKDF2 với salt riêng. ELO ban đầu 1200, K = 24.\nPGN chứa diễn biến ván để tải lại.',76,299,1120,92,22,C.muted);
 text(s,'14 ca kiểm thử mạng và luật cờ',72,433,1120,60,27,C.green,true);
 text(s,'Framing, sai lượt, chiếu hết, luật đặc biệt, clock,\nreconnect, spectator, chat, ghép trận và UDP.',76,512,1110,90,22,C.muted);
 notes(s,11,'Đã chạy14/14 tests19/11/2026. Không có số liệu latency/load chính thức. Dockerfile có sẵn nhưng chưa xác minh Docker trên máy này. Bản hiện tại chưa có TLS, voice chat, lưu phiên qua restart.');
}

for(const [i,s] of p.slides.items.entries()){
 const png=await p.export({slide:s,format:'png',scale:1});
 await fs.writeFile(path.join(build,'renders',`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
 const layout=await s.export({format:'layout'});
 await fs.writeFile(path.join(build,'renders',`slide-${String(i+1).padStart(2,'0')}.json`),await layout.text());
 console.log('Rendered slide',i+1);
}
const candidate=path.join(build,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidate);
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const result=await finalizePresentation({
 workspaceDir:root,candidatePath:candidate,finalPath:path.join(out,'Pixel_Chess_Thuyet_trinh_7_phut.pptx'),
 pythonExecutable:dep+'/python/python.exe',
 integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',
 explicitTotalSlideCount:12,requiredNativeTableOwnerSlides:[6,9,11],requiredNativeChartOwnerSlides:[],
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...([6,9,11].flatMap(n=>['--require-native-table-slide',String(n)]))],
 fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
 receiptPath:path.join(build,'validation.json'),
});
console.log(JSON.stringify(result));
