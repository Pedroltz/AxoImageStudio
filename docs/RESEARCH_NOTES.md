# Pesquisa para a apresentação do Axo Image Studio

Fontes primárias consultadas em **12 de outubro de 2026**. As descrições abaixo ajudam a explicar a proposta do projeto e a separar os componentes externos das contribuições da extensão Axo.

## Base de geração

O Forge Neo continua a interface baseada no Stable Diffusion WebUI e reúne inferência, ferramentas de edição e suporte a modelos. O Axo utiliza essa base e acrescenta a galeria, o guia e a integração do notebook. A lista atual de recursos do Forge não equivale à compatibilidade de uma revisão fixada. [Fonte: repositório do Forge Neo](https://github.com/Haoming02/sd-webui-forge-classic).

O SDXL Base é um modelo de geração de imagens por difusão latente da Stability AI. O modelo base pode ser utilizado sem o refiner; o instalador Axo baixa o base. [Fonte: model card do SDXL](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0).

O Anima é voltado a anime, ilustração e arte, com arquivos específicos para modelo, text encoder e VAE. A documentação diferencia Base, Aesthetic e Turbo. No Axo, o download configurado é o Anima Base; a arte fotográfica de apresentação não é uma demonstração do Anima. [Fonte: model card do Anima](https://huggingface.co/circlestone-labs/Anima).

## Por que explicar os parâmetros

As escolhas de amostragem e distribuição dos níveis de ruído afetam o processo de geração. A documentação de Diffusers recomenda partir da configuração do checkpoint e respeitar a compatibilidade. Na interface Forge, a wiki explica separadamente os controles **sampler** e **scheduler**; a terminologia das bibliotecas pode agrupar funções de outra forma. [Fonte: documentação de schedulers do Diffusers](https://huggingface.co/docs/diffusers/en/using-diffusers/schedulers).

Isso sustenta a proposta didática do Axo Guide: explicar o efeito de cada controle, indicar exemplos e consultar a receita do modelo utilizado, sem apresentar um conjunto de parâmetros como universal.

## A correção da galeria

Na revisão usada pelo notebook, o Forge substitui a função de cache PIL do Gradio e consulta a pasta temporária configurada ao salvar a imagem. [Fonte: `modules/ui_tempdir.py` no commit fixado](https://github.com/Haoming02/sd-webui-forge-classic/blob/bd1d015950b62f1c88a6d95f0b9ea1e0dfc69aa3/modules/ui_tempdir.py).

A solução no Axo entrega caminhos de arquivos de cache locais para miniaturas e prévias e prepara o download original sob demanda. Essa explicação vem da inspeção do código do projeto e dos testes de regressão. Não é uma afirmação de aumento medido de velocidade de geração.

## Execução no Colab

A FAQ do Colab restringe o uso principal por WebUI em ambientes gratuitos sem saldo positivo de computação. A disponibilidade de GPU e a duração das sessões variam. O projeto documenta essa condição sem prometer execução gratuita contínua. [Fonte: FAQ oficial do Colab](https://research.google.com/colaboratory/faq.html).

## Decisões para o post

- Apresentar o projeto como integração e personalização de uma experiência de criação de imagens.
- Destacar entregas verificáveis: galeria, wiki com 29 artigos, notebook independente e testes locais.
- Creditar o Forge e os autores dos modelos utilizados.
- Descrever as artes como material conceitual externo à aplicação e a captura como prévia local da interface.
- Usar o endereço real do repositório e o botão para abrir o notebook no Colab.
- Registrar que os testes sem GPU não validam todas as combinações de modelos e extensões.
