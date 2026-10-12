"""Axo Image Studio gallery. Integrates with AUTOMATIC1111's existing Gradio app."""
from functools import lru_cache
import hashlib
import shutil
import traceback
import html
import os
import tempfile
import zipfile
from pathlib import Path

import gradio as gr
from PIL import Image, ImageOps
from modules import images, script_callbacks, shared

EXTENSION_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = Path(os.environ.get('AXO_OUTPUT_ROOT', '/content/axo-image-studio/outputs'))
PAGE_SIZE = 24
UI_CACHE = Path(os.environ.get('AXO_GALLERY_CACHE', str(Path(tempfile.gettempdir()) / 'axo-gallery-cache')))
SOURCE_KEYS = {
    'txt2img': ('outdir_samples', 'outdir_txt2img_samples'),
    'img2img': ('outdir_samples', 'outdir_img2img_samples'),
    'extras': ('outdir_samples', 'outdir_extras_samples'),
    'grids': ('outdir_grids', 'outdir_txt2img_grids', 'outdir_img2img_grids'),
    'saved': ('outdir_save',),
}
MAX_EXPORT_BYTES = 256 * 1024 * 1024
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.webp'}
TEXT = {
    'en': {
        'tagline': 'Generate. Explore. Create.', 'grids': 'Grids', 'saved': 'Saved', 'select_hint': 'Select an image to inspect it.', 'search_hint': 'Type a filename and press Enter', 'gallery': 'Image library',
        'source': 'Source', 'all': 'All images', 'search': 'Filter by filename',
        'refresh': 'Refresh', 'previous': 'Previous', 'next': 'Next',
        'preview': 'Image preview', 'parameters': 'Generation parameters',
        'prepare': 'Prepare original download', 'download': 'Download image', 'export': 'Export this page as ZIP',
        'archive': 'Download archive', 'language': 'Workspace language',
        'apply': 'Apply language', 'notice': 'Applied. Reload the WebUI to update its main labels. Third-party extensions may remain in English.',
        'empty': 'No images yet. Generate an image, then click Refresh.',
        'page': 'Page {page}/{pages} · {count} images · Newest first',
        'metadata': 'No embedded generation parameters found.',
        'missing': 'This image is no longer available. Refresh the library.',
        'export_limit': 'This page exceeds the 256 MiB archive limit.',
        'bad_image': 'Could not open this image.',
    },
    'pt-BR': {
        'tagline': 'Gere. Explore. Crie.', 'grids': 'Grades', 'saved': 'Salvas', 'select_hint': 'Selecione uma imagem para explorar.', 'search_hint': 'Digite um nome e pressione Enter', 'gallery': 'Biblioteca de imagens',
        'source': 'Origem', 'all': 'Todas as imagens', 'search': 'Filtrar pelo nome do arquivo',
        'refresh': 'Atualizar', 'previous': 'Anterior', 'next': 'Próxima',
        'preview': 'Prévia da imagem', 'parameters': 'Parâmetros de geração',
        'prepare': 'Preparar download original', 'download': 'Baixar imagem', 'export': 'Exportar esta página em ZIP',
        'archive': 'Baixar arquivo ZIP', 'language': 'Idioma do workspace',
        'apply': 'Aplicar idioma', 'notice': 'Aplicado. Recarregue a WebUI para atualizar seus rótulos principais. Extensões de terceiros podem continuar em inglês.',
        'empty': 'Ainda não há imagens. Gere uma imagem e clique em Atualizar.',
        'page': 'Página {page}/{pages} · {count} imagens · Mais recentes primeiro',
        'metadata': 'Não há parâmetros de geração embutidos.',
        'missing': 'A imagem não está mais disponível. Atualize a biblioteca.',
        'export_limit': 'Esta página ultrapassa o limite de 256 MiB do ZIP.',
        'bad_image': 'Não foi possível abrir esta imagem.',
    },
}


def labels(language):
    return TEXT.get(language, TEXT['en'])


def image_roots(source='all'):
    roots = [OUTPUT_ROOT] if source == 'all' else [OUTPUT_ROOT / source]
    for category, keys in SOURCE_KEYS.items():
        if source not in ('all', category):
            continue
        for key in keys:
            value = getattr(shared.opts, key, '')
            if value:
                roots.append(Path(value))
    # Include the standard Forge folders used before this notebook's configuration.
    legacy = EXTENSION_ROOT.parents[1] / 'outputs'
    names = {'txt2img': ('txt2img-images',), 'img2img': ('img2img-images',),
             'extras': ('extras-images',), 'grids': ('txt2img-grids', 'img2img-grids'),
             'saved': ('saved',)}
    roots.extend(legacy / name for category, names_ in names.items()
                 if source in ('all', category) for name in names_)
    return list(dict.fromkeys(root.resolve() for root in roots))


def safe_path(value):
    candidate = Path(value).resolve()
    if not any(candidate.is_relative_to(root) for root in image_roots()) or not candidate.is_file():
        raise ValueError('Image is outside the configured output directories or does not exist.')
    if candidate.suffix.lower() not in IMAGE_SUFFIXES:
        raise ValueError('Unsupported image format.')
    return candidate


def find_images(source='all', query=''):
    found = {}
    # Prune nested roots so the same Drive directory is never scanned twice.
    roots = sorted(image_roots(source), key=lambda root: len(root.parts))
    scanned = []
    allowed = image_roots()
    for root in roots:
        if any(root.is_relative_to(parent) for parent in scanned):
            continue
        scanned.append(root)
        for folder, dirs, names in os.walk(root, followlinks=False):
            dirs[:] = [name for name in dirs if not (Path(folder) / name).is_symlink()]
            for name in names:
                path = Path(folder) / name
                if path.suffix.lower() not in IMAGE_SUFFIXES or query.casefold() not in name.casefold():
                    continue
                try:
                    if path.is_symlink():
                        continue
                    path = path.resolve()
                    if not any(path.is_relative_to(base) for base in allowed):
                        continue
                    found[str(path)] = path.stat().st_mtime_ns
                except (OSError, ValueError):
                    continue
    return sorted(found, key=lambda path: (found[path], path), reverse=True)


def cached_image_file(value, modified, size, edge):
    # File-backed components avoid Forge's save_pil_to_cache override, whose
    # global temp_dir may point to an unavailable directory/Drive mount.
    key = hashlib.sha256(f'{value}|{modified}|{size}|{edge}|v2'.encode()).hexdigest()
    folder = UI_CACHE / 'previews'
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / (key + '.png')
    if target.is_file():
        return str(target)
    with Image.open(value) as original:
        original.draft('RGB', (edge, edge))
        result = ImageOps.exif_transpose(original)
        result.thumbnail((edge, edge), Image.Resampling.LANCZOS)
        result = result.convert('RGBA' if 'A' in result.getbands() or 'transparency' in result.info else 'RGB')
        # Metadata is read separately; malformed EXIF/ICC should never prevent display.
        result.info.clear()
        fd, temporary = tempfile.mkstemp(suffix='.png', dir=folder)
        os.close(fd)
        try:
            result.save(temporary, format='PNG')
            os.replace(temporary, target)
        finally:
            Path(temporary).unlink(missing_ok=True)
            result.close()
    return str(target)


def cached_thumbnail(value, modified, size):
    return cached_image_file(value, modified, size, 384)


def _page_data(source, query, page, language):
    (UI_CACHE / 'previews').mkdir(parents=True, exist_ok=True)
    paths = find_images(source, query)
    pages = max(1, (len(paths) + PAGE_SIZE - 1) // PAGE_SIZE)
    page = min(max(0, int(page)), pages - 1)
    selected = paths[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    thumbnails, valid = [], []
    for value in selected:
        try:
            path = safe_path(value)
            stat = path.stat()
            thumbnails.append((cached_thumbnail(str(path), stat.st_mtime_ns, stat.st_size), path.name))
            valid.append(str(path))
        except (OSError, ValueError, Image.DecompressionBombError) as error:
            print(f'[Axo Studio] Miniatura ignorada: {type(error).__name__}: {error}', flush=True)
            continue
    text = labels(language)
    status = text['page'].format(page=page + 1, pages=pages, count=len(paths)) if paths else text['empty']
    if len(valid) < len(selected):
        status += (' · Arquivos ilegíveis ignorados: ' if language == 'pt-BR' else ' · Unreadable files skipped: ') + str(len(selected) - len(valid))
    preview, parameters, selected_file, details = show_image(valid, 0, language)
    return (thumbnails, valid, page, status, preview, parameters, None, None, details,
            gr.update(interactive=page > 0), gr.update(interactive=page < pages - 1), selected_file)


def error_message(operation, error, language):
    # Preserve the traceback in the Colab log and show the exception type in the UI.
    print(f'[Axo Studio] {operation}: {type(error).__name__}: {error}', flush=True)
    traceback.print_exc()
    prefix = 'Falha em' if language == 'pt-BR' else 'Failed to'
    hint = 'Consulte a célula Diagnosticar galeria no Colab.' if language == 'pt-BR' else 'See the Diagnose gallery cell in Colab.'
    return f'{prefix} {operation} ({type(error).__name__}). {hint}'


def page_data(source, query, page, language):
    try:
        return _page_data(source, query, page, language)
    except Exception as error:
        message = error_message('carregar biblioteca', error, language)
        return ([], [], 0, message, None, '', None, None, '',
                gr.update(interactive=False), gr.update(interactive=False), None)


def show_image(paths, index, language):
    text = labels(language)
    if not isinstance(index, int) or not 0 <= index < len(paths):
        return None, '', None, text['select_hint']
    try:
        path = safe_path(paths[index])
        stat = path.stat()
        preview = cached_image_file(str(path), stat.st_mtime_ns, stat.st_size, 2048)
        with Image.open(path) as image:
            width, height = image.size
            try:
                info, _ = images.read_info_from_image(image)
            except Exception as error:
                # Optional prompt parsing must not break otherwise readable images.
                info = error_message('ler metadados', error, language)
        details = (f'<div class="axo-details"><strong>{html.escape(path.name)}</strong>'
                   f'<span>{width} × {height} px · {stat.st_size / 1048576:.2f} MB</span></div>')
        return preview, str(info or text['metadata']), str(path), details
    except ValueError:
        return None, text['missing'], None, ''
    except (OSError, Image.DecompressionBombError) as error:
        return None, error_message('abrir imagem', error, language), None, ''
    except Exception as error:
        return None, error_message('abrir imagem', error, language), None, ''


def prepare_download(value, language):
    if not value:
        raise gr.Error(labels(language)['select_hint'])
    try:
        source = safe_path(value)
        folder = UI_CACHE / 'downloads'
        folder.mkdir(parents=True, exist_ok=True)
        # Separate original copies from reduced previews. Preserve exact bytes/name.
        target_dir = Path(tempfile.mkdtemp(prefix='original-', dir=folder))
        target = target_dir / source.name
        shutil.copyfile(source, target)
        return str(target)
    except Exception as error:
        raise gr.Error(error_message('preparar download', error, language)) from error


def export_page(paths, language):
    if not paths:
        return None
    files = [safe_path(value) for value in paths]
    if sum(path.stat().st_size for path in files) > MAX_EXPORT_BYTES:
        raise gr.Error(labels(language)['export_limit'])
    folder = Path(tempfile.gettempdir()) / 'axo-image-studio-exports'
    folder.mkdir(parents=True, exist_ok=True)
    # Keep only recent exports; generated source images are never deleted.
    import time
    for old in folder.glob('axo-images-*.zip'):
        if old.stat().st_mtime < time.time() - 86400:
            old.unlink(missing_ok=True)
    fd, name = tempfile.mkstemp(prefix='axo-images-', suffix='.zip', dir=folder)
    os.close(fd)
    with zipfile.ZipFile(name, 'w', compression=zipfile.ZIP_STORED) as archive:
        for index, path in enumerate(files, 1):
            archive.write(path, arcname=f'{index:03d}-{path.name}')
    return name


def initial_language():
    return 'pt-BR' if getattr(shared.opts, 'localization', '') == 'pt_BR' or os.environ.get('AXO_LANGUAGE') == 'pt-BR' else 'en'


@lru_cache(maxsize=1)
def banner_data():
    file = EXTENSION_ROOT / 'assets/banner.b64'
    return file.read_text().strip() if file.is_file() else ''


def header(language):
    text = labels(language)
    art = f'<div class="axo-mascot"><img src="data:image/png;base64,{banner_data()}" alt="Axolote rosa do Axo Image Studio" /></div>' if banner_data() else ''
    return (f'<section class="axo-header"><div class="axo-brand"><span class="axo-eyebrow">PEDROLTZ / CREATIVE WORKSPACE</span>'
            f'<h2>Axo <span>Image Studio</span></h2><p>{html.escape(text["tagline"])}</p>'
            '<a href="https://github.com/Pedroltz" target="_blank" rel="noopener noreferrer">'
            'by <strong>Pedroltz</strong> ↗</a></div>' + art + '</section>')


def source_choices(language):
    text = labels(language)
    return [(text['all'], 'all'), ('txt2img', 'txt2img'), ('img2img', 'img2img'),
            ('Extras', 'extras'), (text['grids'], 'grids'), (text['saved'], 'saved')]


def apply_language(language):
    text = labels(language)
    shared.opts.set('localization', 'pt_BR' if language == 'pt-BR' else 'None')
    shared.opts.save(shared.config_filename)
    return (
        header(language), text['notice'],
        gr.update(label=text['source'], choices=source_choices(language)),
        gr.update(label=text['search'], placeholder=text['search_hint']), gr.update(value=text['refresh']),
        gr.update(value=text['previous']), gr.update(value=text['next']),
        gr.update(label=text['gallery']), gr.update(label=text['preview']),
        gr.update(label=text['parameters']), gr.update(label=text['download']),
        gr.update(value=text['export']), gr.update(label=text['archive']),
        gr.update(label=text['language']), gr.update(value=text['apply']), gr.update(value=text['prepare']),
    )


def on_ui_tabs():
    if os.environ.get('AXO_ENABLE_GALLERY', '1') != '1':
        return []
    lang = initial_language()
    text = labels(lang)
    with gr.Blocks(analytics_enabled=False) as panel:
        heading = gr.HTML(header(lang))
        with gr.Accordion('Idioma / Language', open=False):
            with gr.Row():
                language = gr.Radio(choices=[('English', 'en'), ('Português', 'pt-BR')], value=lang, label=text['language'])
                apply = gr.Button(text['apply'])
            notice = gr.Markdown('')
        with gr.Row(elem_id='axo-toolbar'):
            source = gr.Dropdown(choices=source_choices(lang), value='all', label=text['source'], scale=1, min_width=160)
            search = gr.Textbox(label=text['search'], placeholder=text['search_hint'], scale=3)
            refresh = gr.Button(text['refresh'], variant='primary', elem_id='axo-refresh', scale=1, min_width=120)
        files = gr.State([])
        page = gr.State(0)
        selected_file = gr.State(None)
        with gr.Row(elem_id='axo-workspace', equal_height=False):
            with gr.Column(scale=3, min_width=320):
                gallery = gr.Gallery(label=text['gallery'], elem_id='axo-gallery', columns=3,
                                     height=590, object_fit='contain', preview=False, allow_preview=False,
                                     show_share_button=False, selected_index=None)
                with gr.Row(elem_id='axo-pagination'):
                    previous = gr.Button(text['previous'], interactive=False, min_width=95, scale=0)
                    status = gr.Markdown(text['empty'])
                    next_page = gr.Button(text['next'], interactive=False, min_width=95, scale=0)
            with gr.Column(scale=2, min_width=300, elem_id='axo-inspector'):
                preview = gr.Image(label=text['preview'], interactive=False, type='filepath', height=420,
                                   elem_id='axo-preview', show_share_button=False, show_download_button=False)
                details = gr.HTML(text['select_hint'])
                prepare = gr.Button(text['prepare'])
                download = gr.File(label=text['download'], interactive=False)
                with gr.Accordion('Prompt / Metadata', open=False):
                    parameters = gr.Textbox(label=text['parameters'], lines=8, max_lines=16, interactive=False, show_copy_button=True)
                with gr.Accordion('ZIP', open=False):
                    export = gr.Button(text['export'])
                    archive = gr.File(label=text['archive'], interactive=False)
        outputs = [gallery, files, page, status, preview, parameters, download, archive, details, previous, next_page, selected_file]
        def reset(source, query, lang):
            return page_data(source, query, 0, lang)
        # A nested Blocks load event is retained when Forge renders extension tabs.
        panel.load(reset, [source, search, language], outputs)
        for trigger in [refresh.click, search.submit, source.change]:
            trigger(reset, [source, search, language], outputs)
        previous.click(lambda source, query, page, lang: page_data(source, query, page - 1, lang), [source, search, page, language], outputs)
        next_page.click(lambda source, query, page, lang: page_data(source, query, page + 1, lang), [source, search, page, language], outputs)
        def select(paths, lang, event: gr.SelectData):
            preview_value, params, selected, info = show_image(paths, event.index, lang)
            return preview_value, params, selected, info, None
        gallery.select(select, [files, language], [preview, parameters, selected_file, details, download])
        prepare.click(prepare_download, [selected_file, language], download)
        export.click(export_page, [files, language], archive)
        apply.click(apply_language, language, [heading, notice, source, search, refresh, previous, next_page, gallery, preview, parameters, download, export, archive, language, apply, prepare]).then(reset, [source, search, language], outputs)
    return [(panel, 'Axo Studio', 'axo_studio')]


script_callbacks.on_ui_tabs(on_ui_tabs)
