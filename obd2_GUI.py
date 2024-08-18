
#################################################
# 
# ON-BOARD DIAGNOSTICS LIBRARY
# 
# (C) GlobBruh
# https://glob-bruh.github.io/
# 
# https://github.com/glob-bruh/OBDIITerm
# 
#################################################

import obd2_Base as gDiags
import streamlit as st

def onlineClicked():
    st.session_state.lookupType = "online"

def offlineClicked():
    st.session_state.lookupType = "offline"

print(f"""
TEST VIN: JN3MS37A9PW202929
""")

st.write("""
# OBD-II TERMINAL
### Developed By GlobBruh - Powered by Streamlit
""")
st.image("logo.png", width=250)
submitVin = st.text_input("Vehicle VIN:", key="vin")

if "subVinNum" in st.session_state and st.session_state.lookupType == "offline":
    vin = st.session_state.subVinNum
    offCarYear = gDiags.vinYearDecode(vin)
    st.write(f"""
    * Vehicle Year: {str(offCarYear[0])} or {str(offCarYear[1])}.
    * Check Digit Pass: {str(gDiags.vinCheckDigitCheck(vin))}.
    * Serial Number: {"".join(list(vin)[11:17])}.
    """)

if "subVinNum" in st.session_state and st.session_state.lookupType == "online":
    out = gDiags.vinNHTSAGetInfo(st.session_state.subVinNum)
    st.write(f"""
    * Manufacture: {gDiags.vinNHTSAFind("Manufacturer Name", out)}.
    * Model: {gDiags.vinNHTSAFind("Make", out)} {gDiags.vinNHTSAFind("Model", out)}.
    * Check digit passed? {gDiags.vinNHTSAFind("Error Text", out)}.
    * Year: {gDiags.vinNHTSAFind("Model Year", out)}.
    * Plant: {gDiags.vinNHTSAFind("Plant Company Name", out)} > {gDiags.vinNHTSAFind("Plant City", out)} > {gDiags.vinNHTSAFind("Plant State", out)} > {gDiags.vinNHTSAFind("Plant Country", out)}.
    * Engine Model: {gDiags.vinNHTSAFind("Engine Model", out)}.
    * Primary Fuel Type: {gDiags.vinNHTSAFind("Fuel Type - Primary", out)}.
    * Turbo: {gDiags.vinNHTSAFind("Turbo", out)}.
    * Body Class: {gDiags.vinNHTSAFind("Body Class", out)}.
    * Door Count: {gDiags.vinNHTSAFind("Doors", out)}.
    """)

st.button("Offline Lookup", on_click=offlineClicked)
st.button("Online Lookup", on_click=onlineClicked)

if submitVin != "":
    st.session_state.subVinNum = submitVin