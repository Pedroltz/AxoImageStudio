# Axo Image Studio

**Crie, explore e entenda suas imagens.** Um estúdio para Google Colab com galeria própria e uma wiki integrada em português, personalizado por **Pedroltz** sobre o Forge Neo.

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Pedroltz/AxoImageStudio/blob/main/Axo_Image_Studio.ipynb)
[![Verificações da interface e do notebook](https://github.com/Pedroltz/AxoImageStudio/actions/workflows/validate.yml/badge.svg)](https://github.com/Pedroltz/AxoImageStudio/actions/workflows/validate.yml)

![Prévia do Axo Guide: busca, índice de artigos e explicação de samplers](docs/assets/axo-guide.jpg)

*Captura do Axo Guide em uma prévia local da interface, com os módulos de inferência simulados.*

[Começar no Colab](#começar-no-colab) · [Wiki completa](docs/AXO_GUIDE.md) · [Artes e prompts](docs/DEMOS.md) · [Arquitetura](docs/ARCHITECTURE.md) · [Apresentação no LinkedIn](docs/LINKEDIN_POST.md)

## O projeto

Gerar imagens envolve muitos controles: modelos, prompts, samplers, steps, CFG e extensões. O Axo Image Studio reúne um ambiente de criação, uma biblioteca para explorar os resultados e um guia que explica esses controles durante o uso.

O projeto também resolve um problema encontrado na galeria no Colab: miniaturas e prévias passavam pela pasta temporária global do Forge e podiam falhar no carregamento. A galeria própria usa arquivos em um cache local separado e prepara o download original somente quando solicitado.

### A contribuição do Axo

O Forge oferece o motor de geração e suas ferramentas de edição. O Axo adiciona a biblioteca de imagens, o guia em português, a identidade visual e a preparação do ambiente no Colab. O código da galeria e da wiki fica disponível separadamente, além de incorporado ao notebook.

## O que você encontra

| Área | Recursos |
|---|---|
| **Criação** | txt2img, img2img e Inpaint do Forge; configuração para SDXL e Anima |
| **Axo Studio** | Biblioteca com filtros, busca por nome, 24 imagens por página e atualização ao entrar na aba |
| **Prévia e download** | Prévia reduzida, leitura dos parâmetros, download do arquivo original e exportação da página em ZIP |
| **Axo Guide** | 29 artigos em português, busca no conteúdo, categorias e navegação anterior/próxima |
| **Complementos** | Instalação/configuração de ControlNet, ADetailer Neo e CivBrowser |
| **Colab** | Ambiente Python 3.12 isolado, revisões fixadas e opção de persistência no Google Drive |

A wiki explica cada aba e os conceitos de prompts, pesos, prompt negativo, samplers, schedulers, steps, CFG, seed, resolução, Hires fix, LoRAs e Inpaint. Inclui exemplos e referências às fontes originais.

## Artes de apresentação

| Mascote 3D | Fantasia ilustrada | Estilo fotográfico |
|---|---|---|
| ![Axolote rosa sobre um computador retrô](docs/demos/01-mascote-3d.png) | ![Axolote em uma estufa fantástica](docs/demos/02-fantasia-ilustrada.png) | ![Axolote em um cenário subaquático](docs/demos/03-fotografia-subaquatica.png) |

Essas artes foram geradas com uma ferramenta externa para a apresentação do projeto. Os [arquivos e prompts completos](docs/DEMOS.md) estão disponíveis para explorar as ideias no Axo; os resultados dependem do modelo e dos parâmetros.

## Começar no Colab

O uso principal por uma WebUI é restrito em ambientes gratuitos do Colab sem saldo positivo de unidades de computação. Confira os requisitos atuais de execução na [FAQ oficial do Colab](https://research.google.com/colaboratory/faq.html). GPU e duração da sessão variam conforme disponibilidade e plano.

1. Clique em [**Abrir no Colab**](https://colab.research.google.com/github/Pedroltz/AxoImageStudio/blob/main/Axo_Image_Studio.ipynb).
2. Salve uma cópia no seu Drive se quiser guardar as alterações do notebook.
3. Selecione **Ambiente de execução → Alterar tipo de ambiente de execução → GPU**.
4. Na célula **Install and launch**, escolha o idioma, o modelo inicial e a opção de Google Drive.
5. Execute a célula e abra o endereço `gradio.live` exibido ao final da inicialização. Mantenha a célula em execução durante o uso.
6. Confira o **UI Preset**, o checkpoint e os módulos do modelo. Abra **Axo Guide** para um primeiro teste e **Axo Studio** para explorar as imagens.

O notebook é independente: os arquivos da extensão já estão incluídos nele. Não é necessário enviar a pasta do repositório ao Colab.

Você também pode baixar [Axo_Image_Studio.ipynb](Axo_Image_Studio.ipynb) e usar **Arquivo → Fazer upload de notebook** no Colab.

### Downloads e persistência

Os downloads de SDXL e Anima estão habilitados por padrão. Para usar só uma família, desative os downloads da outra e os complementos que não vai utilizar. A primeira execução instala dependências e baixa os modelos; o tempo depende da GPU, da conexão e das opções escolhidas.

Com `USE_GOOGLE_DRIVE = True`, modelos e imagens ficam em `MyDrive/Axo-Image-Studio-Forge`. Sem essa opção, ficam no armazenamento temporário da sessão do Colab. O ambiente Python é reconstruído em uma nova sessão.

Se um download do Civitai exigir autenticação, use os **Segredos do Colab** com o nome `CIVITAI_TOKEN`.

### Prompts em linguagem natural (opcional)

Marque `ENABLE_PROMPT_ENHANCER` na célula de instalação. A extensão
[Prompt Enhancer](https://github.com/Gunther-Schulz/sd-webui-prompt-enhancer)
transforma descrições e instruções em prompts por meio do Ollama. Ela começa
**desativada**, para manter os downloads e o consumo de memória habituais.

| Opção | Comportamento |
|---|---|
| `PROMPT_ENHANCER_BACKEND = 'local'` | Instala Ollama `v0.40.3`, inicia no Colab em CPU e baixa o modelo antes de abrir o Forge |
| `PROMPT_ENHANCER_BACKEND = 'external'` | Usa um servidor Ollama já acessível pelo Colab; não instala Ollama nem baixa modelos |
| `PROMPT_ENHANCER_API_URL` | URL base do Ollama; no modo local, use `http://127.0.0.1:11434` |
| `PROMPT_ENHANCER_MODEL` | Modelo Ollama, inicialmente `qwen3:4b`; pode escolher outro modelo conforme a RAM disponível |

No modo local, a primeira execução baixa também o pacote Ollama (~1,4 GB)
e os pesos do LLM (vários GB). O modelo 4b é uma escolha de menor consumo;
qualidade e velocidade precisam ser avaliadas para seus prompts. O upstream
recomenda um modelo 9b, que exige mais RAM. A execução em CPU pode demorar;
os limites de espera são 60 segundos sem tokens e 300 segundos por chamada.
Ollama fica restrito à interface local, sem acesso à GPU, e libera o modelo
após a chamada. Veja as [configurações oficiais do Ollama](https://docs.ollama.com/faq).

No modo externo, baixe o modelo no servidor previamente (`ollama pull NOME`).
A URL precisa ser acessível **a partir do Colab**: `localhost` não aponta para
seu computador pessoal. Use uma URL base sem `/api/chat`, credenciais ou
parâmetros; a extensão não oferece campos de autenticação. Os prompts são
enviados ao servidor escolhido.

Abra **Prompt Enhancer** em **txt2img** ou **img2img**, escreva em **Source Prompt**
e clique em **Enhance**. Revise o texto no campo principal e então clique em
**Generate** no Forge. **Edit** altera um prompt existente; **Keep LoRAs** mantém
os tokens LoRA. Escolha a **Base** apropriada ao modelo de imagem: a extensão
não troca automaticamente sua base quando você muda entre SDXL e Anima.

Com Drive habilitado, os pesos Ollama ficam em `models/Ollama` e os arquivos
YAML pessoais em `prompt-enhancer`, dentro da pasta do Axo no Drive. Sem Drive,
eles duram apenas a sessão. A pasta de YAML é criada antes de carregar a
extensão; os modelos Qwen do Ollama são separados do encoder Qwen do Anima.

**Restart** inicia novamente Ollama e Forge. Interromper a célula encerra os
serviços iniciados pelo Axo; um servidor externo continua ativo. Para desativar
ou alterar backend/modelo/URL, interrompa e execute **Install and launch** com
as novas opções. As opções atualizam apenas os padrões API URL/Model da
extensão; as demais configurações da interface são preservadas.

### Atualizar ou reiniciar

Para aplicar mudanças do notebook, interrompa o Forge e execute **Install and launch** novamente. Para reiniciar na mesma instalação, use **Restart**. Downloads já concluídos são reaproveitados.

## Resolver problemas

| Sintoma | O que conferir |
|---|---|
| Galeria ou prévia mostra erro | Interrompa a célula sem excluir a sessão e execute **Diagnosticar galeria** no fim do notebook |
| Uma imagem nova não aparece | Clique em **Atualizar** e confira a pasta de saída configurada no Forge |
| Modelo Anima não carrega corretamente | Confira os módulos Qwen 0.6B e Qwen Image VAE no capítulo de modelos da wiki |
| Falta de memória na GPU | Use batch 1, reduza a resolução, desative Hires fix e mantenha `LOW_VRAM` ativado |
| Aviso de `detached symbolic reference` no CivBrowser | Consulte a [explicação do aviso](docs/TROUBLESHOOTING.md); ele se refere à leitura da branch Git de uma revisão fixada |

## Estrutura do repositório

```text
axo-image-studio/
├── Axo_Image_Studio.ipynb     # Notebook pronto para o Colab
├── axo_launcher.py           # Fonte da célula de instalação
├── extension/                # Interface, galeria, wiki e identidade visual
│   ├── scripts/
│   ├── javascript/
│   ├── assets/
│   └── style.css
├── docs/                     # Wiki, arquitetura, apresentação e prévia
├── tools/build_notebook.py   # Incorpora as fontes no notebook
└── tests/                    # Verificações locais sem inferência com GPU
```

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para editar a interface, atualizar o notebook e executar as verificações. O workflow em `.github/workflows/validate.yml` executa as verificações no GitHub Actions a cada push e pull request.

## Validação e limites

A correção da galeria foi confirmada em uso no Colab. Os testes locais verificam carregamento em abas Gradio, filtros, paginação, prévias, metadados, download original, ZIP, busca e navegação da wiki. Também verificam se o notebook contém as mesmas fontes mantidas no repositório. Um teste adicional em JavaScript verifica a atualização ao entrar e retornar à aba.

Os testes locais não geram imagens com GPU. A inferência completa e todas as combinações de modelos/extensões ainda precisam de testes específicos. A referência de pose do Anima é experimental. A captura acima mostra o guia; as imagens usadas nos testes são sintéticas.

## Autoria e créditos

**Pedroltz** — personalização da interface, galeria, integração do notebook e Axo Guide.

A geração de imagens usa o [Forge Neo](https://github.com/Haoming02/sd-webui-forge-classic), modelos de terceiros e extensões. Este repositório não contém pesos de modelos. Consulte [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) para as referências e revisões utilizadas.

As [notas de pesquisa](docs/RESEARCH_NOTES.md) registram as fontes oficiais consultadas e as decisões de apresentação. A compatibilidade do notebook corresponde às revisões fixadas no instalador, e não a todos os recursos das versões mais recentes dos projetos externos.
