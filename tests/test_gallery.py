import importlib.util
import json
import os
import sys
import types
import zipfile
from pathlib import Path

import gradio as gr
import nbformat
import pytest
from PIL import Image, PngImagePlugin

HERE=Path(__file__).resolve().parents[1]

class Options(types.SimpleNamespace):
    def set(self, key, value): setattr(self,key,value)
    def save(self, filename): pass

def setup_gallery(root):
    output=root/'outputs'
    output.mkdir(parents=True,exist_ok=True)
    os.environ['AXO_OUTPUT_ROOT']=str(output)
    os.environ['AXO_LANGUAGE']='pt-BR'
    os.environ['AXO_GALLERY_CACHE']=str(root/'ui-cache')
    shared=types.SimpleNamespace(opts=Options(localization='pt_BR', temp_dir=''),demo=None,config_filename='unused')
    modules=types.ModuleType('modules')
    modules.shared=shared
    modules.images=types.SimpleNamespace(read_info_from_image=lambda img: (img.info.get('parameters',''),None))
    modules.script_callbacks=types.SimpleNamespace(on_ui_tabs=lambda fn:None)
    sys.modules['modules']=modules
    spec=importlib.util.spec_from_file_location('axo_gallery',HERE/'extension/scripts/axo_gallery.py')
    gallery=importlib.util.module_from_spec(spec);spec.loader.exec_module(gallery)
    return gallery,shared

def make_image(path, color='coral', size=(640,480)):
    path.parent.mkdir(parents=True,exist_ok=True)
    info=PngImagePlugin.PngInfo();info.add_text('parameters','A pink axolotl\nSteps: 20, Seed: 42')
    Image.new('RGB',size,color).save(path,pnginfo=info)
    return str(path.resolve())

@pytest.fixture
def env(tmp_path): return setup_gallery(tmp_path)

def test_initial_load_survives_forge_nested_render(env):
    gallery,shared=env
    panel,_,_=gallery.on_ui_tabs()[0]
    with gr.Blocks() as demo:
        with gr.Tab('Axo Studio'):panel.render()
    shared.demo=demo
    cfg=demo.get_config_file()
    assert any(any(t[1]=='load' for t in x['targets']) for x in cfg['dependencies'])
    assert any(c['props'].get('elem_id')=='axo-gallery' for c in cfg['components'])

def test_find_configured_legacy_and_filter(env):
    g,shared=env
    a=make_image(g.OUTPUT_ROOT/'txt2img/2026/a.PNG')
    b=make_image(g.OUTPUT_ROOT.parent/'custom-output/B.png')
    shared.opts.outdir_img2img_samples=str(Path(b).parent)
    assert set(g.find_images())=={a,b}
    assert g.find_images('img2img','b')==[b]
    assert g.find_images('txt2img')==[a]

def test_pagination_preview_metadata_download_and_zip(env):
    g,_=env
    for i in range(26):make_image(g.OUTPUT_ROOT/f'txt2img/{i:02}.png')
    data=g.page_data('all','',0,'pt-BR')
    assert len(data[0])==24 and len(data[1])==24
    assert Image.open(data[4]).size==(640,480) and 'Seed: 42' in data[5]
    assert data[6] is None and data[11]==data[1][0] and data[9]['interactive'] is False and data[10]['interactive'] is True
    second=g.page_data('all','',1,'pt-BR')
    assert len(second[0])==2 and not set(second[1]) & set(data[1])
    with zipfile.ZipFile(g.export_page(second[1],'pt-BR')) as z:
        assert len(z.namelist())==2
        assert z.read(z.namelist()[0])==Path(second[1][0]).read_bytes()

def test_cache_invalidates_overwrites(env):
    g,_=env
    p=make_image(g.OUTPUT_ROOT/'txt2img/a.png','red')
    first=g.page_data('all','',0,'pt-BR')[0][0][0]
    g.page_data('all','',0,'pt-BR')
    assert g.page_data('all','',0,'pt-BR')[0][0][0]==first
    make_image(Path(p),'blue')
    second=g.page_data('all','',0,'pt-BR')[0][0][0]
    assert Image.open(first).getpixel((0,0)) != Image.open(second).getpixel((0,0))

def test_invalid_deleted_and_outside_files(env):
    g,_=env
    (g.OUTPUT_ROOT/'bad.png').write_bytes(b'incomplete')
    assert len(g.page_data('all','',0,'pt-BR')[0])==0
    outside=make_image(g.OUTPUT_ROOT.parent/'private.png')
    with pytest.raises(ValueError):g.safe_path(outside)
    (g.OUTPUT_ROOT/'link.png').symlink_to(outside)
    assert outside not in g.find_images()
    inside=make_image(g.OUTPUT_ROOT/'a.png');Path(inside).unlink()
    assert g.show_image([inside],0,'pt-BR')[0] is None

def test_empty_search_and_page_clamp(env):
    g,_=env
    assert g.page_data('all','',9,'pt-BR')[2]==0
    assert g.page_data('all','missing',0,'pt-BR')[1]==[]
    assert g.show_image([],None,'pt-BR')[0] is None

def test_orientation_and_large_preview(env):
    g,_=env
    p=make_image(g.OUTPUT_ROOT/'large.png',size=(3200,2400))
    preview,_,download,_=g.show_image([p],0,'pt-BR')
    assert Image.open(preview).size==(2048,1536)
    with Image.open(download) as original:assert original.size==(3200,2400)

def test_export_limit_and_duplicate_names(env,monkeypatch):
    g,_=env
    files=[make_image(g.OUTPUT_ROOT/f'{folder}/a.png') for folder in ['img2img','txt2img']]
    with zipfile.ZipFile(g.export_page(files,'en')) as z:assert len(set(z.namelist()))==2
    monkeypatch.setattr(g,'MAX_EXPORT_BYTES',1)
    with pytest.raises(gr.Error):g.export_page(files,'en')

def test_notebook_embedded_code_and_banner():
    path=HERE/'Axo_Image_Studio.ipynb'
    nb=nbformat.read(path,as_version=4);nbformat.validate(nb)
    for c in nb.cells:
        if c.cell_type=='code':compile(c.source,'notebook','exec')
    assert 'Pedroltz' in nb.cells[0].source
    import ast
    launch=ast.parse(nb.cells[2].source)
    assignment=next(n for n in launch.body if isinstance(n,ast.Assign) and any(getattr(t,'id','')=='AXO_EXTENSION_FILES' for t in n.targets))
    files=ast.literal_eval(assignment.value)
    for p,s in files.items():
        if p.endswith('.py'):compile(s,p,'exec')
    assert files['assets/banner.b64']
    assert 'axo_gallery.js' in ' '.join(files)

def test_forge_missing_temp_folder_regression(env,monkeypatch):
    g,shared=env
    path=make_image(g.OUTPUT_ROOT/'txt2img/a.png')
    # Reproduce a Forge cache hook trying to save PIL images into a missing folder.
    # File-path outputs bypass this PIL hook, which is the important regression.
    def missing_forge_temp_folder(image, *args, **kwargs):
        destination = Path(shared.opts.temp_dir) / 'preview.png'
        image.save(destination)
        return str(destination)
    monkeypatch.setattr(gr.processing_utils,'save_pil_to_cache',missing_forge_temp_folder)
    shared.opts.temp_dir=str(g.OUTPUT_ROOT.parent/'unavailable-temp')
    with gr.Blocks() as demo:
        gallery=gr.Gallery();preview=gr.Image()
    shared.demo=demo
    with Image.open(path) as old_value:
        with pytest.raises(FileNotFoundError): gallery.postprocess([(old_value,'old')])
    result=g.page_data('all','',0,'pt-BR')
    assert gallery.postprocess(result[0]).root[0].image.path
    assert preview.postprocess(result[4]).path
    assert result[6] is None


def test_metadata_failure_does_not_break_preview(env,monkeypatch):
    g,shared=env
    path=make_image(g.OUTPUT_ROOT/'a.png')
    def broken(_):raise RuntimeError('metadata reader failure')
    monkeypatch.setattr(g.images,'read_info_from_image',broken)
    result=g.show_image([path],0,'pt-BR')
    assert Path(result[0]).is_file() and result[2]==path
    assert 'RuntimeError' in result[1]


def test_download_is_separate_and_preserves_original(env):
    g,_=env
    path=make_image(g.OUTPUT_ROOT/'a.png')
    result=g.page_data('all','',0,'pt-BR')
    assert result[6] is None
    download=g.prepare_download(result[11],'pt-BR')
    assert Path(download).read_bytes()==Path(path).read_bytes()
    Path(path).unlink()
    with pytest.raises(gr.Error):g.prepare_download(result[11],'pt-BR')
    assert Path(result[4]).is_file()


def test_scan_failure_returns_actionable_message(env,monkeypatch):
    g,_=env
    def broken(*args):raise PermissionError('Drive unavailable')
    monkeypatch.setattr(g,'find_images',broken)
    data=g.page_data('all','',0,'pt-BR')
    assert len(data)==12 and 'PermissionError' in data[3] and 'Diagnosticar' in data[3]


def test_cmyk_is_normalized_for_png_transport(env):
    g,_=env
    path=g.OUTPUT_ROOT/'cmyk.jpg'
    Image.new('CMYK',(80,60),(0,100,100,0)).save(path)
    result=g.page_data('all','',0,'pt-BR')
    assert len(result[0])==1
    with Image.open(result[4]) as im:assert im.mode=='RGB'
