#20250313 - OK;
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf

def fin():
    col1, col2 = st.columns([4, 1]) 

    with col1:
        st.markdown(
            """
            <h1 class="title">
                FIN
            </h1>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        if st.button("<-"):
            st.session_state.tela_atual = "A"  

    ticker = "BBOI11.SA"

    acao = yf.Ticker(ticker)

    info = acao.info
    st.write(f"**nome:** {info['longName']}")
    st.write(f"**preço atual:** R$ {info['currentPrice']:.2f}")

    historico = acao.history(period="1mo") 

    st.write("**histórico de cotações (último mês):**")
    st.dataframe(historico)

    st.write("**gráfico de preços de fechamento:**")
    st.line_chart(historico['Close'])

if __name__ == "__main__":
    fin()