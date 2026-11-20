import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const base='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1118-904-0_26.1118.904.0_x64__3k8sg7r9htsxt/dependencies/node/node_modules';
const {PresentationFile,FileBlob}=await import(pathToFileURL(base+'/@oai/artifact-tool/dist/artifact_tool.mjs').href);
const p=await PresentationFile.importPptx(await FileBlob.load('presentation/output/Gioi_thieu_nhom_va_de_tai_2_trang.pptx'));
const s=p.slides.getItem(0);
console.log('SHAPES',s.shapes.items.map(x=>({id:x.id,name:x.name,text:x.text.toString(),position:x.position})));
console.log('TABLES',s.tables.items.map(x=>({id:x.id,position:x.position,rows:x.rows.length})));
console.log('DELETE',typeof s.tables.items[0].delete,typeof p.delete);
await fs.mkdir('presentation/.build/brand',{recursive:true});
for(let i=0;i<2;i++){
 const b=await p.export({slide:p.slides.getItem(i),format:'png',scale:1});
 await fs.writeFile(`presentation/.build/brand/before-${i+1}.png`,new Uint8Array(await b.arrayBuffer()));
}
