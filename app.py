import streamlit as st
import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Blockchain Wallet Intelligence",
    page_icon="🔗",
    layout="wide"
)

# =========================================================
# HEADER
# =========================================================

st.title("🔗 Blockchain Wallet Intelligence Platform")

st.write(
    "Analyze public Ethereum wallet activity, "
    "transaction patterns and basic security indicators."
)

st.info(
    "🔐 Safety: Enter only a PUBLIC wallet address. "
    "Never enter a private key, seed phrase or password."
)

# =========================================================
# INPUT
# =========================================================

wallet_address = st.text_input(
    "Enter Public Ethereum Wallet Address",
    placeholder="0x..."
)

analyze_button = st.button(
    "🔍 Analyze Wallet",
    use_container_width=True
)

# =========================================================
# ANALYSIS
# =========================================================

if analyze_button:

    if not wallet_address:

        st.warning(
            "Please enter a public Ethereum wallet address."
        )

    elif not wallet_address.startswith("0x"):

        st.error(
            "Invalid address. Ethereum addresses start with 0x."
        )

    elif len(wallet_address) != 42:

        st.error(
            "Invalid Ethereum wallet address length."
        )

    else:

        try:

            API_BASE = "https://eth.blockscout.com/api/v2"

            # =================================================
            # WALLET INFORMATION
            # =================================================

            address_url = (
                f"{API_BASE}/addresses/{wallet_address}"
            )

            address_response = requests.get(
                address_url,
                timeout=15
            )

            if address_response.status_code != 200:

                st.error(
                    "Wallet could not be found. "
                    "Please check the address."
                )

            else:

                wallet_data = address_response.json()

                st.success(
                    "✅ Wallet found successfully!"
                )

                # =================================================
                # WALLET TYPE
                # =================================================

                wallet_type = wallet_data.get(
                    "type",
                    "Unknown"
                )

                if str(wallet_type).lower() == "contract":

                    wallet_type_display = "Smart Contract"

                else:

                    wallet_type_display = "Regular Wallet / EOA"

                # =================================================
                # BALANCE
                # =================================================

                balance_wei = int(
                    wallet_data.get(
                        "coin_balance"
                    ) or 0
                )

                balance_eth = balance_wei / 10**18

                # =================================================
                # TRANSACTIONS
                # =================================================

                tx_url = (
                    f"{API_BASE}/addresses/"
                    f"{wallet_address}/transactions"
                )

                tx_response = requests.get(
                    tx_url,
                    timeout=15
                )

                if tx_response.status_code != 200:

                    st.error(
                        "Unable to retrieve transaction data."
                    )

                else:

                    tx_data = tx_response.json()

                    transactions = tx_data.get(
                        "items",
                        []
                    )

                    # =================================================
                    # TRANSACTION ANALYSIS
                    # =================================================

                    incoming_count = 0
                    outgoing_count = 0

                    transaction_rows = []

                    for tx in transactions:

                        from_data = tx.get(
                            "from",
                            {}
                        )

                        to_data = tx.get(
                            "to",
                            {}
                        )

                        from_address = str(
                            from_data.get(
                                "hash",
                                ""
                            )
                        )

                        to_address = str(
                            to_data.get(
                                "hash",
                                ""
                            )
                        )

                        tx_hash = tx.get(
                            "hash",
                            "Unknown"
                        )

                        method = tx.get(
                            "method",
                            "Transfer"
                        )

                        # Direction

                        if (
                            to_address.lower()
                            == wallet_address.lower()
                        ):

                            incoming_count += 1
                            direction = "Incoming"

                        elif (
                            from_address.lower()
                            == wallet_address.lower()
                        ):

                            outgoing_count += 1
                            direction = "Outgoing"

                        else:

                            direction = "Other"

                        # Transaction value

                        raw_value = tx.get(
                            "value",
                            "0"
                        )

                        try:

                            value_wei = int(
                                raw_value or 0
                            )

                            value_eth = (
                                value_wei / 10**18
                            )

                        except:

                            value_eth = 0.0

                        transaction_rows.append(
                            {
                                "Transaction Hash":
                                    tx_hash,

                                "Direction":
                                    direction,

                                "Method":
                                    method,

                                "Value ETH":
                                    value_eth
                            }
                        )

                    # =================================================
                    # ACTIVITY
                    # =================================================

                    total_activity = (
                        incoming_count
                        + outgoing_count
                    )

                    if total_activity == 0:

                        activity_level = "Low"

                    elif total_activity < 5:

                        activity_level = "Low"

                    elif total_activity < 20:

                        activity_level = "Medium"

                    else:

                        activity_level = "High"

                    # =================================================
                    # WALLET OVERVIEW
                    # =================================================

                    st.subheader(
                        "📊 Wallet Overview"
                    )

                    col1, col2, col3, col4 = st.columns(4)

                    with col1:

                        st.metric(
                            "💰 Balance",
                            f"{balance_eth:.6f} ETH"
                        )

                    with col2:

                        st.metric(
                            "🔗 Transactions",
                            total_activity
                        )

                    with col3:

                        st.metric(
                            "📥 Incoming",
                            incoming_count
                        )

                    with col4:

                        st.metric(
                            "📤 Outgoing",
                            outgoing_count
                        )

                    # =================================================
                    # WALLET INFORMATION
                    # =================================================

                    st.subheader(
                        "👛 Wallet Information"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.write(
                            f"**Wallet Type:** "
                            f"{wallet_type_display}"
                        )

                    with col2:

                        st.write(
                            f"**Activity Level:** "
                            f"{activity_level}"
                        )

                    # =================================================
                    # ACTIVITY STATUS
                    # =================================================

                    st.subheader(
                        "⚡ Activity Status"
                    )

                    if activity_level == "Low":

                        st.success(
                            "🟢 Low wallet activity"
                        )

                    elif activity_level == "Medium":

                        st.warning(
                            "🟡 Medium wallet activity"
                        )

                    else:

                        st.error(
                            "🔴 High wallet activity"
                        )

                    # =================================================
                    # AUTOMATED SUMMARY
                    # =================================================

                    st.subheader(
                        "🤖 Wallet Activity Summary"
                    )

                    if total_activity == 0:

                        summary = (
                            "This wallet shows very low "
                            "recent activity based on the "
                            "transactions analyzed."
                        )

                    elif incoming_count > outgoing_count:

                        summary = (
                            f"This wallet shows "
                            f"{activity_level.lower()} activity. "
                            f"It has more incoming transactions "
                            f"({incoming_count}) than outgoing "
                            f"transactions ({outgoing_count}). "
                            f"The analyzed activity is more "
                            f"receive-oriented."
                        )

                    elif outgoing_count > incoming_count:

                        summary = (
                            f"This wallet shows "
                            f"{activity_level.lower()} activity. "
                            f"It has more outgoing transactions "
                            f"({outgoing_count}) than incoming "
                            f"transactions ({incoming_count}). "
                            f"The analyzed activity is more "
                            f"send-oriented."
                        )

                    else:

                        summary = (
                            f"This wallet shows "
                            f"{activity_level.lower()} activity. "
                            f"Incoming and outgoing activity "
                            f"are currently balanced."
                        )

                    st.info(summary)

                    # =================================================
                    # TRANSACTION CHART
                    # =================================================

                    st.subheader(
                        "📈 Transaction Direction"
                    )

                    chart_data = pd.DataFrame(
                        {
                            "Type": [
                                "Incoming",
                                "Outgoing"
                            ],

                            "Transactions": [
                                incoming_count,
                                outgoing_count
                            ]
                        }
                    )

                    st.bar_chart(
                        chart_data.set_index(
                            "Type"
                        )
                    )

                    # =================================================
                    # ML ANOMALY DETECTION
                    # =================================================

                    st.subheader(
                        "🤖 ML-Based Anomaly Detection"
                    )

                    anomaly_count = 0
                    normal_count = 0

                    if len(transaction_rows) >= 5:

                        ml_df = pd.DataFrame(
                            transaction_rows
                        )

                        ml_df["Direction_Code"] = (
                            ml_df["Direction"]
                            .map(
                                {
                                    "Incoming": 1,
                                    "Outgoing": -1,
                                    "Other": 0
                                }
                            )
                            .fillna(0)
                        )

                        ml_df["Value ETH"] = pd.to_numeric(
                            ml_df["Value ETH"],
                            errors="coerce"
                        ).fillna(0)

                        ml_df["Value_Log"] = np.log1p(
                            ml_df["Value ETH"]
                        )

                        features = ml_df[
                            [
                                "Direction_Code",
                                "Value_Log"
                            ]
                        ]

                        model = IsolationForest(
                            contamination="auto",
                            random_state=42
                        )

                        predictions = model.fit_predict(
                            features
                        )

                        ml_df["ML Result"] = np.where(
                            predictions == -1,
                            "⚠️ Anomaly",
                            "Normal"
                        )

                        anomaly_count = int(
                            (predictions == -1).sum()
                        )

                        normal_count = int(
                            (predictions == 1).sum()
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            st.metric(
                                "Normal Transactions",
                                normal_count
                            )

                        with col2:

                            st.metric(
                                "Potential Anomalies",
                                anomaly_count
                            )

                        if anomaly_count > 0:

                            st.warning(
                                f"⚠️ ML detected "
                                f"{anomaly_count} potentially "
                                f"unusual transaction pattern(s)."
                            )

                        else:

                            st.success(
                                "🟢 No unusual transaction "
                                "patterns detected."
                            )

                        st.dataframe(
                            ml_df[
                                [
                                    "Transaction Hash",
                                    "Direction",
                                    "Value ETH",
                                    "ML Result"
                                ]
                            ],
                            use_container_width=True
                        )

                    else:

                        st.info(
                            "At least 5 transactions are "
                            "needed for ML anomaly analysis."
                        )

                    # =================================================
                    # SECURITY / RISK SCORE
                    # =================================================

                    st.subheader(
                        "🛡️ Basic Security Analysis"
                    )

                    risk_score = 0
                    risk_reasons = []

                    if total_activity >= 20:

                        risk_score += 40

                        risk_reasons.append(
                            "High transaction frequency."
                        )

                    elif total_activity >= 10:

                        risk_score += 20

                        risk_reasons.append(
                            "Moderate transaction frequency."
                        )

                    if (
                        incoming_count > 0
                        and outgoing_count > 0
                    ):

                        difference = abs(
                            incoming_count
                            - outgoing_count
                        )

                        if difference >= 10:

                            risk_score += 20

                            risk_reasons.append(
                                "Large difference between "
                                "incoming and outgoing activity."
                            )

                    if wallet_type_display == "Smart Contract":

                        risk_score += 10

                        risk_reasons.append(
                            "Address is identified as "
                            "a smart contract."
                        )

                    if anomaly_count > 0:

                        risk_score += min(
                            anomaly_count * 5,
                            30
                        )

                        risk_reasons.append(
                            "ML detected potentially "
                            "unusual transaction patterns."
                        )

                    risk_score = min(
                        risk_score,
                        100
                    )

                    if risk_score >= 60:

                        risk_level = "HIGH 🔴"

                    elif risk_score >= 30:

                        risk_level = "MEDIUM 🟡"

                    else:

                        risk_level = "LOW 🟢"

                    col1, col2 = st.columns(2)

                    with col1:

                        st.metric(
                            "Risk Score",
                            f"{risk_score}/100"
                        )

                    with col2:

                        st.metric(
                            "Risk Level",
                            risk_level
                        )

                    if risk_reasons:

                        st.write(
                            "**Detected Indicators:**"
                        )

                        for reason in risk_reasons:

                            st.write(
                                f"• {reason}"
                            )

                    else:

                        st.success(
                            "No unusual indicators detected "
                            "by the current rules."
                        )

                    st.caption(
                        "⚠️ Risk score and ML results are "
                        "experimental indicators only. "
                        "They do not prove that a wallet is "
                        "safe, malicious, or involved in fraud."
                    )

                    # =================================================
                    # RECENT TRANSACTIONS
                    # =================================================

                    st.subheader(
                        "🧾 Recent Transactions"
                    )

                    if transaction_rows:

                        recent_df = pd.DataFrame(
                            transaction_rows[:10]
                        )

                        st.dataframe(
                            recent_df,
                            use_container_width=True
                        )

                    else:

                        st.info(
                            "No recent transactions found."
                        )

                    # =================================================
                    # WALLET DETAILS
                    # =================================================

                    st.subheader(
                        "🔎 Wallet Details"
                    )

                    st.code(
                        wallet_address
                    )

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.write(
                            f"**Type:** "
                            f"{wallet_type_display}"
                        )

                    with col2:

                        st.write(
                            f"**Balance:** "
                            f"{balance_eth:.6f} ETH"
                        )

                    with col3:

                        st.write(
                            f"**Transactions Analyzed:** "
                            f"{len(transactions)}"
                        )

                    # =================================================
                    # DOWNLOAD SECURITY REPORT
                    # =================================================

                    st.subheader(
                        "📄 Security Report"
                    )

                    report = f"""
BLOCKCHAIN WALLET SECURITY REPORT
=================================

Wallet Address:
{wallet_address}

Wallet Type:
{wallet_type_display}

Balance:
{balance_eth:.6f} ETH

Transactions Analyzed:
{len(transactions)}

Incoming Transactions:
{incoming_count}

Outgoing Transactions:
{outgoing_count}

Activity Level:
{activity_level}

ML Normal Transactions:
{normal_count}

ML Potential Anomalies:
{anomaly_count}

Risk Score:
{risk_score}/100

Risk Level:
{risk_level}

Automated Summary:
{summary}

Security Indicators:
"""

                    if risk_reasons:

                        for reason in risk_reasons:

                            report += (
                                f"- {reason}\n"
                            )

                    else:

                        report += (
                            "- No unusual indicators "
                            "detected by current rules.\n"
                        )

                    report += """

DISCLAIMER
----------
This report is an educational prototype.
The risk score and ML anomaly detection are
experimental indicators based on public blockchain
transaction data. They do not prove that an address
is safe, malicious, fraudulent, or criminal.

Never enter a private key, seed phrase, or password
into this application.
"""

                    st.download_button(
                        label="⬇️ Download Security Report",
                        data=report,
                        file_name="wallet_security_report.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

        except requests.RequestException:

            st.error(
                "Unable to connect to the blockchain "
                "explorer. Check your internet connection."
            )

        except Exception as error:

            st.error(
                "Something went wrong while analyzing "
                "the wallet."
            )

            st.caption(
                f"Technical detail: {error}"
            )

# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Blockchain Wallet Intelligence Platform | "
    "Educational Cybersecurity Project"
)