import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=path.resolve('.');
const dep='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1118-904-0_26.1118.904.0_x64__3k8sg7r9htsxt/dependencies';
process.env.RUNTIME_NODE_MODULES=dep+'/node/node_modules';
const skill='C:/Users/Nguye/.codex/plugins/cache/openai-primary-runtime/presentations/26.1118.11504/skills/presentations';
const {finalizePresentation}=await import(pathToFileURL(skill+'/container_tools/artifact_tool_utils.mjs').href);
const result=await finalizePresentation({
 workspaceDir:root,candidatePath:path.join(root,'presentation/.build/candidate.pptx'),
 finalPath:path.join(root,'presentation/output/Pixel_Chess_Thuyet_trinh_7_phut.pptx'),
 pythonExecutable:dep+'/python/python.exe',
 integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',
 explicitTotalSlideCount:12,requiredNativeTableOwnerSlides:[6,9,11],requiredNativeChartOwnerSlides:[],
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...([6,9,11].flatMap(n=>['--require-native-table-slide',String(n)]))],
 fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,
 receiptPath:path.join(root,'presentation/.build/validation.json')
});
console.log(JSON.stringify(result));
