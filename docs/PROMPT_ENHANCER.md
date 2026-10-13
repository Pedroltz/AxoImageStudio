# Prompts em pt-BR com um LLM local

O notebook oferece `huihui_ai/qwen3.5-abliterated:9b` como modelo inicial do
Prompt Enhancer. Ele é a recomendação da extensão e sua distribuição Ollama
é Q4_K_M, com download de aproximadamente 6,6 GB. Abliteration reduz recusas;
não é garantia de nenhuma recusa nem de qualidade superior em todas as tarefas.
Os pesos ocupam RAM adicional durante o uso, além do download e do Forge.

O modelo base Qwen3.5 é multilíngue. Isso é uma razão para avaliá-lo com entrada
em português, mas os benchmarks do modelo original não comprovam a qualidade
da variante abliterated em pt-BR. Esse teste ainda deve ser feito no Colab.

## Pesquisa da comunidade

Fontes consultadas em 13 de outubro de 2026:

| Fonte | O que oferece | Decisão no Axo |
|---|---|---|
| [Gunther-Schulz: bases.yaml na revisão fixada](https://github.com/Gunther-Schulz/sd-webui-prompt-enhancer/blob/349f28e61780472816b9f688dc2af635eee35e8f/bases.yaml) | Base de expansão em linguagem natural, preservação dos detalhes e formato sem comentários | Manter a base Default disponível e o mecanismo nativo de bases YAML |
| [PinkPixel: prompts.py](https://github.com/pinkpixel-dev/comfyui-llm-prompt-enhancer/blob/36d5172c93d4f40c0592be469584b0f23517b3fc/prompts.py) | System prompts separados para prosa e frases/tags SDXL | Usar a distinção entre formatos para projetar uma base própria e compacta para SDXL |
| [Wujidadi: preset Anima](https://github.com/Wujidadi/text-to-image-prompt-enhancer/blob/475d1de08365096c575d1ac21e1baaf161e3b44e/src/prompt_enhancer/enhancers/anima.txt) | Instruções específicas para tags e linguagem natural Anima | Consultar como referência; não importar suas regras integralmente |
| [Documentação oficial do Anima](https://huggingface.co/circlestone-labs/Anima#prompting) | Tags com espaços, prefixo de artistas e suporte a descrições em linguagem natural | Preferir descrição com pelo menos duas frases; normalizar apenas tags fornecidas |
| [Modelo Ollama](https://ollama.com/huihui_ai/qwen3.5-abliterated:9b) e [Qwen3.5-9B original](https://huggingface.co/Qwen/Qwen3.5-9B) | Variante com recusas reduzidas; família multilíngue | Usar o 9b com modelo configurável e registrar limites de memória e validação |

Esses projetos confirmam que system prompts de geração de imagens já existem.
Eles são instruções enviadas a cada chamada do LLM; não treinam novos pesos.
A integração Axo usa instruções próprias, sem copiar integralmente prompts de
terceiros. Não há evidência de que uma base seja universalmente a melhor.

Um exemplo de divergência: o preset comunitário Anima proíbe pesos numéricos,
enquanto a documentação oficial diz que pesos funcionam. Também exige um
rating, ano e bloco de código. O Axo não impõe esses detalhes nem mistura regras
de Pony/Illustrious com SDXL genérico. Os scores podem variar conforme a versão
do Anima; as bases não inventam scores ou escolhem um rating pelo usuário.

## Uso integrado

1. Marque `ENABLE_PROMPT_ENHANCER` na instalação.
2. Mantenha o backend `local` para baixar e iniciar o modelo no Colab em CPU.
3. Mantenha `PROMPT_ENHANCER_BASE = 'Auto'`: `START_WITH = 'SDXL'` seleciona
   **Axo SDXL - PT-BR**; `START_WITH = 'Anima'` seleciona **Axo Anima - PT-BR**.
4. Em **Source Prompt**, escreva a cena em português. Clique em **Enhance**, revise
   o resultado em inglês e então use **Generate**.
5. Use **Edit** para alterações em português. A instrução de edição mantém o
   formato e os detalhes não afetados. **Keep LoRAs** conserva os tokens LoRA.

As bases orientam o modelo a preservar nomes, contagens e relações espaciais.
Textos solicitados dentro da imagem ficam no idioma original; por exemplo,
`uma loja com a placa "Pão de Açúcar"` deve manter a frase da placa.
A saída em inglês é uma escolha de compatibilidade dos perfis; não significa
que você precisa escrever em inglês ou que todo modelo de imagem rejeita pt-BR.

**Auto vale para a família inicial na instalação**, não acompanha mudanças
posteriores de checkpoint. Ao trocar SDXL/Anima na WebUI, mude também o campo
**Base**. Você pode escolher explicitamente uma base no notebook.
**Default** mantém o corpo de prosa da comunidade, combinado com a orientação
Axo de entrada em português e saída em inglês.

## Personalização e persistência

O Axo grava seus arquivos em `prompt-enhancer-axo/_bases.yaml` e
`prompt-enhancer-axo/_prompts.yaml` na pasta raiz. Esses arquivos são gerenciados
pela instalação. Sua pasta `prompt-enhancer` é carregada **depois**, e portanto
seus arquivos `_bases.yaml` e `_prompts.yaml` podem sobrescrever as instruções.
Os arquivos pessoais não são substituídos ao reinstalar; ambos os diretórios
persistem quando o Drive está habilitado. Edite seus arquivos e clique em
**Reload**; novos grupos de modificadores exigem **Restart**.

## Validação pendente com o LLM

Os testes locais verificam distribuição dos YAMLs, seleção das bases,
preservação dos arquivos pessoais e carregamento na extensão com Gradio.
Eles não medem qualidade de linguagem nem geração de imagens.

No Colab, testar ao menos:

- uma descrição em pt-BR com duas pessoas, posições e cores distintas;
- uma placa com texto acentuado, que deve permanecer em português;
- uma edição em pt-BR que altera apenas luz ou fundo;
- SDXL e Anima, inclusive troca manual de Base após trocar checkpoint;
- Keep LoRAs, Cancel e negativos opcionais;
- consumo de RAM e tempo em CPU com o 9b; reduzir modelo ou usar backend externo se necessário.

Uma frase repetida, detalhes alterados ou textos traduzidos indevidamente são
falhas a corrigir na instrução ou no modelo; os perfis não garantem fidelidade.

A seleção inicial também é aplicada ao código da UI da extensão: o Forge Neo
fixado compara rótulos de opções com seus valores ao restaurar dropdowns,
e os rótulos decorados de Base são diferentes dos valores. A adaptação garante
que a base inicial e sua descrição correspondam à escolha do notebook.
