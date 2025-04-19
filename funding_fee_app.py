
import streamlit as st
import requests
import pandas as pd
import hmac
import hashlib
import time
from urllib.parse import urlencode
from datetime import datetime, time as dt_time
import smtplib
from email.message import EmailMessage
import os
import plotly.express as px

st.set_page_config(page_title="Funding Fee Tracker", layout="wide")

def sign_request(secret, params):
    query_string = urlencode(params)
    signature = hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return query_string + f"&signature={signature}"

def get_open_positions(api_key, api_secret):
    url = "https://fapi.binance.com/fapi/v2/positionRisk"
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    signed_params = sign_request(api_secret, params)
    headers = {"X-MBX-APIKEY": api_key}
    response = requests.get(f"{url}?{signed_params}", headers=headers)
    try:
        data = response.json()
        if isinstance(data, dict) and "msg" in data:
            st.error(f"Lỗi từ Binance API: {data['msg']}")
            return []
        return [p for p in data if isinstance(p, dict) and "positionAmt" in p and abs(float(p["positionAmt"])) > 0]
    except Exception as e:
        st.error(f"Lỗi khi đọc dữ liệu vị thế: {e}")
        return []

def get_funding_rate_history(symbol, start_time, end_time):
    start_time = datetime.combine(start_time, dt_time.min)
    end_time = datetime.combine(end_time, dt_time.max)
    url = "https://fapi.binance.com/fapi/v1/fundingRate"
    params = {
        "symbol": symbol,
        "startTime": int(start_time.timestamp() * 1000),
        "endTime": int(end_time.timestamp() * 1000),
        "limit": 1000
    }
    response = requests.get(url, params=params)
    try:
        data = response.json()
        if isinstance(data, dict) and "msg" in data:
            st.warning(f"{symbol}: {data['msg']}")
            return pd.DataFrame()
        df = pd.DataFrame(data)
        if df.empty:
            return df
        df["fundingTime"] = pd.to_datetime(df["fundingTime"], unit="ms")
        df["fundingRate"] = df["fundingRate"].astype(float)
        df["fundingRate(%)"] = df["fundingRate"] * 100
        return df
    except Exception as e:
        st.warning(f"Lỗi khi tải funding rate của {symbol}: {e}")
        return pd.DataFrame()

def calculate_funding_fee(position_amt, df):
    df["funding_fee"] = df["fundingRate"] * float(position_amt)
    return df["funding_fee"].sum(), df

def send_email_report(sender, password, receiver, subject, body, attachment_path=None):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content(body)

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            msg.add_attachment(f.read(), maintype="application", subtype="octet-stream", filename=os.path.basename(attachment_path))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)

st.title("📊 Funding Fee Tracker - Binance Futures")

with st.sidebar:
    st.header("🔐 Cấu hình API & Email")
    api_key = st.text_input("API Key", type="password")
    api_secret = st.text_input("API Secret", type="password")
    email_sender = st.text_input("Email gửi (Gmail)", type="default")
    email_pass = st.text_input("App Password Gmail", type="password")
    email_receiver = st.text_input("Email nhận báo cáo", type="default")

st.markdown("### 📅 Chọn thời gian cần tra cứu")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Từ ngày", datetime(2024, 1, 1))
with col2:
    end_date = st.date_input("Đến ngày", datetime(2024, 3, 31))

if st.button("🚀 Tra cứu funding fee"):
    if not all([api_key, api_secret, email_sender, email_pass, email_receiver]):
        st.warning("Vui lòng nhập đầy đủ thông tin cấu hình!")
    else:
        with st.spinner("Đang lấy dữ liệu..."):
            positions = get_open_positions(api_key, api_secret)
            if not positions:
                st.error("Không có vị thế mở.")
            else:
                all_results = []
                summary = []
                for pos in positions:
                    symbol = pos["symbol"]
                    amt = float(pos["positionAmt"])
                    direction = "Long" if amt > 0 else "Short"
                    df = get_funding_rate_history(symbol, start_date, end_date)
                    if df.empty:
                        continue
                    total_fee, df = calculate_funding_fee(amt, df)
                    df["Symbol"] = symbol
                    df["Position Size"] = amt
                    df["Direction"] = direction
                    summary.append({"Symbol": symbol, "Direction": direction, "Total Funding Fee": total_fee})
                    all_results.append(df)

                if all_results:
                    final_df = pd.concat(all_results)
                    summary_df = pd.DataFrame(summary)

                    st.success("✅ Hoàn tất!")
                    st.subheader("📋 Tổng quan funding fee")
                    st.dataframe(summary_df)

                    st.subheader("📈 Biểu đồ tương tác funding fee")
                    chart_data = summary_df.groupby(["Symbol", "Direction"])["Total Funding Fee"].sum().unstack()
                    chart_data_reset = chart_data.reset_index()
                    fig = px.bar(chart_data_reset, x="Symbol", y=chart_data.columns.tolist(), barmode="stack", title="Funding Fee theo Coin và Vị thế")
                    st.plotly_chart(fig, use_container_width=True)

                    chart_path = "funding_fee_chart_web.png"
                    fig.write_image(chart_path)

                    excel_path = "funding_fee_report_web.xlsx"
                    final_df.to_excel(excel_path, index=False)

                    st.download_button("📥 Tải báo cáo Excel", data=open(excel_path, "rb").read(), file_name=excel_path)

                    try:
                        body = f"Kết quả funding fee từ {start_date} đến {end_date}\n\n" + summary_df.to_string(index=False)
                        send_email_report(email_sender, email_pass, email_receiver, "Funding Fee Report", body, excel_path)
                        st.success(f"📧 Báo cáo đã gửi tới {email_receiver}")
                    except Exception as e:
                        st.error(f"Lỗi khi gửi email: {e}")
                else:
                    st.warning("Không có dữ liệu funding trong khoảng thời gian đã chọn.")
