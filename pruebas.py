import requests
import os
import numpy as np
import pandas as pd
import streamlit as st
from  streamlit_lottie import  st_lottie
from streamlit_option_menu import option_menu
from  PIL import  Image as Pillow
import plotly.express as px


import pandas as pd
import streamlit as st

data_df = pd.DataFrame(
    {
        "widgets": ["st.selectbox", "st.number_input", "st.text_area", "st.button"],
        "favorite": [True, False, False, True],
    }
)

print(data_df)

st.data_editor(
    data_df,
    column_config={
        "Status": st.column_config.CheckboxColumn(
            "Your favorite?",
            help="Select **statu`s** order",
            default=False,
        )
    },
    disabled=["widgets"],
    hide_index=True,
)