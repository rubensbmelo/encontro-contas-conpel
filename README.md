# Sistema de Gestão de Encontro de Contas
### Nova Conpel & Pincéis Roma

Aplicação Web em Python / Streamlit para acompanhamento em tempo real do faturamento e compensação de maquinário.

## Funcionalidades
- **Dashboard de Indicadores:** Valor da máquina (R$ 900k), Total Compensado, Saldo Restante e Excedente.
- **Gráficos Interativos:** Plotly com visualização mês a mês e barra de progresso.
- **Gestão de Notas Fiscais:** Cadastro, listagem e exclusão com banco de dados SQLite persistente.
- **Links Diretos do Drive:** Botão integrado para visualização dos PDFs das notas fiscais.
- **Exportação:** Geração de planilha Excel (.xlsx) consolidada com 1 clique.

## Como Executar Localmente
1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Inicie a aplicação:
   ```bash
   streamlit run app.py
   ```
   *(Ou dê 2 cliques no arquivo `run_app.bat`)*

## Como Publicar Online (100% Gratuito)
1. Crie um repositório no seu **GitHub** (ex: `encontro-contas-conpel`).
2. Suba os arquivos da pasta: `app.py`, `database.py`, `requirements.txt`.
3. Acesse [share.streamlit.io](https://share.streamlit.io) e conecte com seu GitHub.
4. Selecione o repositório e clique em **Deploy**.
5. Seu sistema estará online com um link público (ex: `https://conpel-roma.streamlit.app`)!
