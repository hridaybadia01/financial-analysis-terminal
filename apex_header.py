import streamlit as st


def render_apex_header(
    title="Financial Analysis Terminal",
    subtitle="Research • Valuation • Markets • Portfolio & Risk Analysis",
    market_status="NSE Market Closed",
    timestamp=""
):
    st.html(
        f"""
        <div class="apex-header">

            <div class="apex-header-left">

                <div class="apex-brand-mark">
                    <div class="apex-brand-chevron">A</div>
                </div>

                <div class="apex-brand-text">

                    <div class="apex-brand-title">
                        {title}
                    </div>

                    <div class="apex-brand-subtitle">
                        {subtitle}
                    </div>

                </div>

            </div>

            <div class="apex-header-right">

                <div class="apex-market-status">
                    <span class="apex-status-dot"></span>
                    <span>{market_status}</span>
                </div>

                <div class="apex-header-time">
                    {timestamp}
                </div>

            </div>

        </div>
        """
    )