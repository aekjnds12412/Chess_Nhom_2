import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {createHash} from 'node:crypto';
const root=path.resolve('.');
const dep='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1118-904-0_26.1118.904.0_x64__3k8sg7r9htsxt/dependencies';
process.env.RUNTIME_NODE_MODULES=dep+'/node/node_modules';
const {PresentationFile,FileBlob}=await import(pathToFileURL(dep+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const require=createRequire(pathToFileURL(dep+'/node/node_modules/__runtime__.cjs'));
const sharp=require('sharp');
const build=path.join(root,'presentation/.build/brand');
await fs.mkdir(build,{recursive:true});
const p=await PresentationFile.importPptx(await FileBlob.load(path.join(root,'presentation/output/Gioi_thieu_nhom_va_de_tai_2_trang.pptx')));
const s=p.slides.getItem(0);
function t(str,x,y,w,h,size,color='#F1F3E9',bold=false){
 const sh=s.shapes.add({name:str.slice(0,70),geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=str;sh.text.style={fontFamily:'Arial',fontSize:`${size}pt`,color,bold,insets:0,wrap:'square',autoFit:'none'};
}
// Edit only slide 1. Keep the native member table and all of slide 2 intact.
for(const sh of [...s.shapes.items]) sh.delete();
const header=path.join(build,'uth-header.png');
await sharp('C:/Users/Nguye/AppData/Local/Temp/codex-clipboard-d4ee3122-bcfc-47fd-bb8d-558c82679d81.png')
 .extract({left:17,top:15,width:1249,height:115}).toFile(header);
s.images.add({blob:new Uint8Array(await fs.readFile(header)),contentType:'image/png',alt:'Logo UTH và tên Trường Đại học Giao thông vận tải Thành phố Hồ Chí Minh từ ảnh người dùng cung cấp',fit:'contain',position:{left:48,top:20,width:1184,height:109.016}});
t('Viện Công nghệ thông tin và Điện, điện tử',54,148,1172,34,18,'#F1F3E9',true);
t('Ngành / chuyên ngành: Công nghệ thông tin',54,188,1172,34,18,'#AFBEA7');
t('Bài tập lớn Lập trình mạng',54,246,950,58,32,'#F1F3E9',true);
t('Nhóm 2',1045,253,185,46,24,'#B6DC88',true);
const table=s.tables.items[0];
table.position={left:54,top:326,width:1172,height:308};
table.columnTracks=[{mode:'fixed',value:536},{mode:'fixed',value:320},{mode:'fixed',value:316}];
table.cells.block({row:0,column:0,rowCount:7,columnCount:3}).assign({margins:{left:16,right:16,top:5,bottom:5},anchor:'center'});
for(let r=0;r<7;r++){
 table.rows[r].height=44;
 for(let c=0;c<3;c++) table.getCell(r,c).text.style={fontFamily:'Arial',fontSize:'18pt',color:r===0?'#B6DC88':(r===1?'#EAB190':'#F1F3E9'),bold:r===0||r===1};
}
t('NHÓM TRƯỞNG NGUYỄN TRỌNG TRÌNH PHỤ TRÁCH DEMO',54,666,1172,30,12,'#AFBEA7');
s.speakerNotes.text='Người trình bày gợi ý: Huỳnh Xuân Huy. Slide1 khoảng25giây, slide2 khoảng35giây. Tổng giới thiệu60giây, tiếp đến demo3phút trên máy và thảo luận3phút.\n\nKính chào thầy cô và các bạn. Chúng em là Nhóm2, ngành Công nghệ thông tin, Viện Công nghệ thông tin và Điện, điện tử, Trường Đại học Giao thông vận tải Thành phố Hồ Chí Minh. Nhóm thực hiện bài tập lớn môn Lập trình mạng với sáu thành viên như trên màn hình. Nguyễn Trọng Trình là nhóm trưởng và sẽ trực tiếp thực hiện phần demo.\n\nKhông đọc mã thành viên. Chuyển sang slide2 giới thiệu đề tài.\nNguồn logo/tên trường: ảnh codex-clipboard-d4ee3122-bcfc-47fd-bb8d-558c82679d81.png. Nguồn viện/ngành: ảnh codex-clipboard-d1e53a20-952d-48ff-8251-6bff9d48c684.png. Nguồn danh sách: Danh_sach_thanh_vien_nhom.docx, tất cả do người dùng cung cấp. Logo dùng ảnh gốc, chỉ cắt viền màn hình.';
for(let i=0;i<2;i++){
 const b=await p.export({slide:p.slides.getItem(i),format:'png',scale:1});
 await fs.writeFile(path.join(build,`after-${i+1}.png`),new Uint8Array(await b.arrayBuffer()));
}
const hash=async f=>createHash('sha256').update(await fs.readFile(f)).digest('hex');
console.log('Slide2 render unchanged:',(await hash(path.join(build,'before-2.png'))) === (await hash(path.join(build,'after-2.png'))));
await (await PresentationFile.exportPptx(p)).save(path.join(build,'candidate.pptx'));
console.log('Updated only slide1 school/institute/major branding.');
