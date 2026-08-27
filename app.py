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

# Resumo Global Calculations with Automatic Rollover (Saldo Acumulado)
resumo_meses = []
saldo_anterior_acumulado = 0.0

for idx, m in enumerate(MESES):
    df_m = dados_meses.get(m, pd.DataFrame())
    tot_notas = df_m['valor'].sum() if not df_m.empty else 0.0
    
    # Meta do mês atual = Parcela Base (150k) + Saldo Pendente do mês anterior
    meta_mes = PARCELA_MENSAL + saldo_anterior_acumulado
    compensado = min(meta_mes, tot_notas)
    saldo_pend = max(meta_mes - tot_notas, 0.0)
    excedente = max(tot_notas - meta_mes, 0.0)
    
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
        'parcela_base': PARCELA_MENSAL,
        'saldo_anterior': saldo_anterior_acumulado,
        'meta_mes': meta_mes,
        'total_notas': tot_notas,
        'compensado': compensado,
        'saldo': saldo_pend,
        'excedente': excedente,
        'status': status,
        'qtd_notas': len(df_m)
    })
    
    # Transfere o saldo restante para acumular no próximo mês
    saldo_anterior_acumulado = saldo_pend

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
    # 1. Mobile-friendly Progress Bar Card
    prog_html = (
        f'<div style="background: #FFFFFF; border: 1px solid #EAE0D8; border-radius: 16px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(81,44,25,0.04);">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 10px;">'
        f'<div>'
        f'<span style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #785D50; letter-spacing: 0.5px;">Quitação Geral do Acordo</span>'
        f'<div style="font-size: 18px; font-weight: 800; color: #512C19; margin-top: 2px;">{format_brl(total_compensado_geral)} <span style="font-size: 13px; font-weight: 500; color: #785D50;">de {format_brl(VALOR_TOTAL_MAQUINA)}</span></div>'
        f'</div>'
        f'<div style="background: #FAF6F2; border: 1px solid #D6C5BC; padding: 6px 14px; border-radius: 20px; font-size: 14px; font-weight: 800; color: #512C19;">{percentual_quitado:.1f}% concluído</div>'
        f'</div>'
        f'<div style="background: #EAE0D8; border-radius: 999px; height: 12px; width: 100%; overflow: hidden; margin-top: 6px;">'
        f'<div style="background: linear-gradient(90deg, #512C19 0%, #784227 100%); width: {percentual_quitado}%; height: 100%; border-radius: 999px;"></div>'
        f'</div>'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 12px; color: #785D50; flex-wrap: wrap; gap: 4px;">'
        f'<span>✅ Total Compensado: <strong style="color: #16A34A;">{format_brl(total_compensado_geral)}</strong></span>'
        f'<span>⏳ Saldo Restante: <strong style="color: #C27835;">{format_brl(saldo_geral_maquina)}</strong></span>'
        f'</div>'
        f'</div>'
    )
    st.markdown(prog_html, unsafe_allow_html=True)

    # 2. Clean Responsive Evolution Chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_resumo['mes'],
        y=df_resumo['total_notas'],
        name='Faturamento Lançado',
        marker_color='#512C19',
        text=[format_brl(v) if v > 0 else '' for v in df_resumo['total_notas']],
        textposition='outside'
    ))
    fig.add_trace(go.Scatter(
        x=df_resumo['mes'],
        y=[PARCELA_MENSAL] * len(MESES),
        name='Parcela Mensal (R$ 150k)',
        mode='lines',
        line=dict(color='#C27835', width=2, dash='dash')
    ))
    fig.update_layout(
        title="📊 Evolução Mensal do Encontro de Contas",
        yaxis_title="Valor (R$)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=10, r=10, t=45, b=10),
        height=280,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(size=11)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.write("### 📅 Resumo Mês a Mês")
    
    # 3. Mobile-First Modern Cards for each month
    # In desktop: 3 columns; in mobile: stacks neatly into 1 column
    row1_cols = st.columns(3)
    row2_cols = st.columns(3)
    all_grid_cols = row1_cols + row2_cols

    for idx, r_row in df_resumo.iterrows():
        col = all_grid_cols[idx]
        m_name = r_row['mes']
        m_total = r_row['total_notas']
        m_comp = r_row['compensado']
        m_saldo = r_row['saldo']
        m_exced = r_row['excedente']
        m_qtd = r_row['qtd_notas']
        m_status = r_row['status']
        
        # Status Badge Colors
        if m_status == "Compensado":
            badge_bg = "#DCFCE7"
            badge_color = "#166534"
            badge_border = "#BBF7D0"
        elif m_status == "Pendente":
            badge_bg = "#FEF9C3"
            badge_color = "#854D0E"
            badge_border = "#FEF08A"
        elif m_status == "Excedente a Cobrar":
            badge_bg = "#DBEAFE"
            badge_color = "#1E40AF"
            badge_border = "#BFDBFE"
        else:
            badge_bg = "#F3F4F6"
            badge_color = "#6B7280"
            badge_border = "#E5E7EB"

        with col:
            m_saldo_ant = r_row['saldo_anterior']
            m_meta = r_row['meta_mes']
            
            saldo_ant_line = f'<div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px; color: #C27835; background: #FAF6F2; padding: 3px 6px; border-radius: 6px;"><span>+ Saldo Acumulado Anterior:</span><strong>{format_brl(m_saldo_ant)}</strong></div>' if m_saldo_ant > 0 else ''
            exced_block = f'<div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;"><span style="color: #2563EB;">Excedente a Faturar:</span><strong style="color: #2563EB;">{format_brl(m_exced)}</strong></div>' if m_exced > 0 else ''
            saldo_color = '#C27835' if m_saldo > 0 else '#16A34A'
            card_html = (
                f'<div style="background: #FFFFFF; border: 1px solid #EAE0D8; border-radius: 14px; padding: 16px; margin-bottom: 14px; box-shadow: 0 2px 6px rgba(81,44,25,0.03);">'
                f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">'
                f'<span style="font-weight: 800; font-size: 15px; color: #512C19;">{m_name}</span>'
                f'<span style="background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_border}; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 12px;">{m_status}</span>'
                f'</div>'
                f'{saldo_ant_line}'
                f'<div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;">'
                f'<span style="color: #785D50;">Meta do Mês:</span><strong style="color: #512C19;">{format_brl(m_meta)}</strong>'
                f'</div>'
                f'<div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;">'
                f'<span style="color: #785D50;">Notas Lançadas:</span><strong style="color: #2A160C;">{format_brl(m_total)}</strong>'
                f'</div>'
                f'<div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;">'
                f'<span style="color: #785D50;">Encontro de Contas:</span><strong style="color: #16A34A;">{format_brl(m_comp)}</strong>'
                f'</div>'
                f'<div style="display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 6px;">'
                f'<span style="color: #785D50;">Saldo a Compensar:</span><strong style="color: {saldo_color};">{format_brl(m_saldo)}</strong>'
                f'</div>'
                f'{exced_block}'
                f'<div style="border-top: 1px dashed #EAE0D8; margin-top: 10px; padding-top: 8px; font-size: 11.5px; color: #785D50; display: flex; justify-content: space-between;">'
                f'<span>Qtd. de Notas: <strong>{m_qtd}</strong></span>'
                f'<span>Base: <strong>{format_brl(PARCELA_MENSAL)}</strong></span>'
                f'</div>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

    # 4. Optional Table in Expander
    with st.expander("📋 Ver Tabela Completa (Formato Planilha)"):
        table_display = df_resumo.copy()
        table_display['parcela'] = table_display['parcela'].apply(format_brl)
        table_display['total_notas'] = table_display['total_notas'].apply(format_brl)
        table_display['compensado'] = table_display['compensado'].apply(format_brl)
        table_display['saldo'] = table_display['saldo'].apply(format_brl)
        table_display['excedente'] = table_display['excedente'].apply(format_brl)
        table_display.columns = ['Mês', 'Parcela', 'Total Notas', 'Encontro de Contas', 'Saldo Pendente', 'Excedente a Cobrar', 'Status', 'Qtd Notas']
        st.dataframe(table_display, use_container_width=True, hide_index=True)

    # Download Excel Button
    st.write("")
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
        label="📥 Baixar Planilha Consolidada (.xlsx)",
        data=generate_excel(),
        file_name="Encontro_de_Contas_Nova_Conpel_Oficial.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )


# Individual Month Tabs
for i, m in enumerate(MESES, start=1):
    with selected_tabs[i]:
        row_info = df_resumo[df_resumo['mes'] == m].iloc[0]
        
        mc1, mc2, mc3, mc4 = st.columns(4)
        s_ant = row_info['saldo_anterior']
        if s_ant > 0:
            mc1.metric("Meta do Mês", format_brl(row_info['meta_mes']), delta=f"+ {format_brl(s_ant)} acumulado anterior", delta_color="off")
        else:
            mc1.metric("Parcela do Mês", format_brl(PARCELA_MENSAL))
            
        mc2.metric("Total das Notas", format_brl(row_info['total_notas']))
        mc3.metric("Encontro de Contas", format_brl(row_info['compensado']))
        mc4.metric("Saldo Restante", format_brl(row_info['saldo']), delta=f"{format_brl(row_info['excedente'])} Excedente" if row_info['excedente'] > 0 else None)
        
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
