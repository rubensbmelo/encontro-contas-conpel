import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import json
import os
import base64

import drive_sync as ds
import database as db

# Page configuration
st.set_page_config(
    page_title="Nova Conpel • Encontro de Contas",
    page_icon="logo_conpel.png" if os.path.exists("logo_conpel.png") else "🏭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Constants
PARCELA_MENSAL = 150000.00
NUM_PARCELAS = 6
VALOR_TOTAL_MAQUINA = PARCELA_MENSAL * NUM_PARCELAS
MESES = ['AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO', 'JANEIRO']
CONFIG_FILE = "config_drive.json"

# Helper for logo in base64
def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), "logo_conpel.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_b64 = get_logo_base64()
logo_img_tag = f'<img src="data:image/png;base64,{logo_b64}" style="width: 58px; height: 58px; border-radius: 12px; background: white; padding: 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.15);">' if logo_b64 else '<div style="width: 52px; height: 52px; background: #512C19; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 20px;">NC</div>'

# Helper for configs
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "drive_url": "https://drive.google.com/file/d/1cflk0IP_m4GqaFc8xvPaMToyMs2_j3Kg/view?usp=drive_link",
        "auto_sync": True
    }

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

config = load_config()

# Nova Conpel Theme CSS
st.markdown("""
<style>
    /* Global accents */
    :root {
        --conpel-primary: #512C19;
        --conpel-dark: #381E11;
        --conpel-light: #784227;
        --conpel-accent: #C27835;
        --conpel-bg: #FAF6F2;
    }
    
    .main-header {
        background: linear-gradient(135deg, #512C19 0%, #381E11 100%);
        padding: 24px 28px;
        border-radius: 18px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 6px 16px rgba(81, 44, 25, 0.2);
    }
    .main-header h1 {
        color: #FFFFFF !important;
        font-size: 25px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #E8D8CF !important;
        font-size: 14px;
        margin: 4px 0 0 0;
    }
    
    .kpi-container {
        background: #FFFFFF;
        border: 1px solid #EAE0D8;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 2px 6px rgba(81, 44, 25, 0.04);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(81, 44, 25, 0.08);
    }
    .kpi-label {
        font-size: 11.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #785D50;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 800;
        margin: 6px 0 3px 0;
    }
    
    /* Primary buttons */
    .stButton>button {
        background-color: #512C19 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: background-color 0.2s ease !important;
    }
    .stButton>button:hover {
        background-color: #784227 !important;
    }
    
    /* Link buttons */
    a[data-testid="stLinkButton"] {
        background-color: #FAF6F2 !important;
        color: #512C19 !important;
        border: 1px solid #D6C5BC !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    a[data-testid="stLinkButton"]:hover {
        background-color: #512C19 !important;
        color: #FFFFFF !important;
        border-color: #512C19 !important;
    }
    
    /* Tabs styling */
    button[data-baseweb="tab"] {
        font-weight: 700 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #512C19 !important;
        border-bottom-color: #512C19 !important;
    }
</style>
""", unsafe_allow_html=True)

def format_brl(val):
    return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Sidebar: Conexao com Google Drive
with st.sidebar:
    if os.path.exists("logo_conpel.png"):
        st.image("logo_conpel.png", width=70)
    st.title("Nova Conpel")
    st.caption("Painel de Gestão e Encontro de Contas")
    st.divider()
    
    drive_input = st.text_input(
        "Link da Planilha no Drive:",
        value=config.get("drive_url", ""),
        help="Cole o link de compartilhamento da planilha no Google Drive ou Google Sheets."
    )
    
    col_s1, col_s2 = st.columns(2)
    if col_s1.button("🔄 Sincronizar", use_container_width=True):
        st.cache_data.clear()
        config["drive_url"] = drive_input
        save_config(config)
        st.rerun()
        
    if col_s2.button("💾 Salvar", use_container_width=True):
        config["drive_url"] = drive_input
        save_config(config)
        st.success("Salvo!")

    if drive_input:
        st.write("")
        st.link_button("🔗 Abrir Planilha Google Drive", drive_input, use_container_width=True)

# Fetch Data quietly (Cache with TTL 60s for live sync)
@st.cache_data(ttl=60)
def fetch_live_data(url):
    return ds.load_data_from_google_drive(url)

dados_meses, sync_ok, sync_msg = fetch_live_data(config.get("drive_url", ""))

# Top Header Bar with Nova Conpel Logo
st.markdown(f"""
<div class="main-header">
    <div style="display: flex; align-items: center; gap: 18px;">
        {logo_img_tag}
        <div>
            <h1>Gestão de Encontro de Contas</h1>
            <p>NOVA CONPEL & PINCÉIS ROMA — Acompanhamento do Acordo e Faturamento</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Resumo Global Calculations
resumo_meses = []
for m in MESES:
    df_m = dados_meses.get(m, pd.DataFrame())
    tot_notas = df_m['valor'].sum() if not df_m.empty else 0.0
    compensado = min(PARCELA_MENSAL, tot_notas)
    saldo_pend = max(PARCELA_MENSAL - tot_notas, 0.0)
    excedente = max(tot_notas - PARCELA_MENSAL, 0.0)
    
    if saldo_pend > 0 and tot_notas == 0:
        status = "Aguardando"
    elif saldo_pend > 0:
        status = "Pendente"
    elif excedente > 0:
        status = "Excedente a Cobrar"
    else:
        status = "Compensado"
        
    resumo_meses.append({
        'mes': m,
        'parcela': PARCELA_MENSAL,
        'total_notas': tot_notas,
        'compensado': compensado,
        'saldo': saldo_pend,
        'excedente': excedente,
        'status': status,
        'qtd_notas': len(df_m)
    })

df_resumo = pd.DataFrame(resumo_meses)
total_compensado_geral = df_resumo['compensado'].sum()
saldo_geral_maquina = VALOR_TOTAL_MAQUINA - total_compensado_geral
total_excedente_geral = df_resumo['excedente'].sum()
percentual_quitado = (total_compensado_geral / VALOR_TOTAL_MAQUINA) * 100

# Global KPIs
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Valor Total do Acordo</div>
        <div class="kpi-value" style="color: #512C19;">{format_brl(VALOR_TOTAL_MAQUINA)}</div>
        <small style="color: #785D50;">6 parcelas de {format_brl(PARCELA_MENSAL)}</small>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Total Compensado</div>
        <div class="kpi-value" style="color: #16A34A;">{format_brl(total_compensado_geral)}</div>
        <small style="color: #16A34A; font-weight: 700;">{percentual_quitado:.1f}% quitado</small>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Saldo Restante do Acordo</div>
        <div class="kpi-value" style="color: #C27835;">{format_brl(saldo_geral_maquina)}</div>
        <small style="color: #785D50;">A compensar nos próximos meses</small>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-container">
        <div class="kpi-label">Excedente Faturado</div>
        <div class="kpi-value" style="color: #784227;">{format_brl(total_excedente_geral)}</div>
        <small style="color: #785D50;">Valor a faturar separadamente</small>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Navigation Tabs
tab_names = ["📊 VISÃO CONSOLIDADA"] + [f"📅 {m}" for m in MESES]
selected_tabs = st.tabs(tab_names)

# Tab 0: Visão Consolidada
with selected_tabs[0]:
    st.subheader("📈 Resumo Consolidado do Encontro de Contas")
    
    col_chart1, col_chart2 = st.columns([3, 2])
    
    with col_chart1:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_resumo['mes'],
            y=df_resumo['total_notas'],
            name='Notas Lançadas (R$)',
            marker_color='#512C19'
        ))
        fig.add_trace(go.Scatter(
            x=df_resumo['mes'],
            y=[PARCELA_MENSAL] * len(MESES),
            name='Meta Parcela (R$ 150k)',
            mode='lines',
            line=dict(color='#C27835', width=2.5, dash='dash')
        ))
        fig.update_layout(
            title="Evolução Mensal: Faturamento vs. Parcela de Compensação",
            yaxis_title="Valor (R$)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=50, b=20),
            height=340,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        fig_donut = go.Figure(data=[go.Pie(
            labels=['Compensado', 'Saldo Restante'],
            values=[total_compensado_geral, max(saldo_geral_maquina, 0)],
            hole=.65,
            marker_colors=['#512C19', '#EAE0D8']
        )])
        fig_donut.update_layout(
            title=f"Quitação do Acordo: {percentual_quitado:.1f}%",
            annotations=[dict(text=f"{percentual_quitado:.1f}%", x=0.5, y=0.5, font_size=24, showarrow=False, font_weight='bold', font_color='#512C19')],
            margin=dict(l=20, r=20, t=50, b=20),
            height=340,
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # Detalhamento Tabela
    st.write("### Detalhamento por Mês")
    table_display = df_resumo.copy()
    table_display['parcela'] = table_display['parcela'].apply(format_brl)
    table_display['total_notas'] = table_display['total_notas'].apply(format_brl)
    table_display['compensado'] = table_display['compensado'].apply(format_brl)
    table_display['saldo'] = table_display['saldo'].apply(format_brl)
    table_display['excedente'] = table_display['excedente'].apply(format_brl)
    table_display.columns = ['Mês', 'Parcela', 'Total Notas', 'Encontro de Contas', 'Saldo Pendente', 'Excedente a Cobrar', 'Status', 'Qtd Notas']
    st.dataframe(table_display, use_container_width=True, hide_index=True)

    # Download Excel
    st.divider()
    def generate_excel():
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_resumo.to_excel(writer, sheet_name='RESUMO', index=False)
            for m in MESES:
                df_m = dados_meses.get(m, pd.DataFrame())
                if not df_m.empty:
                    df_m.to_excel(writer, sheet_name=m, index=False)
                else:
                    pd.DataFrame(columns=['id', 'mes', 'data', 'numero_nf', 'valor', 'link_drive', 'observacao']).to_excel(writer, sheet_name=m, index=False)
        return output.getvalue()

    st.download_button(
        label="📥 Exportar Dados Atualizados para Excel (.xlsx)",
        data=generate_excel(),
        file_name="Encontro_de_Contas_Nova_Conpel_Oficial.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Individual Month Tabs
for i, m in enumerate(MESES, start=1):
    with selected_tabs[i]:
        row_info = df_resumo[df_resumo['mes'] == m].iloc[0]
        
        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Parcela do Mês", format_brl(PARCELA_MENSAL))
        mc2.metric("Total das Notas", format_brl(row_info['total_notas']))
        mc3.metric("Encontro de Contas", format_brl(row_info['compensado']))
        mc4.metric("Saldo Pendente", format_brl(row_info['saldo']), delta=f"{format_brl(row_info['excedente'])} Excedente" if row_info['excedente'] > 0 else None)
        
        st.divider()

        notas_mes = dados_meses.get(m, pd.DataFrame())
        st.subheader(f"📋 Notas Fiscais — {m} ({len(notas_mes)} lançadas)")
        
        if not notas_mes.empty:
            for idx, n in notas_mes.iterrows():
                with st.container():
                    c_date, c_nf, c_val, c_doc = st.columns([2.5, 2.5, 3, 3])
                    
                    try:
                        d_obj = datetime.strptime(str(n['data'])[:10], "%Y-%m-%d")
                        formatted_d = d_obj.strftime("%d/%m/%Y")
                    except Exception:
                        formatted_d = str(n['data']) if n['data'] else "—"
                        
                    c_date.write(f"📅 **{formatted_d}**")
                    c_nf.write(f"NF `#{n['numero_nf']}`")
                    c_val.write(f"**{format_brl(n['valor'])}**")
                    
                    link_val = str(n['link_drive']).strip() if n['link_drive'] else ""
                    if link_val and link_val.startswith("http"):
                        c_doc.link_button("📄 Abrir PDF (Drive)", link_val)
                    else:
                        c_doc.caption("Sem anexo")
                st.divider()
        else:
            st.info(f"Nenhuma nota fiscal lançada para {m}.")
