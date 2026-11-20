import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
const root=path.resolve('.');
const dep='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1118-904-0_26.1118.904.0_x64__3k8sg7r9htsxt/dependencies';
process.env.RUNTIME_NODE_MODULES=dep+'/node/node_modules';
const {PresentationFile,FileBlob}=await import(pathToFileURL(dep+'/node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const build=path.join(root,'presentation/.build/blend');
await fs.mkdir(build,{recursive:true});
const p=await PresentationFile.importPptx(await FileBlob.load(path.join(root,'presentation/output/Gioi_thieu_UTH_nhom_va_de_tai.pptx')));
const s=p.slides.getItem(0);
const before=await p.export({slide:p.slides.getItem(1),format:'png',scale:1});
const secondBefore=new Uint8Array(await before.arrayBuffer());
for(const im of [...s.images.items]) im.delete();
const logo=path.join(root,'presentation/.build/brand/uth-mark-transparent.png');
s.images.add({blob:new Uint8Array(await fs.readFile(logo)),contentType:'image/png',alt:'Logo UTH tách nền để hiển thị trên nền xanh đậm',fit:'contain',position:{left:54,top:25,width:206,height:92}});
function text(str,pos,size,color,bold=false,align='left'){
 const sh=s.shapes.add({name:str.slice(0,70),geometry:'textbox',position:pos,fill:'none',line:{fill:'none',width:0}});
 sh.text=str;sh.text.style={fontFamily:'Arial',fontSize:`${size}pt`,color,bold,insets:0,wrap:'square',autoFit:'none',alignment:align};
}
text('UNIVERSITY\nOF TRANSPORT\nHOCHIMINH CITY',{left:277,top:40,width:225,height:77},12.5,'#F1F3E9',true);
text('TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI\nTHÀNH PHỐ HỒ CHÍ MINH',{left:530,top:39,width:702,height:87},20,'#B6DC88',true,'center');
s.speakerNotes.text=s.speakerNotes.text+'\nNguồn logo tách nền: uth-mark-transparent.png, dẫn xuất từ ảnh logo người dùng cung cấp. Tên trường và dòng tiếng Anh là chữ có thể chỉnh sửa trên slide.';
for(let i=0;i<2;i++){
 const b=await p.export({slide:p.slides.getItem(i),format:'png',scale:1});
 const bytes=new Uint8Array(await b.arrayBuffer());
 await fs.writeFile(path.join(build,`slide-${i+1}.png`),bytes);
 if(i===1) console.log('Slide2 unchanged:',createHash('sha256').update(bytes).digest('hex')===createHash('sha256').update(secondBefore).digest('hex'));
}
await (await PresentationFile.exportPptx(p)).save(path.join(build,'candidate.pptx'));
const prompt=(await fs.readFile(path.join(root,'presentation/.build/brand/uth-header.png'))).length;
await fs.writeFile(path.join(build,'asset_provenance.txt'),'Tool: built-in ImageGen\nSelected asset: ../brand/uth-mark-transparent.png\nEdit prompt: Extract ONLY the large teal serif UTH letters from the supplied university header. Preserve letterforms, spacing, teal and gold edge. Remove all background and other lettering. Transparent tightly framed clean logo, no shadow or added marks.\nOriginal header bytes: '+prompt+'\n');
console.log('Header blended with dark slide background.');
