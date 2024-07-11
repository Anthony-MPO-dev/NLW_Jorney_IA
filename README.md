# Travel Itinerary Agent with AWS Integration

Este projeto cria um agente de planejamento de viagens que integra ferramentas de pesquisa e análise utilizando a API do ChatGPT da OpenAI. Ele é implementado como uma função AWS Lambda para ser invocado sob demanda.

## Execução via cURL
Você pode invocar a função Lambda do agente de itinerário de viagem utilizando curl da seguinte maneira:

```bash
curl -X POST "http://api-travelagent-946764600.sa-east-1.elb.amazonaws.com" \
-H "Content-Type: application/json" \
-d '{
    "question": "Vou viajar para Londres em agosto de 2024. Quero que faça para um roteiro de viagem para mim com eventos que irão ocorrer na data da viagem e com o preço de passagem de São Paulo para Londres." 
}'
```

## Explicação:
- -X POST: Especifica que o método HTTP usado é POST, indicando que você está enviando dados para o servidor.
- -H "Content-Type: application/json": Define o cabeçalho HTTP para indicar que o conteúdo enviado é do tipo JSON.
- -d '{ ... }': Envia os dados JSON com a consulta de viagem. Substitua o conteúdo dentro das chaves { ... } com sua própria consulta de viagem.
### Isso enviará a consulta para o endpoint especificado, onde a função Lambda processará a solicitação e retornará um roteiro de viagem personalizado como resposta.
