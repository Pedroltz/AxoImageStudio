# Créditos e componentes externos

O Axo Image Studio personaliza e integra ferramentas existentes. O motor de geração, as bibliotecas, os modelos e as extensões abaixo pertencem aos seus respectivos projetos. Os links dos projetos são a referência para as licenças e condições de uso de cada componente.

| Componente | Papel | Referência |
|---|---|---|
| Forge Neo | Interface base e inferência | [Haoming02/sd-webui-forge-classic](https://github.com/Haoming02/sd-webui-forge-classic) |
| Stable Diffusion WebUI | Recursos e sintaxe herdados pelo Forge | [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) |
| ADetailer Neo | Detalhamento automático | [Haoming02/ADetailer-Neo](https://github.com/Haoming02/ADetailer-Neo) |
| CivBrowser | Navegação e download de modelos | [SignalFlagZ/sd-webui-civbrowser](https://github.com/SignalFlagZ/sd-webui-civbrowser) |
| Localização pt-BR | Tradução da interface base | [M-art-ucci/stable-diffusion-webui-localization-pt_BR](https://github.com/M-art-ucci/stable-diffusion-webui-localization-pt_BR) |
| Gradio | Componentes e transporte da interface | [gradio-app/gradio](https://github.com/gradio-app/gradio) |
| PyTorch | Execução de modelos na GPU | [pytorch/pytorch](https://github.com/pytorch/pytorch) |
| SDXL Base | Modelo base SDXL | [stabilityai/stable-diffusion-xl-base-1.0](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) |
| Anima | Modelo e módulos Anima | [circlestone-labs/Anima](https://huggingface.co/circlestone-labs/Anima) |

## Revisões fixadas no instalador

| Projeto | Commit |
|---|---|
| Forge Neo | `bd1d015950b62f1c88a6d95f0b9ea1e0dfc69aa3` |
| ADetailer Neo | `af228eba7a3f3691a25bcd1fc94aa95e600dd3e6` |
| CivBrowser | `7c9c32040722ee125cebb9bc3c9454322b14a2a3` |

O notebook baixa esses componentes na sessão do Colab. O repositório distribui a extensão Axo e o instalador, sem os pesos de modelos e sem uma cópia completa do Forge. Outros pesos e pré-processadores baixados pelo instalador têm referências no código e continuam sujeitos às condições de seus autores.

Os exemplos da wiki são orientações didáticas; resultados e configurações dependem do modelo. A arte de identidade visual foi preservada do notebook fornecido para este projeto; a captura de interface em `docs/assets` mostra o Axo Guide.
