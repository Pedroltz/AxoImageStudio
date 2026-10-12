# Desenvolver e verificar

O notebook é o arquivo de distribuição. As fontes editáveis ficam em `axo_launcher.py` e `extension/`; alterações nesses arquivos precisam ser incorporadas ao notebook antes de distribuí-lo.

## Ambiente de desenvolvimento

Use **Python 3.12** para manter compatibilidade com as versões utilizadas pelo projeto. Os testes da interface não precisam de GPU nem baixam modelos.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

O Node.js é usado apenas para a verificação do comportamento de atualização da aba.

## Onde editar

| Mudança | Arquivo |
|---|---|
| Instalação, configuração ou inicialização no Colab | `axo_launcher.py` |
| Galeria, filtros, cache, metadados e downloads | `extension/scripts/axo_gallery.py` |
| Conteúdo, busca e navegação da wiki | `extension/scripts/axo_guide.py` |
| Aparência da interface | `extension/style.css` |
| Atualização ao entrar na aba | `extension/javascript/axo_gallery.js` |
| Instruções introdutórias ou células de diagnóstico | `Axo_Image_Studio.ipynb` |

Se alterar os artigos da wiki, atualize também `docs/AXO_GUIDE.md`. O conteúdo HTML e Python incorporado ao notebook continua independente do repositório.

## Gerar o notebook

```bash
python tools/build_notebook.py
python tools/build_notebook.py --check
```

O primeiro comando incorpora os arquivos da extensão e a fonte do instalador. O segundo detecta diferenças sem modificar arquivos. A geração remove as saídas de execução das células; não executa o instalador.

## Verificar

```bash
GRADIO_ANALYTICS_ENABLED=False python -m pytest -q
node tests/test_refresh.cjs
```

As verificações cobrem comportamentos da galeria e da wiki, incluindo a regressão de prévias quando um hook de cache PIL tenta usar uma pasta temporária inexistente. Os módulos de inferência do Forge são simulados nos testes locais; isso não substitui uma sessão real com GPU.

Para uma mudança no instalador ou nos modelos, valide também no Colab: inicialização, seleção de módulos, uma geração pequena, visualização, download e persistência no Drive quando habilitada.

## Publicar o repositório depois

Este projeto foi preparado como um repositório **local**, sem envio ao GitHub. Quando quiser publicá-lo, crie um repositório vazio na sua conta e configure o endereço dele como `origin`:

```bash
git remote add origin https://github.com/SEU_USUARIO/axo-image-studio.git
git push -u origin main
```

Substitua `SEU_USUARIO` pelo nome da sua conta. A documentação já usa caminhos relativos para funcionar no GitHub. Modelos, imagens geradas, ambientes locais, logs e credenciais estão excluídos pelo `.gitignore`.
