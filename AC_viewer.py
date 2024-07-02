from io import BytesIO
from pathlib import Path
from tempfile import NamedTemporaryFile
import zipfile

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from reader import datconv as dv

def plot_ac_inst(ac_inst):
    xx = ac_inst.df["uvEnergy"].values
    yy = ac_inst.df["pyield"].values 
    yn = ac_inst.df["npyield"].values 
    fig, ax = plt.subplots()
    fig.set_figheight(3)
    fig.set_figwidth(4)
    ax.set_title(f'{ac_inst.metadata["sampleName"]}')
    ax.plot(xx,yn,'ro-',label='Data')
    ax.plot(xx,ac_inst.df["guideline"],'g-',label=f'Estimate\n {ac_inst.metadata["thresholdEnergy"]:.2f} eV')
    ax.legend()
    ax.grid()
    ax.set_xlabel('Energy [eV]')
    ax.set_ylabel(f'$Intensity^{{{ac_inst.metadata["powerNumber"]:.2f}}}$')
 
    return fig

def main():
    st.title("AC dat file Viewer")
    
    download_zip_file = st.empty()

    uploaded_files = st.file_uploader("dat file upload", accept_multiple_files=True, type=["dat"])

    figures = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            with NamedTemporaryFile(delete=False) as f:
                fp = Path(f.name)
                fp.write_bytes(uploaded_file.getvalue())
                
                acdata = dv.AcConv(f'{f.name}')
                acdata.convert()

            fp.unlink()
            
            fig = plot_ac_inst(acdata)
            st.pyplot(fig)
            figures.append((fig, uploaded_file.name))

        def create_zip():
            in_memory = BytesIO()
            with zipfile.ZipFile(in_memory, 'w', zipfile.ZIP_DEFLATED) as zf:
                for fig, name in figures:
                    img_bytes = BytesIO()
                    fig.savefig(img_bytes, format='png')
                    img_bytes.seek(0)
                    zf.writestr(f"{Path(name).stem}.png", img_bytes.read())
            in_memory.seek(0)
            return in_memory

        zip_buffer = create_zip()
        download_zip_file.download_button(
            label="Download (zip)",
            data=zip_buffer,
            file_name='graphs.zip',
            mime='application/zip'
        )


if __name__ == "__main__":
    main()
    
    # streamlit run .\AC_viewer.py
