# Axo Guide · Wiki de Pedroltz

29 artigos para entender e usar o Axo Image Studio.

## Índice

- 01 · Primeiros passos e mapa das abas — Começar
- 02 · Checkpoint, preset, VAE e famílias — Começar
- 03 · txt2img: criar do zero — Abas e ferramentas
- 04 · Como construir um prompt — Prompts
- 05 · Negative prompt: como e quando usar — Prompts
- 06 · Pesos, parênteses e sintaxe avançada — Prompts
- 07 · Prompts para Anima Base e variantes — Prompts
- 08 · Sampler e scheduler: o que cada um faz — Amostragem e qualidade
- 09 · Steps, CFG, denoise e Shift — Amostragem e qualidade
- 10 · Seed, resolução e batch — Amostragem e qualidade
- 11 · Hires fix: ampliar durante a geração — Amostragem e qualidade
- 12 · img2img: transformar uma imagem — Abas e ferramentas
- 13 · Inpaint: corrigir uma região — Abas e ferramentas
- 14 · Sketch, Inpaint sketch, upload e Batch — Abas e ferramentas
- 15 · ControlNet: pose e estrutura — Complementos
- 16 · ADetailer: rosto e mãos — Complementos
- 17 · LoRAs, cartões e palavras de ativação — Complementos
- 18 · CivBrowser: encontrar e baixar modelos — Abas e ferramentas
- 19 · Extras: ampliar uma imagem pronta — Abas e ferramentas
- 20 · PNG Info: recuperar e repetir uma geração — Abas e ferramentas
- 21 · Axo Studio: biblioteca e downloads — Abas e ferramentas
- 22 · Scripts e comparação X/Y/Z — Complementos
- 23 · Checkpoint Merger: mistura de modelos — Abas e ferramentas
- 24 · Settings e controles do workspace — Abas e ferramentas
- 25 · Extensions e versões fixadas — Abas e ferramentas
- 26 · Receitas de teste e fluxo de trabalho — Aprender e resolver
- 27 · Problemas comuns e diagnóstico — Aprender e resolver
- 28 · Glossário rápido — Aprender e resolver
- 29 · Fontes e como usar este guia — Aprender e resolver

---

# Primeiros passos

O Axo Studio usa o Forge para gerar e editar imagens. Cada aba cobre uma etapa: criar, corrigir, ampliar ou organizar. Este guia pode ser consultado enquanto você trabalha.

## Um primeiro teste simples

1. No topo, escolha **UI Preset** `xl` ou `anima` e um **Checkpoint** da mesma família.
2. Confira **VAE / Text Encoder** no capítulo de modelos.
3. Abra **txt2img**, escreva um prompt curto e escolha uma resolução moderada.
4. Use **Batch size = 1**. Para entender o resultado inicial, desative Hires fix, ADetailer e ControlNet.
5. Clique em **Generate**. Depois, ajuste uma coisa de cada vez.

## Para onde ir

| Quero… | Abrir… |
|---|---|
| Criar a partir de texto | txt2img |
| Transformar uma imagem | img2img |
| Corrigir apenas uma região | img2img → Inpaint |
| Aumentar uma imagem pronta | Extras |
| Recuperar o prompt e as configurações | PNG Info |
| Procurar checkpoints e LoRAs | CivBrowser |
| Explorar e baixar minhas imagens | Axo Studio |
| Entender os controles | Axo Guide |
| Comparar modelos por mistura de pesos | Checkpoint Merger |
| Configurar interface e salvamento | Settings |
| Consultar extensões instaladas | Extensions |

**ControlNet** e **ADetailer** são painéis dentro das abas de geração. **LoRA**, **Styles** e cartões de modelos ficam nos painéis de redes adicionais; a posição depende do layout escolhido.

Use a busca à esquerda: ela procura nos títulos e no texto dos artigos. Os nomes dos controles aparecem em inglês e português para ajudar a encontrá-los na interface.

---

# Escolher e carregar o modelo

**Checkpoint** é o modelo principal. Ele influencia os estilos que a aplicação consegue criar e como interpreta o prompt. **UI Preset** organiza os controles e lembra o modelo e os módulos daquela família.

| Família | Preset deste notebook | VAE / Text Encoder |
|---|---|---|
| SDXL Base, Illustrious e Pony baseados em SDXL | `xl` | VAE SDXL compatível; retire os módulos Qwen do Anima |
| Anima | `anima` | Selecione **qwen_3_06b_base.safetensors** e **qwen_image_vae.safetensors** juntos |

O notebook baixa SDXL Base e Anima Base quando suas opções de download estão habilitadas. Illustrious, Pony e outros derivados precisam ser baixados separadamente.

## O papel de cada arquivo

- **Checkpoint:** produz a representação interna da imagem durante a geração.
- **Text encoder:** transforma seu texto em informações que o modelo entende. Anima usa um módulo separado; o SDXL deste fluxo usa os encoders do checkpoint.
- **VAE:** converte a representação interna em pixels e também codifica imagens de entrada para img2img.
- **LoRA:** é um complemento aplicado ao modelo; ela não substitui o checkpoint.

## Antes de trocar de família

Selecione o preset, o checkpoint e os módulos corretos. Revise LoRAs, ControlNet, prompts e valores de geração. Um complemento que funciona em SDXL pode ser incompatível com Anima. Dentro de SDXL, derivados também podem responder melhor às LoRAs treinadas para sua base específica.

Se surgir erro de dimensões de tensores, confirme essas combinações antes de mexer nos parâmetros de qualidade. Para cores muito estranhas, confira o VAE e se o erro acontece com o modelo sem complementos.

[Arquivos do Anima](https://huggingface.co/circlestone-labs/Anima) · [Modelos no Forge](https://github.com/Haoming02/sd-webui-forge-classic/wiki/Download-Models)

---

# txt2img

Esta aba começa com ruído e usa o texto e as configurações para construir uma imagem. É o lugar para testar ideias, personagens, composições e estilos.

## Controles principais

| Controle | O que muda |
|---|---|
| Prompt | O que você quer representar |
| Negative prompt | Características que deseja reduzir |
| Sampling method / Sampler | O método usado para atualizar a imagem a cada etapa |
| Schedule type / Scheduler | Como os níveis de ruído são distribuídos entre as etapas |
| Sampling steps | Quantas etapas serão executadas |
| CFG Scale | A intensidade da orientação pelo texto |
| Width / Height | Largura e altura da imagem inicial |
| Seed | O número usado para iniciar o ruído |
| Batch count | Quantos lotes executar em sequência |
| Batch size | Quantas imagens produzir de uma vez por lote |

## Um jeito útil de testar

Escreva a cena, escolha uma configuração inicial no artigo **Receitas**, gere algumas opções e escolha uma composição. Guarde a seed dessa imagem. Em seguida, mantenha a seed e altere somente o prompt, o CFG ou o sampler para observar o efeito.

O painel do resultado costuma permitir salvar a imagem e enviá-la para **img2img**, **Inpaint**, **Extras** ou **PNG Info**. Esses atalhos reaproveitam a imagem e, quando disponível, seus parâmetros.

**Interrupt** interrompe o trabalho atual. **Skip**, quando disponível, tenta pular a geração corrente. Não use o número de steps como única medida de qualidade: o resultado também depende do modelo, da resolução, da composição e do método de amostragem.

---

# O sistema de prompt

Um prompt descreve a imagem desejada. Ele serve como orientação para o modelo, e não como uma lista de comandos com execução garantida. Uma descrição clara ajuda a reduzir interpretações concorrentes.

## Uma estrutura fácil de usar

**Assunto + aparência + ação + ambiente + enquadramento + iluminação + estilo.**

Exemplo em linguagem natural:

```text
A small pink axolotl sits on top of a vintage computer in a cozy studio.
The computer screen shows a mountain sunset. Medium shot, warm soft light,
pastel colors, clean digital illustration.
```

A mesma ideia em tags:

```text
pink axolotl, vintage computer, cozy studio, mountain sunset on screen,
medium shot, warm lighting, pastel colors, digital illustration
```

Os exemplos estão em inglês como ponto de partida. Você pode experimentar português; a compreensão e os detalhes variam com o checkpoint.

## Refinar sem perder o controle

1. Comece pelo assunto e a composição.
2. Acrescente detalhes visuais que realmente fazem diferença.
3. Evite contradições como `close-up` e `full body` para o mesmo enquadramento.
4. Se houver dois personagens, descreva cada um e sua posição: esquerda, direita, primeiro plano.
5. Acrescente o estilo e a luz. Compare com a mesma seed.

Não existe uma ordem de palavras que funcione melhor em todos os modelos. Tags de qualidade, nomes de personagens e palavras de ativação dependem do treinamento do checkpoint e da LoRA.

## Styles e tokens

**Styles** são textos salvos que a interface adiciona aos prompts. Confira o que o estilo insere, inclusive no negativo, antes de combinar várias opções.

O contador de **tokens** estima como o texto será dividido pelo encoder; ele não conta simplesmente palavras. SDXL e Anima usam encoders diferentes. Um texto longo pode exigir mais processamento e tornar a intenção menos clara. Reorganize a descrição antes de continuar acrescentando adjetivos.

Consulte os artigos **Pesos e sintaxe** e **Prompts para Anima** para diferenças importantes.

---

# Negative prompt

O prompt negativo orienta o modelo a reduzir características indesejadas. Ele não recorta objetos nem garante a ausência de um defeito.

Um começo simples para um teste de ilustração:

```text
blurry, jpeg artifacts, low quality
```

Depois, inclua somente problemas que aparecem no resultado: por exemplo, `text` ou `watermark` quando você não quer esses elementos. Um negativo muito grande pode afetar o estilo ou eliminar características desejadas.

## Evite estes atalhos

- **Listas enormes copiadas de outro checkpoint:** palavras úteis em uma base podem ter outro efeito na sua.
- **Embeddings incompatíveis:** escrever o nome de um embedding só carrega seu efeito se o arquivo estiver instalado e for compatível. Um embedding de SD 1.5 não é uma solução geral para SDXL ou Anima.
- **Tentar resolver toda a anatomia com texto:** pose, resolução, composição, ADetailer e Inpaint também influenciam o resultado.

## Um teste controlado

Guarde a seed e gere com o negativo vazio. Depois, use um negativo curto. Compare a composição e os detalhes, sem alterar o resto da configuração. Assim você descobre se a lista está ajudando.

Em modelos acelerados que usam CFG próximo de 1, o negativo pode ter pouco efeito ou um funcionamento diferente. Use a receita do checkpoint. Para Anima Base, veja o artigo dedicado; a variante Aesthetic usa orientações diferentes para tags de qualidade.

---

# Pesos e sintaxe do prompt

A interface possui um interpretador de prompt. Algumas marcações modificam a ênfase; outras ativam complementos. O comportamento depende do modelo e da configuração **Emphasis**.

| Sintaxe | Intenção |
|---|---|
| `(red hair)` | Aumentar a ênfase no trecho |
| `(red hair:1.2)` | Dar um peso explícito ao trecho |
| `(red hair:0.8)` | Reduzir sua ênfase |
| `[red hair]` | Reduzir a ênfase na sintaxe tradicional |
| `\(red hair\)` | Usar parênteses como texto literal |
| `<lora:nome_do_arquivo:0.7>` | Ativar uma LoRA instalada com esse peso |

**Peso do prompt, peso da LoRA e CFG são controles diferentes.** O primeiro enfatiza texto; o segundo regula o complemento; o terceiro regula a orientação geral pelo texto.

Para um SDXL comum, experimente primeiro um peso leve, como `1.1` ou `1.2`. São sugestões de teste deste guia. Pesos altos podem deformar atributos ou dominar a composição. O Anima tem uma resposta diferente; compare pequenas mudanças na mesma seed antes de exagerar.

## Recursos avançados da interface

Na sintaxe herdada do A1111, `[day:night:0.5]` troca o condicionamento durante a amostragem; `AND` permite combinar condicionamentos. `BREAK` é usado em fluxos CLIP para separar blocos de texto.

Esses recursos são avançados. Não presuma que os efeitos serão iguais entre o encoder CLIP do SDXL e o Qwen do Anima. Para aprender, comece com descrição comum e pesos simples. Evite usar todas as marcações ao mesmo tempo.

[Referência de sintaxe](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Features#attentionemphasis)

---

# Prompts para Anima

O **Anima Base** trabalha com tags e descrições em linguagem natural. Para uma cena com vários elementos, experimente uma descrição completa em duas frases ou uma combinação de tags e frases.

## Exemplo para Anima Base

```text
masterpiece, best quality, score_7, safe,
a small pink axolotl resting on a vintage computer.
The screen shows a sunset over mountains. The room is a cozy art studio,
with warm light and a soft pastel palette. Clean digital illustration.
```

Negativo para experimentar:

```text
worst quality, low quality, blurry, jpeg artifacts
```

As tags de qualidade acima seguem a orientação do autor para **Base**. Elas não são uma fórmula obrigatória. Experimente com e sem o prefixo, mantendo o resto igual.

## Quando a variante muda

| Variante | Como tratar |
|---|---|
| Base | A versão baixada por padrão neste notebook; permite explorar diferentes estilos |
| Aesthetic | Tem orientações próprias para tags de qualidade; evite copiar todas as tags `score_*` da Base |
| Turbo | Usa uma receita de geração acelerada; o autor indica CFG 1 e 8–12 steps |
| Outros derivados | Leia a página da versão exata que você baixou |

O Anima tende a trabalhar melhor com ilustração e arte. Para uma fotografia realista, considere um checkpoint apropriado a esse objetivo. Ao escrever texto dentro da imagem, prefira poucas palavras e revise o resultado.

O preset `anima` precisa dos módulos Qwen e VAE corretos. Se a imagem sai errada, confira os arquivos antes de tentar compensar tudo com o prompt.

[Orientações do autor do Anima](https://huggingface.co/circlestone-labs/Anima#prompting)

---

# Sampler e scheduler

Durante a geração, o modelo produz estimativas que ajudam a transformar o ruído em imagem. O **sampler** define como usar essas estimativas em cada etapa. O **scheduler** define quais níveis de ruído serão visitados e como eles serão espaçados.

Uma analogia: o sampler é a forma de dar cada passo; o scheduler é a distribuição das paradas ao longo do percurso. Mudar qualquer um pode mudar o resultado, mesmo com a mesma seed.

## Samplers que você pode encontrar

| Nome | Como interpretar e experimentar |
|---|---|
| Euler | Método simples; útil como referência de comparação |
| Euler a | Variante ancestral, que adiciona ruído ao longo do processo; pode explorar outros resultados ao mudar os steps |
| DPM++ 2M | Método de múltiplas etapas; uma opção para comparar em SDXL |
| DPM++ SDE / 2M SDE | Métodos com componente estocástica; compare usando a mesma configuração de ruído |
| Heun | Faz uma etapa de correção; pode gastar mais avaliações do modelo que Euler |
| DDIM / UniPC | Alternativas presentes em alguns fluxos; escolha conforme a receita do modelo |
| LCM | Use com um modelo ou complemento preparado para esse tipo de geração |

As opções exibidas dependem do modelo e dos componentes disponíveis. O mesmo número de steps não implica o mesmo tempo entre samplers.

## Schedulers comuns

| Nome | Papel |
|---|---|
| Automatic | Usa a escolha padrão definida para o sampler nesse fluxo |
| Karras | Distribui os níveis de ruído segundo uma curva específica; opção comum para comparar com DPM++ em SDXL |
| Normal | Usa o escalonamento normal implementado para o modelo |
| Simple | Amostra níveis do fluxo do modelo de forma simples |
| Exponential | Usa espaçamento exponencial entre níveis |
| Beta | Distribui etapas segundo parâmetros de uma distribuição beta |

## Como escolher sem adivinhar

Comece pela recomendação do checkpoint. Depois compare, por exemplo, **Euler + Simple** e **DPM++ 2M + Karras**, se ambos estiverem disponíveis. Mantenha prompt, seed, tamanho e CFG iguais. Salve os resultados junto dos parâmetros.

Essas combinações são sugestões de comparação deste guia, não garantias de melhor qualidade. Confira se a receita que você copiou escreve sampler e scheduler em campos separados: “DPM++ 2M Karras” normalmente representa os dois.

[Samplers nesta versão do Forge](https://github.com/Haoming02/sd-webui-forge-classic/blob/bd1d015950b62f1c88a6d95f0b9ea1e0dfc69aa3/modules/sd_samplers_kdiffusion.py) · [Schedulers](https://github.com/Haoming02/sd-webui-forge-classic/blob/bd1d015950b62f1c88a6d95f0b9ea1e0dfc69aa3/modules/sd_schedulers.py)

---

# Entender os valores de geração

## Sampling steps

É o número de etapas. Poucas etapas podem deixar o resultado incompleto; aumentar muito pode apenas gastar tempo. O ponto útil muda conforme o sampler e o checkpoint.

Experimento sugerido: mantenha a seed e compare **20, 30 e 40 steps** em um modelo comum que não seja Turbo/Lightning. Compare detalhes e tempo. Modelos destilados precisam de seu próprio intervalo.

## CFG Scale

Regula a força da orientação pelo texto. Um valor alto pode aumentar certas características, mas também exagerar cores, contornos e contraste. Um valor baixo pode deixar o resultado se afastar da descrição. Essa relação não é perfeitamente linear.

Para aprender em SDXL Base, compare **CFG 4, 5 e 6**. São valores de teste deste guia. Em Anima Base, a página do modelo sugere **30–50 steps e CFG 4–5**. A receita para Turbo é diferente.

## Denoising strength

Aparece em img2img, Inpaint e Hires fix. Regula quanto a imagem existente pode ser refeita.

| Faixa de teste | Tendência prática |
|---|---|
| 0.15–0.30 | Mudança pequena; preservar estrutura |
| 0.35–0.55 | Transformação moderada |
| 0.60–0.85 | Mudança forte; maior chance de alterar identidade e composição |

São intervalos ilustrativos. O resultado depende da imagem, da máscara e do fluxo. Denoise não é um percentual simples de pixels substituídos.

## Shift e controles específicos

O Forge pode mostrar **Shift** para modelos como Anima. Esse controle altera o escalonamento do fluxo do modelo; não é equivalente a CFG. Use o valor padrão do preset ou a receita publicada antes de testar mudanças. **Distilled CFG** é outro controle específico e não substitui automaticamente o CFG comum.

[Configuração publicada do Anima](https://huggingface.co/circlestone-labs/Anima#generation-settings)

---

# Seed, tamanho e número de imagens

## Seed

A seed identifica o estado inicial do gerador de ruído. **-1** pede uma seed aleatória. Depois de encontrar uma composição interessante, use o botão de reaproveitar a seed ou copie o número exibido nos parâmetros.

Para repetir um resultado, guarde também checkpoint, módulos, prompt, sampler, scheduler, steps, CFG, resolução, complementos e versões. Mesma seed sozinha não garante a mesma imagem em outro ambiente ou após uma atualização.

## Width e Height

São a largura e a altura iniciais. A proporção participa da composição: retrato, paisagem e quadrado podem organizar os objetos de formas diferentes.

| Objetivo | Exemplo inicial de teste |
|---|---|
| Quadrado | 1024 × 1024 |
| Retrato | 768 × 1024 |
| Paisagem | 1024 × 768 |

Esses valores são pontos de partida deste guia. Prefira uma resolução suportada pelo checkpoint. Uma imagem de 2048 × 2048 contém quatro vezes os pixels de 1024 × 1024; a necessidade de memória pode aumentar bastante, mas não segue uma regra fixa de multiplicação.

## Batch count versus Batch size

**Batch size** controla quantas imagens são feitas simultaneamente. **Batch count** controla quantos lotes executar em sequência. Com size 1 e count 4, você pede quatro imagens em quatro lotes; com size 4 e count 1, pede quatro de uma vez.

No Colab, comece com **Batch size = 1**. Aumente o count para explorar variações mantendo o uso simultâneo de memória mais baixo. Gere primeiro em tamanho moderado e amplie a opção escolhida depois.

---

# Hires fix

O Hires fix acrescenta uma segunda passagem em txt2img: primeiro cria a imagem inicial, depois a amplia e pode gerar novos detalhes na resolução maior.

## Os principais controles

| Campo | Função |
|---|---|
| Upscaler | Como aumentar a imagem ou os latentes antes da segunda passagem |
| Upscale by / Resize | Fator ou tamanho final |
| Hires steps | Etapas da segunda passagem; verifique no controle se 0 significa reutilizar as etapas iniciais |
| Denoising strength | Quanto a passagem pode transformar o resultado |
| Hires sampler / scheduler | Permitem escolher o método da segunda passagem, quando esses controles estão visíveis |

## Um teste inicial

Escolha uma boa composição sem Hires. Depois, teste um aumento de **1.5×**, com denoise em torno de **0.25–0.40**, se o checkpoint aceitar esse fluxo. São sugestões para experimentar. Ampliações grandes podem exigir mais memória e criar objetos duplicados ou mudar detalhes do rosto.

Upscalers **Latent** trabalham na representação interna e precisam da passagem de geração para produzir um resultado útil. Upscalers de pixels usam outra abordagem. Compare as opções disponíveis com a mesma imagem.

## Hires ou Extras?

Use **Hires fix** quando quiser que o modelo acrescente detalhes durante a ampliação. Use **Extras** para ampliar uma imagem pronta com o upscaler escolhido. Extras é útil quando você quer conservar o conteúdo de uma imagem aprovada sem outra passagem completa de prompt.

Em caso de falta de memória, reduza o fator de ampliação e o tamanho inicial antes de aumentar outros controles.

---

# img2img

Esta aba usa uma imagem como ponto de partida. Você descreve o resultado desejado e decide quanto a geração pode alterar a imagem original.

## Passo a passo

1. Envie uma imagem ou use o atalho de txt2img para enviá-la a img2img.
2. Escreva como deve ficar o resultado, incluindo o assunto e o estilo.
3. Ajuste a proporção e o modo de redimensionamento.
4. Comece com um denoise moderado e gere uma imagem.
5. Aumente o denoise se quase nada mudar; reduza se a composição ou o rosto mudarem demais.

## Redimensionamento

**Just resize** pode deformar a imagem ao forçar outro formato. **Crop and resize** preenche a proporção recortando partes. **Resize and fill** procura manter o conteúdo e preencher áreas extras. Confira os nomes disponíveis e o enquadramento antes de gerar.

**Resize to** define dimensões finais; **Resize by** trabalha com um fator relativo à imagem de entrada.

## Quando usar

Mudar uma ilustração para outro acabamento, testar roupas e cores, retrabalhar um esboço ou adicionar detalhes a uma imagem pequena. Para mexer só em uma região, use Inpaint.

Os botões de **Interrogate**, quando disponíveis, tentam criar uma descrição ou tags a partir da imagem. São uma ajuda para começar; revise o texto, pois ele pode interpretar objetos e estilos incorretamente.

Se a referência precisa impor uma pose ou uma estrutura específica, combine img2img com um ControlNet compatível. Só aumentar o denoise não cria esse tipo de controle.

---

# Inpaint

O Inpaint permite refazer uma região marcada por uma máscara. Use para corrigir uma mão, alterar uma peça de roupa, remover um elemento ou reconstruir um detalhe.

## Fluxo de uma correção

1. Envie a imagem para **img2img → Inpaint**.
2. Pinte a região a modificar, incluindo uma pequena margem de contexto.
3. Confira se o modo altera **a área marcada** ou **a área fora da máscara**.
4. Descreva o resultado desejado naquela região. Para uma mão: `a natural hand holding a ceramic cup`.
5. Ajuste denoise, contexto e resolução do recorte. Compare algumas seeds.

## Campos que fazem diferença

| Campo | Como usar |
|---|---|
| Mask blur | Suaviza a borda da máscara para integrar melhor a correção |
| Masked content | Define o ponto de partida da região: original, preenchimento, ruído ou vazio, conforme as opções exibidas |
| Inpaint area: Whole picture | Trabalha considerando a imagem inteira |
| Inpaint area: Only masked | Processa um recorte em torno da área marcada |
| Padding | Acrescenta contexto ao recorte em pixels |
| Denoising strength | Define quanto a região pode ser reconstruída |

Se a mão mantém o mesmo erro, tente um denoise maior ou outra inicialização da região. Se o rosto perde identidade, teste um denoise menor e uma máscara mais precisa. Uma borda dura pode pedir mais blur e contexto.

Comece com alterações pequenas e salve cada versão aprovada. A compatibilidade de Inpaint depende do checkpoint e do backend; se Anima produzir um resultado ruim, compare com um fluxo de SDXL compatível e consulte o diagnóstico.

---

# Outras subabas de img2img

Esses modos mudam como você fornece a imagem ou a máscara. O modelo, o prompt e o denoise continuam influenciando o resultado.

| Subaba | Para que serve |
|---|---|
| img2img | Usar uma imagem existente como ponto de partida |
| Sketch | Desenhar ou pintar um esboço e transformá-lo em imagem |
| Inpaint | Pintar uma máscara sobre a imagem |
| Inpaint sketch | Combinar pintura de cores e marcação da região que será retrabalhada |
| Inpaint upload | Enviar a imagem e a máscara como arquivos separados |
| Batch → Upload | Processar um conjunto de imagens enviadas |
| Batch → From directory | Processar imagens de uma pasta do servidor |

## Esboços

Use formas simples para indicar composição e cores. Um esboço não garante a mesma pose ou o mesmo contorno depois da geração. Para impor a estrutura, teste um ControlNet da mesma família.

## Máscaras enviadas

Use imagem e máscara com dimensões correspondentes. Confira a convenção da máscara e a opção de inverter antes de executar um lote. Faça primeiro um teste com um único arquivo.

## Pastas no Colab

O caminho de **From directory** é uma pasta do ambiente que roda o Forge, como `/content/...`. Não é uma pasta do seu computador. Se usar Drive, ele precisa estar montado e o caminho deve apontar para o local correto.

Em Batch, configure uma pasta de saída apropriada e confirme como os arquivos serão nomeados. Um conjunto grande leva tempo; aprove primeiro o fluxo com uma imagem e mantenha o Batch size baixo.

---

# ControlNet

ControlNet acrescenta orientação visual à geração: uma pose, bordas, profundidade ou outra estrutura. O prompt continua descrevendo o conteúdo e o estilo.

## Preprocessor versus Model

O **preprocessor** transforma a referência em um mapa, como um esqueleto de pose. O **model** é o peso de controle que interpreta esse mapa junto do modelo principal. Os dois precisam ser compatíveis com o tipo de controle escolhido.

## Uma pose neste notebook

1. Abra ControlNet e habilite uma unidade.
2. Envie a imagem de referência.
3. Para extrair corpo, rosto e mãos com DWPose, escolha **dw_openpose_full**, se disponível.
4. Confira a prévia do mapa: se a detecção falhou, troque a referência ou corrija o mapa.
5. Em SDXL, use **thibaud_xl_openpose_256lora**. Para Anima, o notebook pode baixar **anima-lllite-pose-1**, cujo controle é experimental neste projeto.
6. Use a mesma proporção da referência e teste a geração.

Se você já tem um mapa de pose pronto, escolha **Preprocessor = None** e o peso de pose adequado.

## Ajustar a influência

**Control Weight** muda a intensidade do controle. **Guidance Start / End** definem a parte do processo em que ele age; `0` a `1` representa o intervalo completo. Como teste inicial, experimente peso `1` e intervalo completo, depois ajuste conforme o resultado.

Peso demais pode endurecer a composição; peso baixo pode deixar a pose escapar. O mapa influencia a estrutura, mas não garante anatomia perfeita nem copia a identidade da referência.

Não use pesos SD 1.5 em SDXL, nem pesos SDXL em Anima. Para outros controles, como Canny ou Depth, também confira se o peso correspondente foi instalado.

---

# ADetailer

O ADetailer detecta regiões na imagem e executa Inpaint automaticamente. É útil para refinar rostos e mãos sem desenhar cada máscara manualmente.

## Configuração deste notebook

| Passagem | Detector | Denoise | Recorte de Inpaint | Steps |
|---|---|---|---|---|
| Rosto | face_yolov8n.pt | 0.30 | 768 × 768 | 20 |
| Mãos | hand_yolov8n.pt | 0.40 | 768 × 768 | 20 |

Esses são os padrões configurados pelo notebook. Você pode alterá-los; o efeito depende do tamanho da região e do checkpoint.

## O que revisar

- **Enable / checkbox:** habilita o processamento adicional.
- **Detector:** escolhe o tipo de região a encontrar. O YOLO localiza a região; não é o modelo que desenha a correção.
- **Confidence / threshold:** define quais detecções serão aceitas. Muito alto pode ignorar rostos pequenos; muito baixo pode aceitar regiões erradas.
- **Denoising strength:** controla quanto o rosto ou a mão serão refeitos.
- **Prompt próprio:** se disponível, descreve a correção; revise o comportamento de campos vazios na extensão.
- **Mask blur / padding:** ajudam a integrar a borda e dar contexto ao recorte.

Mantenha o **ControlNet interno do ADetailer em None** nesse fluxo inicial, para não aplicar uma referência de corpo inteiro a um recorte pequeno.

Se o rosto muda de pessoa, reduza o denoise e confira o prompt. Se o detector não acha a mão, tente Inpaint manual. Desative ADetailer durante testes rápidos: cada região detectada acrescenta trabalho.

O notebook configura o recurso para Anima, mas a qualidade dessa combinação precisa ser avaliada no seu modelo e GPU. Compare com e sem o complemento.

[ADetailer Neo](https://github.com/Haoming02/ADetailer-Neo)

---

# LoRAs e redes adicionais

Uma LoRA é um arquivo menor que altera certos comportamentos do checkpoint: personagem, roupa, estilo, composição ou outro conceito. A compatibilidade depende da arquitetura e da base usada no treinamento.

## Usar uma LoRA

1. Baixe o arquivo para a pasta de LoRAs pelo CivBrowser.
2. Confirme a família: SDXL, Illustrious, Pony ou Anima, conforme a página do arquivo.
3. Atualize o painel **LoRA / Extra networks**.
4. Clique no cartão para inserir a marcação no prompt.
5. Inclua as **trigger words** indicadas pelo autor, se houver.
6. Teste o peso recomendado; se não houver receita, compare valores moderados.

Exemplo de marcação — substitua pelo nome de uma LoRA realmente instalada:

```text
<lora:nome_da_lora:0.7>, descrição da cena
```

`0.7` é um exemplo para um teste, não um valor universal. Algumas LoRAs precisam de pesos diferentes. Duas LoRAs podem competir entre si; habilite uma por vez antes de combinar.

## O que pode dar errado

**Cartão ausente:** atualize a lista, confirme o caminho de download e se o arquivo terminou de baixar.

**Nenhum efeito:** confira nome, família, peso e trigger words. Veja se o log reporta incompatibilidade.

**Imagem deformada ou estilo forte demais:** reduza o peso e compare com o checkpoint sem a LoRA.

**Embeddings / Textual Inversion** são outro tipo de complemento textual. Também precisam ser instalados e compatíveis; não são sinônimos de LoRA.

Em **Styles**, você salva trechos de prompt; isso não instala nem treina uma LoRA.

---

# CivBrowser

Esta extensão permite procurar modelos no Civitai, consultar versões e baixar arquivos para o Forge. Um mesmo modelo pode ter várias versões com bases e configurações diferentes.

## Antes de baixar

Confira o **tipo de arquivo** e o **base model**. Um checkpoint deve ir para a pasta de checkpoints; uma LoRA deve ir para a pasta de LoRAs. Neste notebook, os downloads são alinhados às pastas de modelos do workspace.

Leia a receita da versão: sampler, steps, CFG, trigger words e exemplo de prompt. Os parâmetros de uma imagem de demonstração não se aplicam automaticamente a todas as versões do modelo.

## Depois do download

Espere o arquivo terminar de baixar. Atualize a lista de checkpoints ou o painel LoRA. Para trocar o modelo principal, selecione o preset correto e revise os módulos VAE / Text Encoder.

Se enviar os parâmetros de uma imagem de exemplo para txt2img, confira se todos os modelos e complementos citados estão instalados. Um exemplo pode usar LoRAs que você ainda não tem.

## Falhas comuns

- Download bloqueado ou exige autenticação: confira a exigência do arquivo e a configuração do token.
- Modelo ausente: confirme pasta, extensão do arquivo e atualização da lista.
- Aviso **detached HEAD**: esta instalação fixa versões. O Forge pode falhar ao ler o nome da branch; esse aviso de metadados não prova que o download ou a geração falharam.

Use o recurso de credenciais do notebook quando necessário; mantenha o token fora de prompts e arquivos que você pretende compartilhar.

[Documentação do CivBrowser](https://github.com/SignalFlagZ/sd-webui-civbrowser)

---

# Extras

Use Extras para pós-processar uma imagem pronta. A ferramenta pode ampliar com um upscaler instalado e oferecer outros processadores, conforme o que aparece na interface.

## Fluxo simples

1. Envie a imagem ou use o atalho do painel de resultados.
2. Escolha o fator de escala ou as dimensões finais.
3. Selecione o upscaler.
4. Execute e compare o resultado com o original.

**Upscaler** é o modelo ou algoritmo de ampliação. Opções diferentes podem favorecer linhas, texturas ou fotografias. Compare um recorte importante, como rosto ou cabelo, em vez de avaliar apenas a imagem inteira reduzida na tela.

Se houver um segundo upscaler e um controle de mistura, ele combina os resultados dos dois processadores. Comece com apenas um para entender seu efeito.

## O que esperar

A ampliação aumenta o tamanho e pode reconstruir detalhes aparentes. Ela não recupera com certeza a informação que não estava na imagem original. Uma mão errada continua podendo precisar de Inpaint.

Processadores de restauração facial, quando disponíveis, podem mudar traços e identidade; confira o resultado antes de adotá-los como etapa padrão.

**Batch** permite pós-processar várias imagens. Verifique tamanho e espaço disponível antes de ampliar uma coleção inteira. Uma imagem grande também exige memória para pós-processamento.

As saídas dessa aba aparecem na origem **Extras** da biblioteca Axo Studio, conforme os caminhos configurados.

---

# PNG Info

Esta aba lê os parâmetros embutidos em uma imagem. Pode recuperar prompt, negativo, seed, sampler, resolução e outras informações gravadas pelo fluxo que criou o arquivo.

## Como usar

Envie a imagem e confira o texto extraído. Os botões de envio permitem transferir dados para txt2img, img2img ou outra ferramenta, quando disponíveis.

Para reproduzir, confirme que o checkpoint e as LoRAs citadas existem. O nome do modelo pode ser insuficiente; hashes e versões ajudam a distinguir arquivos com nomes semelhantes.

## Por que o prompt pode não aparecer

O arquivo pode nunca ter recebido os parâmetros, ter passado por um editor que removeu metadados ou ter sido baixado de um serviço que entregou uma cópia reduzida. JPEG e WebP também podem conter dados, mas isso depende de como foram salvos.

PNG Info não consegue deduzir com certeza o prompt original de qualquer imagem. Um botão de Interrogate cria uma interpretação; ele não recupera os parâmetros de geração apagados.

## Guardar um resultado útil

Salve a imagem original e uma cópia do texto dos parâmetros. Se compartilhar o arquivo, revise os metadados: eles podem incluir o prompt e nomes de modelos usados.

Na biblioteca **Axo Studio**, o painel **Prompt / Metadata** também tenta mostrar essas informações. O download original preserva os bytes do arquivo; a prévia reduzida serve para navegar.

---

# A biblioteca Axo Studio

A aba organiza as imagens encontradas nas pastas de saída configuradas no Forge. As miniaturas e prévias usam um cache local para manter a navegação mais leve no Colab.

## Navegar

- **Origem:** filtra txt2img, img2img, Extras, grades ou imagens salvas.
- **Filtrar pelo nome:** digite parte do nome e pressione Enter.
- **Atualizar:** procura arquivos novos e recarrega a página.
- **Anterior / Próxima:** navegam nas páginas de até 24 imagens.
- **Miniatura:** seleciona a imagem para mostrar a prévia, as dimensões e os parâmetros disponíveis.

A busca atual é por nome de arquivo. Ela não analisa visualmente a imagem nem procura dentro do prompt.

## Baixar

**Preparar download original** cria uma cópia para download da imagem selecionada. Use então o arquivo mostrado em **Baixar imagem**. A prévia é reduzida; o original conserva resolução e metadados.

Em **ZIP**, clique em **Exportar esta página em ZIP** para agrupar os arquivos da página atual. O limite configurado é 256 MiB por arquivo ZIP. O botão não exporta todas as páginas de uma vez.

## Se alguma imagem faltar

Confira a origem e a busca, clique em Atualizar e confirme onde o Forge está salvando. Imagens ilegíveis podem ser ignoradas e indicadas no contador. Se a sessão anterior do Colab foi encerrada sem persistência, os arquivos locais daquela sessão podem não estar disponíveis.

Se surgir um erro, use a célula **Diagnosticar galeria** após interromper a execução do Forge. Não confunda “não há imagens” com uma falha de carregamento.

---

# Scripts de geração e testes comparativos

O seletor **Script**, geralmente na parte inferior da geração, adiciona um fluxo especial. As opções dependem dos scripts instalados e da aba aberta.

## X/Y/Z plot, quando disponível

Cria uma grade de comparação variando parâmetros em eixos. É útil para comparar samplers, CFG, steps ou pesos sem editar os campos manualmente em cada geração.

Exemplo de teste:

- Prompt e seed fixos.
- Eixo X: CFG com `4, 5, 6`.
- Eixo Y: steps com `20, 30`.
- Resultado: seis combinações para avaliar.

Revise os nomes dos eixos e a sintaxe esperada pelo campo da sua versão. Se cada combinação usa batch, Hires ou ADetailer, o custo total aumenta.

## Outros scripts

**Prompt matrix** combina partes de uma descrição conforme sua sintaxe. **Prompts from file or textbox** pode executar uma sequência de prompts. Consulte as instruções mostradas pelo script antes de colar uma lista.

## Um bom experimento

Mude uma variável de cada vez quando estiver descobrindo seu efeito. Só crie grades com dois ou três eixos depois de entender cada controle. Guarde checkpoint, seed e módulos: uma comparação de CFG não é válida se o modelo também mudou entre as imagens.

Para voltar à geração normal, selecione **None / Nenhum** no campo Script. Um script deixado ativo pode explicar resultados ou tempos diferentes do esperado.

---

# Checkpoint Merger

Esta aba cria um novo checkpoint combinando pesos de modelos compatíveis. É um recurso avançado para experimentar comportamentos e estilos.

## O que você configura

Escolhe os checkpoints de entrada, um método de mistura, um coeficiente e um nome para o arquivo de saída. Os métodos disponíveis podem interpolar modelos ou combinar diferenças entre eles; revise a descrição do método na interface.

## Compatibilidade

Comece com modelos de mesma arquitetura e estrutura de pesos. Mesmo essa condição não garante uma mistura útil. Não trate o merger como um conversor entre SDXL e Anima.

O Anima deste notebook usa arquivos separados de difusão, encoder e VAE. A presença da aba não comprova suporte a uma mistura desses arquivos nesse fluxo. Use um procedimento publicado e compatível com a versão antes de tentar.

## Antes de executar

Garanta espaço para o arquivo novo e preserve os arquivos de entrada. Confira nome e destino para não substituir um modelo existente. A operação pode consumir bastante RAM e tempo no Colab.

Depois, teste o checkpoint gerado com as mesmas seeds e configurações usadas para avaliar os modelos originais. Avalie composição, estabilidade e detalhes, e não apenas uma imagem que saiu bonita.

Para o uso cotidiano — criar, editar e ampliar imagens — você pode trabalhar nas outras abas sem fazer uma mistura de checkpoints.

---

# Settings

A aba reúne preferências de interface, geração, salvamento, metadados e caminhos. A organização pode mudar conforme a versão e as extensões.

## Mudanças úteis

| Área | O que conferir |
|---|---|
| Interface / UI | Layout, painéis visíveis e controles rápidos |
| Saving images | Pastas, nomes, salvamento automático e metadados |
| Localization | Idioma da interface principal |
| Extra networks | Exibição e atualização de cartões de modelos e LoRAs |
| Sampler / model options | Ajustes avançados ligados ao backend |

Depois de editar, use **Apply settings**. Algumas mudanças exigem **Reload UI**; outras só entram em vigor ao reiniciar o processo. Confira a indicação do próprio controle.

## Cuidado com mudanças persistentes

O notebook configura caminhos de saída e módulos ao iniciar. Uma preferência alterada manualmente pode ser substituída pela configuração do notebook na próxima instalação. Se quiser uma mudança permanente nesses valores, ela deve ser incorporada ao notebook.

**Clip skip** modifica o uso de camadas em encoders compatíveis. Ele não significa “mais qualidade” e não tem o mesmo papel em todos os modelos. Mantenha a receita do checkpoint; não aplique um valor de SDXL automaticamente ao encoder Qwen do Anima.

As opções **LOW_VRAM** e **USE_GOOGLE_DRIVE** do notebook são definidas antes de iniciar o Forge. Elas não são simples preferências de aparência. Para aprender um controle avançado, registre o valor atual e teste uma mudança por vez.

---

# Extensions

Esta aba mostra as extensões e, conforme a instalação, permite consultar versões, habilitar ou desabilitar componentes e procurar atualizações.

## Neste projeto

O notebook instala versões específicas de **ADetailer Neo** e **CivBrowser** e cria a extensão local **axo-image-studio**, que contém a biblioteca e este guia. ControlNet e outros recursos de backend também podem vir como extensões internas do Forge.

Uma atualização automática pode trocar as versões que foram combinadas no notebook. Registre o estado que funciona antes de atualizar e consulte a compatibilidade com o Forge instalado. Depois de mudar extensões, normalmente é necessário reiniciar ou recarregar o processo.

## O aviso detached HEAD

O Git pode apontar diretamente para uma versão específica, sem uma branch ativa. Isso é chamado **detached HEAD**. O notebook usa esse estado ao fixar algumas versões.

O Forge pode tentar consultar a branch para preencher os dados da extensão e imprimir um traceback. Esse aviso de leitura de versão não demonstra, sozinho, falha na geração ou na extensão. Confira se o painel abre e se a função funciona.

## Quando uma extensão sumir

Confira se foi desabilitada e se houve erro durante a inicialização. Leia o log da célula do Colab; ele costuma mostrar a primeira exceção que impediu o carregamento.

O botão de restart do notebook reaproveita a instalação existente. Para aplicar uma nova versão do guia ou da biblioteca fornecida no notebook, execute **Install and launch** da nova versão.

---

# Receitas para começar

Estas receitas são pontos de partida para comparar resultados. Os melhores valores dependem da versão do checkpoint, da imagem desejada e da GPU.

| Campo | SDXL Base: sugestão deste guia | Anima Base: teste inicial |
|---|---|---|
| Preset | xl | anima |
| Sampler | DPM++ 2M | Euler |
| Scheduler | Karras | Simple |
| Steps | 28 | 32 |
| CFG | 5 | 4 |
| Resolução | 1024 × 1024 | 768 × 1024 |
| Batch size | 1 | 1 |
| Hires / ControlNet / ADetailer | Desabilitados no primeiro teste | Desabilitados no primeiro teste |

A combinação Euler + Simple é um teste sugerido por este projeto. Compare com a recomendação da versão do Anima que você utiliza. Turbo, Lightning, LCM e modelos destilados precisam de receitas próprias; não use automaticamente os valores da tabela.

## Criar, corrigir, ampliar

1. Gere algumas composições em txt2img.
2. Escolha uma imagem e guarde os parâmetros.
3. Corrija uma região em Inpaint, se necessário.
4. Teste ADetailer para regiões detectáveis ou ControlNet para controle de estrutura.
5. Amplie a imagem aprovada em Hires ou Extras.
6. Baixe o arquivo original na biblioteca.

## Comparações que ensinam

Com a mesma seed, compare negativos curtos, três CFGs ou dois samplers. Anote o que mudou. Para explorar ideias, use seeds aleatórias; para entender uma mudança, fixe a seed.

Só adicione um complemento depois de aprovar a geração básica. Isso torna mais fácil perceber qual etapa causou uma alteração inesperada.

---

# Problemas comuns

| Sintoma | Primeiro teste |
|---|---|
| CUDA out of memory / OOM | Batch size 1; reduza resolução; desative Hires e complementos; mantenha LOW_VRAM |
| Geração lenta | Veja o tempo sem ADetailer, ControlNet e Hires; FP32 e offload podem aumentar o tempo |
| Imagem preta, ruído ou cores incorretas | Confira checkpoint, VAE, encoder e mensagens do log; teste sem LoRAs |
| Erro de tensor / shape mismatch | Confira se módulos e complementos pertencem à família do checkpoint |
| Prompt pouco obedecido | Remova contradições; simplifique; confira a receita do modelo; compare CFG e pesos |
| Rosto ou mão muda demais | Reduza denoise e reveja máscara, padding e prompt de correção |
| Pose ignorada | Confira mapa do preprocessor, modelo de controle, peso e intervalo de atuação |
| LoRA não aparece | Confira pasta e fim do download; atualize o painel |
| Biblioteca vazia | Limpe busca e filtro; confira a pasta de saída e clique em Atualizar |
| Biblioteca mostra erro | Consulte a mensagem e a célula Diagnosticar galeria |
| Link do Forge para de abrir | Confira se a célula está rodando e se a sessão do Colab continua ativa |

## Encontrar o erro útil

Uma linha **INFO** descreve o estado da aplicação. Uma linha com **Traceback** mostra uma exceção. Procure a primeira falha ligada à operação que você acabou de executar, e não apenas a última linha do log.

Anote a aba, o checkpoint e o passo que provocou o erro. Interrompa a célula de execução sem excluir o ambiente e use **Inspect the last startup log** ou **Diagnosticar galeria**. Isso ajuda a separar um arquivo ausente de uma incompatibilidade de dependências.

**Restart** reaproveita os modelos e a instalação que existem na sessão. Encerrar ou excluir o runtime pode apagar arquivos locais; com Drive configurado, confirme que as imagens foram salvas lá antes de encerrar.

---

# Glossário

| Termo | Significado neste guia |
|---|---|
| Checkpoint | Modelo principal usado na geração |
| Preset | Conjunto de controles e escolhas de uma família no Forge |
| Prompt | Descrição do que você deseja criar |
| Negative prompt | Orientação para reduzir características indesejadas |
| Token | Unidade em que o encoder divide o texto |
| Text encoder | Modelo que transforma texto em representações usadas na geração |
| Latent | Representação interna comprimida da imagem |
| VAE | Módulo que converte entre pixels e representação interna |
| Sampler | Método que calcula as atualizações da geração |
| Scheduler | Distribuição dos níveis de ruído ao longo das etapas |
| Steps | Número de etapas de amostragem |
| CFG | Força de orientação pelo texto |
| Seed | Número usado para inicializar o gerador de ruído |
| Denoise | Intensidade de transformação de uma imagem de partida |
| Mask | Máscara que indica uma região de edição |
| Inpaint | Geração ou correção de uma região marcada |
| Upscaler | Ferramenta ou modelo para ampliar a imagem |
| LoRA | Complemento treinado para modificar comportamentos do modelo |
| Trigger words | Palavras de ativação indicadas para um complemento |
| ControlNet | Orientação visual baseada em uma estrutura de referência |
| ADetailer | Detecção automática seguida de Inpaint de regiões |
| Infotext / Metadata | Texto de parâmetros salvo com uma imagem |
| VRAM | Memória da GPU |
| Offload | Transferência de componentes entre GPU e memória do computador |
| Batch size | Quantidade de imagens processadas ao mesmo tempo por lote |
| Batch count | Quantidade de lotes executados |

Use a busca para encontrar o artigo que mostra o termo em um fluxo real. Por exemplo, busque **sampler**, **máscara**, **LoRA** ou **download**.

---

# Fontes e alcance do guia

Esta wiki foi escrita para o **notebook Axo Image Studio de Pedroltz**, com Forge Neo e os complementos que ele instala. Os exemplos de teste são sugestões do guia; os resultados variam com o checkpoint.

Os nomes dos controles e as abas foram conferidos no código da versão fixada do Forge. Recursos de outra versão, de outro backend ou de extensões adicionais podem aparecer de forma diferente.

## Referências oficiais

- [Forge Neo: projeto e documentação](https://github.com/Haoming02/sd-webui-forge-classic)
- [Código da interface usada por este notebook](https://github.com/Haoming02/sd-webui-forge-classic/blob/bd1d015950b62f1c88a6d95f0b9ea1e0dfc69aa3/modules/ui.py)
- [Forge: instalação de modelos e módulos](https://github.com/Haoming02/sd-webui-forge-classic/wiki/Download-Models)
- [Forge: referências de geração](https://github.com/Haoming02/sd-webui-forge-classic/wiki/Inference-References)
- [Anima: arquivos, variantes, prompts e geração](https://huggingface.co/circlestone-labs/Anima)
- [A1111: sintaxe de prompt e recursos herdados](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Features)
- [ADetailer Neo](https://github.com/Haoming02/ADetailer-Neo)
- [CivBrowser](https://github.com/SignalFlagZ/sd-webui-civbrowser)

## Como aprender com a wiki

Escolha um objetivo, abra o artigo correspondente e faça um teste pequeno. Salve os parâmetros do resultado. Ao comparar configurações, mantenha o modelo e a seed fixos e altere uma variável por vez.

Para checkpoints baixados depois, a documentação da **versão exata do arquivo** deve orientar módulos, palavras de ativação, sampler, steps e CFG. O guia ajuda a entender os controles para aplicar essa receita.
