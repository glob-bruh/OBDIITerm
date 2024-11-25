
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

print(f"""
TEST VIN: JN3MS37A9PW202929
""")

def guiConfigConnect():
    st.write("## ConfigConnect")

def guiMonTools():
    st.write("## MonTools")

def guiCommander():
    st.write("## Commander")
    st.markdown("""
    <center id='warning'>
    <p><b><u>WARNING:</u></b><p>
    <p><b>Commands entered here can inflict damage to your vehicle. As stated by the included license, you assume all liability for any damage incurred.</b></p>
    </center>
    <style> #warning {color: red;} </style>
    """, unsafe_allow_html=True)

    if "areaText" not in st.session_state:
        st.session_state.areaText = ""

    if "CommandToRun" in st.session_state:
        if len(st.session_state.CommandToRun) == 27:
            st.session_state.areaText += f"--> SEND CMD: {st.session_state.CommandToRun}\n"
            result = gDiags.sendCANmsg(st.session_state.CommandToRun)
            if result == False:
                st.session_state.areaText += f"!!! FAILED TO TRANSMIT\n!!! Have you setup CAN with ConfigConnect?\n"
                # obd2_Base doesnt return a FAILURE! Likely caused by a try/except. FIX THIS!
            #result = gDiags.readCANmsg(True, st.session_state.arbIDrecv, False)
        else:
            st.session_state.areaText += f"??? CMD {st.session_state.CommandToRun} is not a valid command! Not executing.\n"
        del st.session_state.CommandToRun

    x1,txt1,x2,x3,x4,x5,x6,x7,x8,x9 = st.columns(10)
    with x1: arbID = st.text_input("CMD:", key="arbID", max_chars=3, placeholder="7DF")
    with txt1: st.text_input("", key="x", max_chars=1, value="#", disabled=True)
    with x2: val1 = st.text_input("", key="val1", max_chars=2, placeholder="02")
    with x3: val2 = st.text_input("", key="val2", max_chars=2, placeholder="01")
    with x4: val3 = st.text_input("", key="val3", max_chars=2, placeholder="0C")
    with x5: val4 = st.text_input("", key="val4", max_chars=2, placeholder="00")
    with x6: val5 = st.text_input("", key="val5", max_chars=2, placeholder="00")
    with x7: val6 = st.text_input("", key="val6", max_chars=2, placeholder="00")
    with x8: val7 = st.text_input("", key="val7", max_chars=2, placeholder="00")
    with x9: val8 = st.text_input("", key="val8", max_chars=2, placeholder="00")
    respID = st.text_input("Response ID to listen for:", key="respID", max_chars=3, placeholder="7E8")

    st.button("Execute Command", on_click=lambda:st.session_state.__setitem__("CommandToRun", str(
        arbID + "#" + 
        val1 + " " + val2 + " " + val3 + " " +
        val4 + " " + val5 + " " + val6 + " " +
        val7 + " " + val8
    ).strip()))

    st.text_area("Output Log:", disabled=True, value=st.session_state.areaText)
    

def guiVinProfiler():
    st.write("## VIN Profiler")
    submitVin = st.text_input("Vehicle VIN:", key="vin")

    if "subVinNum" in st.session_state and st.session_state.lookupType == "offline":
        try:
            vin = st.session_state.subVinNum
            offCarYear = gDiags.vinYearDecode(vin)
            st.write(f"""
            * Vehicle Year: {str(offCarYear[0])} or {str(offCarYear[1])}.
            * Check Digit Pass: {str(gDiags.vinCheckDigitCheck(vin))}.
            * Serial Number: {"".join(list(vin)[11:17])}.
            """)
        except:
            st.write(f"""
            **VIN DECODE FAILURE!**\n
            Is the VIN you submitted proper?
            """)

    if "subVinNum" in st.session_state and st.session_state.lookupType == "online":
        try:
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
        except:
            st.write(f"""
            **VIN DECODE FAILURE!**\n
            Is the VIN you submitted proper?
            Are you connected to the internet?
            """)

    x1,x2 = st.columns(2)
    with x1: st.button("Offline Lookup", on_click=lambda:st.session_state.__setitem__("lookupType", "offline"))
    with x2: st.button("Online Lookup (via NHTSA)", on_click=lambda:st.session_state.__setitem__("lookupType", "online"))
    
    if submitVin != "":
        st.session_state.subVinNum = submitVin

st.markdown("""
<center>
<h1>OBD-II LIBRARY</h1>
<h3>Developed By <a href='https://glob-bruh.github.io/'>GlobBruh</a> &bull; Powered by <a href='https://streamlit.io/'>Streamlit</a></h3>
</center>
""", unsafe_allow_html=True)
st.image("logo.png", width=250)
x1,x2,x3,x4 = st.columns(4)
with x1: st.button("ConfigConnect", on_click=lambda:st.session_state.__setitem__("mode", "configconnect"))
with x2: st.button("MonTools", on_click=lambda:st.session_state.__setitem__("mode", "montools"))
with x3: st.button("Commander", on_click=lambda:st.session_state.__setitem__("mode", "commander"))
with x4: st.button("VIN Profiler", on_click=lambda:st.session_state.__setitem__("mode", "vin"))
st.markdown("---")

if "mode" in st.session_state:
    match st.session_state.mode:
        case "configconnect": guiConfigConnect()
        case "montools": guiMonTools()
        case "commander": guiCommander()
        case "vin": guiVinProfiler()
else:
    st.write("**Please select a mode from the buttons above.**")
