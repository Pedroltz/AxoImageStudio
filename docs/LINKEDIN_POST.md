# Post para o LinkedIn

Estou compartilhando o Axo Image Studio, um projeto de geração e edição de imagens no Google Colab, baseado no Forge Neo.

A proposta é reunir criação, organização dos resultados e explicações dos controles em uma mesma interface.

Um dos problemas trabalhados foi o carregamento da galeria: miniaturas, prévias e downloads apresentavam erros no Colab. A solução usa um cache local separado e prepara o arquivo original quando o download é solicitado.

O projeto reúne:

• Axo Studio: galeria com filtros, paginação, prévia, parâmetros da imagem e exportação em ZIP.
• Axo Guide: wiki integrada com 29 artigos em português sobre as abas, prompts, samplers, CFG, seeds e Inpaint.
• Notebook independente, com preparação do ambiente e opção de persistência no Google Drive.
• Código organizado, documentação e 21 testes locais da interface e do notebook.

A geração utiliza o Forge e modelos de terceiros. Minha contribuição está na personalização, na integração e na experiência de uso do Axo.

Nas imagens, apresento uma prévia local do guia e artes conceituais criadas com IA para a identidade do projeto.

Código, documentação e notebook:
https://github.com/Pedroltz/AxoImageStudio

Sugestões sobre a interface e o guia são bem-vindas.

#Python #InteligenciaArtificial #Gradio #GoogleColab #UX

---

Use a [captura do guia e as artes](DEMOS.md) na sequência sugerida no [roteiro de apresentação](PRESENTATION.md). As fontes consultadas estão nas [notas de pesquisa](RESEARCH_NOTES.md).
