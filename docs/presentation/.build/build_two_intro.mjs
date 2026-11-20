import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const root=path.resolve('.');
const dep='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1118-904-0_26.1118.904.0_x64__3k8sg7r9htsxt/dependencies';
process.env.RUNTIME_NODE_MODULES=dep+'/node/node_modules';
const {Presentation,PresentationFile}=await import(pathToFileURL(dep+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const require=createRequire(pathToFileURL(dep+'/node/node_modules/__runtime__.cjs'));
const sharp=require('sharp');
const build=path.join(root,'presentation/.build/two_intro');
await fs.mkdir(build,{recursive:true});
const p=Presentation.create({slideSize:{width:1280,height:720}});
const members=JSON.parse(await fs.readFile('presentation/content_script.json','utf8')).roster;
function t(slide,str,x,y,w,h,size,color='#F1F3E9',bold=false){
 const sh=slide.shapes.add({name:str.slice(0,60),geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=str;sh.text.style={fontFamily:'Arial',fontSize:`${size}pt`,color,bold,insets:0,wrap:'square',autoFit:'none'};
}
{
 const s=p.slides.add();s.background.fill='#101B15';
 t(s,'BÀI TẬP LỚN',72,42,1136,35,13,'#B6DC88',true);
 t(s,'Môn Lập trình mạng',72,107,1136,85,40,'#F1F3E9',true);
 t(s,'Nhóm 2',76,199,1116,52,25,'#B6DC88');
 const values=[['Họ và tên','Mã thành viên','Vai trò'],...members.map(m=>[m.name,m.id,m.role])];
 const table=s.tables.add({rows:7,columns:3,left:76,top:264,width:1124,height:350,values,columnWidths:[520,310,294]});
 table.borders.assign({style:'solid',fill:'#425747',width:1});
 table.cells.block({row:0,column:0,rowCount:7,columnCount:3}).assign({fill:'#101B15',textStyle:{fontFamily:'Arial',fontSize:'19pt',color:'#F1F3E9'},margins:{left:16,right:16,top:8,bottom:8},anchor:'center'});
 for(let r=0;r<7;r++) for(let col=0;col<3;col++){
  const cell=table.getCell(r,col);cell.fill=r===0?'#253A2A':'#101B15';
  cell.text.style={fontFamily:'Arial',fontSize:'19pt',color:r===0?'#B6DC88':(r===1?'#EAB190':'#F1F3E9'),bold:r===0||r===1};
 }
 t(s,'NGUYỄN TRỌNG TRÌNH PHỤ TRÁCH DEMO',76,666,1124,30,12,'#AFBEA7');
 s.speakerNotes.text='Người trình bày gợi ý: Huỳnh Xuân Huy. Slide 1: khoảng 25 giây. Hai slide giới thiệu có tổng thời lượng 60 giây.\n\nKính chào thầy cô và các bạn. Chúng em là Nhóm 2, thực hiện bài tập lớn môn Lập trình mạng. Nhóm gồm Nguyễn Trọng Trình là nhóm trưởng, Huỳnh Xuân Huy, Lê Công Thịnh, Trần Phúc Hậu, Đinh Quang Linh và Đỗ Đức Huy. Trưởng nhóm Trình sẽ trực tiếp thực hiện phần demo sau phần giới thiệu.\n\nKhông cần đọc mã thành viên. Chuyển sang slide 2. Nguồn tên, mã và vai trò: Danh_sach_thanh_vien_nhom.docx do người dùng cung cấp. Nhãn nguồn là MSNV, ở slide dùng nhãn chung Mã thành viên để giữ nguyên giá trị, không đổi ý nghĩa thành mã sinh viên.';
}
{
 const s=p.slides.add();s.background.fill='#101B15';
 t(s,'BÀI TẬP LỚN MÔN LẬP TRÌNH MẠNG',72,42,1136,35,13,'#B6DC88',true);
 t(s,'Cờ vua trực tuyến đa luồng',72,107,1136,85,40,'#F1F3E9',true);
 t(s,'Pixel Chess kết hợp TCP và UDP',76,199,1116,52,25,'#B6DC88');
 t(s,'Hai kỳ thủ trên hai máy, có khán giả cùng xem',76,299,950,52,23,'#F1F3E9',true);
 t(s,'TCP truyền nước đi và chat',76,371,920,50,23,'#AFBEA7');
 t(s,'UDP tìm server LAN, cập nhật đồng hồ và biểu cảm',76,430,940,75,23,'#AFBEA7');
 t(s,'Server kiểm tra luật cờ và giữ trạng thái chung',76,520,1050,52,23,'#B6DC88',true);
 const sprite=path.join(build,'knight.png');
 await sharp(path.join(root,'assets/wn.png')).resize(256,320,{kernel:'nearest'}).toFile(sprite);
 s.images.add({blob:new Uint8Array(await fs.readFile(sprite)),contentType:'image/png',alt:'Quân mã pixel từ bộ asset người dùng cung cấp',fit:'contain',position:{left:1052,top:295,width:145,height:182}});
 t(s,'NHÓM 2',76,638,220,30,13,'#AFBEA7');
 s.speakerNotes.text='Người trình bày gợi ý: Huỳnh Xuân Huy. Slide 2: khoảng 35 giây. Hai slide giới thiệu có tổng thời lượng 60 giây.\n\nĐề tài của nhóm là cờ vua trực tuyến đa luồng kết hợp TCP và UDP, tên ứng dụng là Pixel Chess. Hai kỳ thủ có thể chơi trên hai máy và có khán giả cùng theo dõi. TCP truyền nước đi và chat. UDP tìm server trong mạng LAN, cập nhật đồng hồ và gửi biểu cảm. Server kiểm tra luật cờ và giữ trạng thái thống nhất. Sau đây, em xin mời nhóm trưởng Nguyễn Trọng Trình demo trực tiếp trên máy trong ba phút, sau đó nhóm dành ba phút thảo luận.\n\nChuyển thẳng từ slide sang ứng dụng. Không có slide demo hoặc thảo luận. Nguồn: README.md; chessnet/protocol.py, server.py, client.py; asset assets/wn.png cắt từ ảnh người dùng cung cấp.';
}
for(let i=0;i<p.slides.items.length;i++){
 const png=await p.export({slide:p.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(build,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
await (await PresentationFile.exportPptx(p)).save(path.join(build,'candidate.pptx'));
console.log('Rendered exactly 2 introduction slides.');
